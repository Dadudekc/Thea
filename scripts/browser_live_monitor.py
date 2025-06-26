#!/usr/bin/env python3
"""
Browser-based Live Monitor 🛰️
=============================

Continuously polls ChatGPT's sidebar via undetected-chromedriver, finds new
conversation threads, extracts them, stores in the DB, runs Dreamscape &
MMORPG updates, and notifies Discord.  Intended to replace the previous API
LiveProcessor with a no-API browser transport.

CLI:
    python scripts/browser_live_monitor.py --headless --interval 300

Safe to run indefinitely (catches exceptions, re-logs in if cookies expire).
"""
from __future__ import annotations

import sys
import logging
import time
import json
from pathlib import Path
from typing import Set, List, Dict, Optional

# Repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Internal imports (reuse existing modules, no new scraping logic!)
from core.memory_manager import MemoryManager
from core.conversation_stats_updater import ConversationStatsUpdater
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from core.discord_manager import DiscordManager
from core.scraper_orchestrator import ScraperOrchestrator, ConversationData, ScrapingResult

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("browser_monitor")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _store_conversation(memory: MemoryManager, conv_dict: Dict):
    """Persist conversation JSON dict directly into DB & index."""
    memory.store_conversation(conv_dict)
    # Ensure messages table / word counts
    stats_updater = ConversationStatsUpdater(memory)
    stats_updater.update_conversation_stats(conv_dict["id"])

# ---------------------------------------------------------------------------
# Live Monitor
# ---------------------------------------------------------------------------

class BrowserLiveMonitor:
    def __init__(self, *, headless: bool = False, interval_sec: int = 300):
        self.interval = interval_sec
        self.scraper = ScraperOrchestrator(headless=headless, use_undetected=True)
        self.discord = DiscordManager()
        self.dreamscape = DreamscapeProcessor()
        self.mmorpg = MMORPGEngine()
        self.known_ids: Set[str] = set()

    # ------------------------------------------------------------
    def _ensure_login(self):
        result = self.scraper.login_and_save_cookies()
        if not result.success and not result.metadata.get("requires_manual_login"):
            raise RuntimeError(f"Login failed: {result.error}")
        if result.metadata.get("requires_manual_login"):
            logger.warning("Manual login requested – waiting in browser window…")
            print("Please finish login in the opened browser, then press Enter here → ", end="", flush=True)
            input()

    # ------------------------------------------------------------
    def _initialise(self):
        logger.info("Initialising browser session …")
        res = self.scraper.initialize_browser()
        if not res.success:
            raise RuntimeError(res.error)
        self._ensure_login()

        # Prime known IDs from DB to avoid re-processing
        with MemoryManager("dreamos_memory.db") as mem:
            cursor = mem.storage.conn.cursor()
            cursor.execute("SELECT id FROM conversations")
            self.known_ids = {row[0] for row in cursor.fetchall()}
        logger.info("Monitor knows %d existing conversations", len(self.known_ids))

    # ------------------------------------------------------------
    def run_forever(self):
        self._initialise()
        while True:
            try:
                self._tick()
            except Exception as e:
                logger.error("Tick failed: %s", e, exc_info=True)
            time.sleep(self.interval)

    # ------------------------------------------------------------
    def _tick(self):
        logger.info("Polling sidebar for new conversations …")
        list_res = self.scraper.extract_conversations()
        if not list_res.success:
            logger.warning("Could not pull conversation list: %s", list_res.error)
            return
        new_items: List[ConversationData] = [c for c in list_res.data if c.id not in self.known_ids]
        if not new_items:
            logger.info("No new threads.")
            return

        logger.info("Found %d new conversations", len(new_items))
        with MemoryManager("dreamos_memory.db") as memory:
            for conv in new_items:
                self._process_single(conv, memory)

    # ------------------------------------------------------------
    def _process_single(self, conv: ConversationData, memory: MemoryManager):
        logger.info("Processing new conversation %s – %s", conv.id, conv.title)
        content_res = self.scraper.extract_conversation_content(conv.url)
        if not content_res.success:
            logger.warning("Failed to fetch content: %s", content_res.error)
            return
        conv_json = content_res.data  # Already formatted by ContentProcessor
        conv_json.setdefault("id", conv.id)
        conv_json.setdefault("url", conv.url)

        _store_conversation(memory, conv_json)
        self.known_ids.add(conv.id)

        # Dreamscape and MMORPG updates
        try:
            self.dreamscape.process_conversation_for_dreamscape(conv.id, conv_json["content"])
            self.mmorpg.update_from_conversation(conv.id)
        except Exception as e:
            logger.warning("Dreamscape/MMORPG update failed for %s: %s", conv.id, e)

        # Discord notification
        try:
            if self.discord.config.get("enabled"):
                msg = f"✨ **New Conversation** `{conv.title}` (👤 {conv_json.get('message_count',0)} msgs) processed into Dreamscape."
                import asyncio
                asyncio.run(self.discord.send_dreamscape_update(msg))
        except Exception as e:
            logger.debug("Discord message failed: %s", e)

        logger.info("Finished processing %s", conv.id)

# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Continuous browser-based ChatGPT monitor")
    p.add_argument("--headless", action="store_true", help="Run Chrome headless")
    p.add_argument("--interval", type=int, default=300, help="Polling interval in seconds (default 300)")
    args = p.parse_args()

    monitor = BrowserLiveMonitor(headless=args.headless, interval_sec=args.interval)
    monitor.run_forever() 