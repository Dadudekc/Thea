#!/usr/bin/env python3
"""
AI-Driven Conversation Analyzer
===============================

Opens each ChatGPT thread without a stored summary, sends the Jinja
`templates/prompts/conversation_analyzer.j2` prompt, captures the
assistant's reply, and stores it back into the `conversations` table
(`summary` + optional `tags`).

Designed to run after the nightly scraping pipeline so newly ingested
threads gain structured insights automatically.

CLI usage::

    python scripts/analyze_conversations_ai.py --headless --limit 50
"""
from __future__ import annotations

import sys
import time
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any

# Repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Existing modules
from core.memory_manager import MemoryManager
from core.template_engine import render_template
from scrapers.browser_manager import BrowserManager
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor
from scrapers.conversation_list_manager import ConversationListManager

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("conversation_analyzer")

TEMPLATE_PATH = "prompts/conversation_analyzer.j2"

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def extract_tags(summary_text: str) -> str:
    """Very naive tag extractor – looks for a bullet list labelled Tags."""
    tag_match = re.search(r"Tags\s*[:\-]\s*(.+)", summary_text, re.IGNORECASE)
    if tag_match:
        tags = [t.strip() for t in re.split(r",|;|\|", tag_match.group(1)) if t.strip()]
        return ",".join(tags)
    return ""

# ---------------------------------------------------------------------------
# Analyzer class
# ---------------------------------------------------------------------------

class ConversationAnalyzer:
    def __init__(self, *, headless: bool = False):
        self.browser_manager = BrowserManager(headless=headless, use_undetected=True)
        self.cookie_manager = CookieManager("data/chatgpt_cookies.pkl")
        self.login_handler = LoginHandler()
        self.extractor = ConversationExtractor()
        self.driver = None

    # ---------------------------- public -----------------------------------
    def run(self, limit: Optional[int] = None):
        with MemoryManager("dreamos_memory.db") as memory:
            to_process = self._fetch_unanalysed_conversations(memory, limit)
            if not to_process:
                logger.info("Nothing to analyse – DB already up-to-date ✅")
                return

            logger.info("Need to analyse %d conversations", len(to_process))

            self.driver = self.browser_manager.create_driver()
            self._ensure_logged_in()

            for idx, conv in enumerate(to_process, 1):
                cid = conv["id"]
                logger.info("(%d/%d) Analysing %s – %s", idx, len(to_process), cid, conv["title"])
                try:
                    if not self.extractor.enter_conversation(self.driver, conv["url"]):
                        logger.warning("Could not open conversation %s – skipping", cid)
                        continue

                    prompt = self._build_prompt(conv["content"])
                    if not self.extractor.send_prompt(self.driver, prompt, wait_for_response=True):
                        logger.warning("Prompt failed for %s", cid)
                        continue

                    # Retrieve updated messages and capture last assistant reply
                    data = self.extractor.get_conversation_content(self.driver)
                    messages = data.get("messages", [])
                    if not messages:
                        logger.warning("No messages fetched after prompt – skipping")
                        continue

                    last = messages[-1]
                    if last.get("role") != "assistant":
                        logger.warning("Last message not from assistant – skipping")
                        continue

                    summary_txt = last.get("content", "").strip()
                    tags = extract_tags(summary_txt)

                    self._store_summary(memory, cid, summary_txt, tags)
                    logger.info("Stored summary for %s (%d chars)", cid, len(summary_txt))

                    # polite delay
                    time.sleep(1.5)
                except Exception as e:
                    logger.error("Error analysing %s: %s", cid, e, exc_info=True)
                    continue
            logger.info("Conversation analysis complete ✅")
        # Close browser
        if self.driver:
            self.browser_manager.close_driver()

    # ---------------------------- internals --------------------------------
    def _ensure_logged_in(self):
        logger.info("Navigating to ChatGPT …")
        self.driver.get("https://chat.openai.com/")
        time.sleep(3)

        if self.cookie_manager.cookie_file_exists():
            self.cookie_manager.load_cookies(self.driver)
            self.driver.refresh()
            time.sleep(2)

        if self.login_handler.is_logged_in(self.driver):
            logger.info("Logged-in via cookies ✅")
            return

        if not self.login_handler.ensure_login_modern(self.driver, allow_manual=True, manual_timeout=180):
            raise RuntimeError("Cannot login – aborting analysis")
        self.cookie_manager.save_cookies(self.driver)

    def _build_prompt(self, conversation_content: str) -> str:
        # Trim to ~4000 chars to avoid token blow-up
        if len(conversation_content) > 4000:
            conversation_content = conversation_content[:4000] + "\n… (truncated) …"
        return render_template(TEMPLATE_PATH, {"conversation_content": conversation_content})

    def _fetch_unanalysed_conversations(self, memory: MemoryManager, limit: Optional[int]):
        cursor = memory.storage.conn.cursor()
        q = "SELECT id, title, url, content FROM conversations WHERE (summary IS NULL OR summary = '') ORDER BY timestamp DESC"
        if limit:
            q += " LIMIT ?"
            cursor.execute(q, (limit,))
        else:
            cursor.execute(q)
        return [dict(r) for r in cursor.fetchall()]

    def _store_summary(self, memory: MemoryManager, convo_id: str, summary: str, tags: str):
        cursor = memory.storage.conn.cursor()
        cursor.execute(
            """
            UPDATE conversations
            SET summary = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (summary, tags, convo_id)
        )
        memory.storage.conn.commit()

# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Run AI analysis on conversations without summaries")
    p.add_argument("--headless", action="store_true", help="Run Chrome headless")
    p.add_argument("--limit", type=int, default=None, help="Max conversations to analyse")
    args = p.parse_args()

    analyzer = ConversationAnalyzer(headless=args.headless)
    analyzer.run(limit=args.limit) 