#!/usr/bin/env python3
"""
full_historical_scrape.py
owner: scraper  |  purpose: End-to-end scrape, ingest and dreamscape process of all historical ChatGPT conversations in one shot.  |  created: 2025-06-25

Usage example:
    python scripts/full_historical_scrape.py \
        --max_conversations 1300 \
        --cookies_file data/chatgpt_cookies.pkl \
        --output_json outputs/all_convos_2025-06-25.json \
        --run_dreamscape

The script reuses existing Dream.OS infrastructure — ScraperOrchestrator,
MemoryManager, DreamscapeProcessor and ConversationStatsUpdater — without
introducing duplicate logic. It skips conversations already present in the DB
(id match), maintains dev-log entry and ensures cookie-first login flow.
"""

from __future__ import annotations
# EDIT START: ensure project root is on PYTHONPATH for standalone execution
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# EDIT END

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from core.scraper_orchestrator import ScraperOrchestrator
from core.memory_manager import MemoryManager
from core.dreamscape_processor import DreamscapeProcessor
from core.conversation_stats_updater import ConversationStatsUpdater

logger = logging.getLogger("full_historical_scrape")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def parse_args() -> argparse.Namespace:
    """CLI argument parsing."""
    today_str = datetime.now().date().isoformat()
    parser = argparse.ArgumentParser(
        description="Scrape ChatGPT history, ingest into Dream.OS memory, run Dreamscape processing and refresh stats.",
    )
    parser.add_argument("--max_conversations", type=int, default=1300, help="Maximum number of conversations to fetch.")
    parser.add_argument("--cookies_file", type=str, default="data/chatgpt_cookies.pkl", help="Path to saved cookie pickle.")
    parser.add_argument(
        "--output_json",
        type=str,
        default=f"outputs/all_convos_{today_str}.json",
        help="Destination JSON listing scraped conversation files.",
    )
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (stealth mode)")
    parser.add_argument("--no_env_login", action="store_true", help="Disable auto-login via environment credentials")
    parser.add_argument("--wait_secs", type=int, default=120, help="Max seconds to wait for manual login")
    parser.add_argument(
        "--run_dreamscape", action="store_true", help="After ingesting, run Dreamscape processing pipeline.",
    )
    return parser.parse_args()


def ensure_dirs(*paths: Path) -> None:
    """Create directories if they do not already exist."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    start_time = time.time()

    # Instantiate orchestrator with requested headless flag
    orch = ScraperOrchestrator(headless=args.headless, use_undetected=True)
    if not orch.initialize_browser().success:
        logger.error("Browser initialisation failed. Aborting.")
        return

    # Force orchestrator to use the provided cookies path
    orch.cookie_manager.cookie_file = args.cookies_file  # renamed attribute

    # Optional automated credentials from env
    username = password = None
    if not args.no_env_login:
        username = os.getenv("CHATGPT_USERNAME")
        password = os.getenv("CHATGPT_PASSWORD")

    login_res = orch.login_and_save_cookies(username=username, password=password)

    # Manual fallback polling
    if login_res.metadata and login_res.metadata.get("requires_manual_login"):
        logger.info("Manual login required — waiting up to %s s for user…", args.wait_secs)
        waited = 0
        while waited < args.wait_secs:
            if orch.login_handler.is_logged_in(orch.driver):
                logger.info("Manual login detected early at %s s", waited)
                break
            time.sleep(5)
            waited += 5
            logger.info("… still waiting (%s/%s)" , waited, args.wait_secs)
        else:
            logger.warning("Timed out waiting for manual login")

        orch.cookie_manager.save_cookies(orch.driver)

    # Retrieve conversation index
    index_res = orch.extract_conversations(max_conversations=args.max_conversations)
    if not index_res.success:
        logger.error(f"Conversation list extraction failed: {index_res.error}")
        orch.close()
        return

    conversations = index_res.data or []
    logger.info("Found %s conversations in history", len(conversations))

    conv_dir = Path("data/conversations")
    ensure_dirs(conv_dir)

    mem = MemoryManager()
    new_files: list[str] = []

    for conv in conversations:
        # Skip if already present in DB
        if mem.get_conversation_by_id(conv.id):
            continue

        content_res = orch.extract_conversation_content(conv.url)
        if not content_res.success:
            logger.warning("Skipping %s due to extract error: %s", conv.url, content_res.error)
            continue

        payload = content_res.data or {}
        payload["id"] = conv.id
        payload["url"] = conv.url

        dest_file = conv_dir / f"{conv.id}.json"
        try:
            with open(dest_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            new_files.append(str(dest_file))
            logger.info("Saved conversation %s", dest_file.name)
        except Exception as e:
            logger.warning("Failed to save %s: %s", dest_file, e)

    orch.close()

    # Aggregate file list for optional downstream tooling
    output_json_path = Path(args.output_json)
    ensure_dirs(output_json_path.parent)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(new_files, f, indent=2)

    # Ingest into MemoryManager
    ingested_count = mem.ingest_conversations(str(conv_dir))
    logger.info("Ingested %s new conversation(s)", ingested_count)

    # Dreamscape processing
    if args.run_dreamscape:
        dsp = DreamscapeProcessor()
        dsp.process_conversations_chronological()
        dsp.close()

    # Stats refresh
    stats_updater = ConversationStatsUpdater(mem)
    stats_updater.update_all_conversation_stats()

    final_count = mem.get_conversations_count()
    elapsed_s = time.time() - start_time

    # Devlog entry
    devlog_dir = Path("outputs/devlogs")
    ensure_dirs(devlog_dir)
    devlog_file = devlog_dir / f"{datetime.now().date()}-scrape-run.md"
    with open(devlog_file, "w", encoding="utf-8") as f:
        f.writelines(
            [
                f"# Historical Scrape Run – {datetime.now().isoformat()}\n\n",
                f"*Newly downloaded files*: {len(new_files)}\n",
                f"*Ingested*: {ingested_count}\n",
                f"*Total in DB*: {final_count}\n",
                f"*Elapsed*: {elapsed_s:.1f}s\n",
            ]
        )

    mem.close()
    logger.info("✅ Completed historical scrape in %.1fs (DB now holds %s conversations)", elapsed_s, final_count)


if __name__ == "__main__":
    main() 