#!/usr/bin/env python3
"""
Complete Conversation Scraper
=============================

Scrapes *every* ChatGPT conversation visible in the sidebar using the existing
undetected-Chromedriver based components and stores **one JSON ﬁle per thread**
inside `data/conversations/`.

Each JSON file has the structure expected by `core.memory_manager.ingest_conversations`:
{
  "id": "<conversation id>",
  "title": "<title>",
  "timestamp": "<iso datetime scrape finished>",
  "url": "https://chat.openai.com/c/<id>",
  "messages": [ {"role": "user|assistant", "content": "…"}, … ],
  "message_count": <int>,
  "model": "GPT-4o" | "GPT-3.5" | "Unknown"
}

If the file already exists it is skipped unless `--overwrite` is supplied.

CLI Usage
---------
$ python scripts/complete_conversation_scraper.py --headless --max 500

Options
-------
--headless           Run Chrome in headless mode.
--max N              Stop after scraping N conversations (handy for testing).
--overwrite          Re-download and overwrite existing JSON ﬁles.
--raw-html           Also dump the raw HTML of each thread next to the JSON.

Environment variables recognised by the underlying LoginHandler:
  CHATGPT_USERNAME, CHATGPT_PASSWORD, CHATGPT_TOTP_SECRET

Notes
-----
• Relies entirely on the existing scraper modules – no new web-scraping logic.
• Uses the CookieManager first; falls back to LoginHandler.ensure_login_modern,
  which will prompt for manual login if credentials are missing.
• Designed to be idempotent; can be scheduled nightly.
"""

from __future__ import annotations

import sys
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add repo root for imports when executed directly
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Existing components
from scrapers.browser_manager import BrowserManager
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_list_manager import ConversationListManager
from scrapers.conversation_extractor import ConversationExtractor

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("conversation_scraper")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def save_json_atomic(data: Dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    """Write *data* to *path* using a tmp file then rename for atomicity."""
    if path.exists() and not overwrite:
        logger.debug("File %s exists – skipping (use --overwrite to replace)", path.name)
        return

    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    tmp.replace(path)

# ---------------------------------------------------------------------------
# Main scraper class
# ---------------------------------------------------------------------------

class ConversationHistoryScraper:
    """Facade around existing scraper pieces to dump full conversation JSONs."""

    def __init__(self, *, headless: bool = False, max_threads: Optional[int] = None,
                 overwrite: bool = False, dump_raw_html: bool = False):
        self.headless = headless
        self.max_threads = max_threads
        self.overwrite = overwrite
        self.dump_raw_html = dump_raw_html

        self.browser_manager = BrowserManager(headless=headless, use_undetected=True)
        self.cookie_manager = CookieManager("data/chatgpt_cookies.pkl")
        self.login_handler = LoginHandler()
        self.list_manager = ConversationListManager()
        self.extractor = ConversationExtractor()

        self.driver = None
        self.out_dir = REPO_ROOT / "data" / "conversations"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------- public -------------
    def run(self) -> None:
        try:
            self.driver = self.browser_manager.create_driver()
            self._navigate_and_login()
            conversations = self.list_manager.get_conversation_list(self.driver)
            if not conversations:
                logger.error("No conversations discovered – aborting")
                return

            if self.max_threads:
                conversations = conversations[: self.max_threads]

            logger.info("Starting extraction of %d threads", len(conversations))
            for idx, conv in enumerate(conversations, 1):
                cid = conv.get("id") or f"idx_{idx}"
                fname = f"{cid}.json"
                fpath = self.out_dir / fname

                if fpath.exists() and not self.overwrite:
                    logger.info("(%d/%d) %s exists – skipping", idx, len(conversations), fname)
                    continue

                logger.info("(%d/%d) Scraping %s – %s", idx, len(conversations), cid, conv.get("title"))
                if not self.extractor.enter_conversation(self.driver, conv["url"]):
                    logger.warning("Could not open conversation %s – skipping", cid)
                    continue

                convo_data = self.extractor.get_conversation_content(self.driver)
                convo_data.setdefault("id", cid)
                convo_data.setdefault("url", conv["url"])
                # Enrich with scrape timestamp
                convo_data["captured_at"] = datetime.utcnow().isoformat()

                save_json_atomic(convo_data, fpath, overwrite=self.overwrite)
                logger.info("Saved %s (%d messages)", fpath.name, convo_data.get("message_count", 0))

                # Optional: raw HTML dump (useful for debugging selector breakage)
                if self.dump_raw_html:
                    html_path = fpath.with_suffix(".html")
                    html_path.write_text(self.driver.page_source, encoding="utf-8")

                # Friendly delay to reduce server load & detection
                time.sleep(1.2)

            logger.info("🎉 Finished scraping %d conversations", len(conversations))
        finally:
            if self.driver:
                self.browser_manager.close_driver()

    # -------------------------------------------------- internals ----------
    def _navigate_and_login(self):
        logger.info("Loading chat.openai.com …")
        self.driver.get("https://chat.openai.com/")
        time.sleep(3)

        # Load cookies if available and refresh
        if self.cookie_manager.cookie_file_exists():
            logger.info("Injecting saved cookies …")
            self.cookie_manager.load_cookies(self.driver)
            self.driver.refresh()
            time.sleep(2)

        if self.login_handler.is_logged_in(self.driver):
            logger.info("Already logged in via cookies ✅")
            return

        logger.info("Not logged in – attempting credential / manual login …")
        if not self.login_handler.ensure_login_modern(self.driver, allow_manual=True, manual_timeout=180):
            raise RuntimeError("Login failed – cannot proceed with scraping")

        logger.info("Login successful – saving fresh cookies")
        self.cookie_manager.save_cookies(self.driver)

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape full ChatGPT conversation history")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    parser.add_argument("--max", type=int, default=None, help="Max number of threads to scrape (for testing)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing JSON files")
    parser.add_argument("--raw-html", action="store_true", help="Also dump raw HTML per conversation")

    args = parser.parse_args()

    scraper = ConversationHistoryScraper(
        headless=args.headless,
        max_threads=args.max,
        overwrite=args.overwrite,
        dump_raw_html=args.raw_html,
    )
    scraper.run() 