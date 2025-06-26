#!/usr/bin/env python3
"""
Nightly Conversation Pipeline
=============================

1. Scrape ALL ChatGPT threads into `data/conversations/*.json` (via
   ConversationHistoryScraper).
2. Ingest new/updated JSON files into the SQLite memory DB.
3. Re-compute message counts + word counts (ConversationStatsUpdater).
4. Generate lightweight analytics JSON (top longest threads, busiest days).
5. Dreamscape storyline processing.
6. Update MMORPG engine (basic XP increment per processed convo).
7. Optional Discord notification.

Intended to be run from cron / GitHub Actions every night.

Example:
    python scripts/nightly_conversation_pipeline.py --headless
"""
from __future__ import annotations

import sys
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import asyncio

# Repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Existing components
from scripts.complete_conversation_scraper import ConversationHistoryScraper
from core.memory_manager import MemoryManager
from core.conversation_stats_updater import ConversationStatsUpdater
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from core.discord_manager import DiscordManager

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nightly_pipeline")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_analytics(memory: MemoryManager, out_path: Path):
    """Create a small JSON analytics file for dashboard use."""
    logger.info("Generating analytics summary …")
    stats = memory.get_conversation_stats()

    # Top N longest threads by message_count
    cursor = memory.storage.conn.cursor()
    cursor.execute(
        """
        SELECT id, title, message_count, word_count, timestamp
        FROM conversations
        ORDER BY message_count DESC
        LIMIT 20
        """
    )
    top_threads = [dict(row) for row in cursor.fetchall()]

    # Daily activity for past 30 days
    cursor.execute(
        """
        SELECT DATE(timestamp) as day, COUNT(*)
        FROM conversations
        WHERE DATE(timestamp) >= DATE('now', '-30 days')
        GROUP BY day
        ORDER BY day ASC
        """
    )
    daily_rows = cursor.fetchall()
    daily_activity = {row[0]: row[1] for row in daily_rows}

    analytics = {
        "generated_at": datetime.utcnow().isoformat(),
        "stats": stats,
        "top_threads": top_threads,
        "daily_activity": daily_activity,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analytics, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Analytics written to %s", out_path)

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def run_pipeline(headless: bool = False, max_threads: int | None = None):
    # 1. Scrape
    scraper = ConversationHistoryScraper(headless=headless, max_threads=max_threads)
    scraper.run()

    # 2. Ingest conversations
    with MemoryManager("dreamos_memory.db") as memory:
        ingested = memory.ingest_conversations("data/conversations")
        logger.info("Ingested %d new/updated conversations", ingested)

        # 3. Update message stats
        updater = ConversationStatsUpdater(memory)
        res = updater.update_all_conversation_stats()
        if not res.get("success"):
            logger.error("Stats update failed: %s", res.get("error"))
        else:
            logger.info(
                "Updated stats for %d/%d conversations (errors: %d)",
                res.get("updated_count"), res.get("total_conversations"), len(res.get("errors", []))
            )

        # 4. Generate analytics JSON
        analytics_path = REPO_ROOT / "outputs" / "analytics" / "conversation_analytics.json"
        generate_analytics(memory, analytics_path)

        # 5. Dreamscape storyline processing
        dsp = DreamscapeProcessor()
        dres = dsp.process_conversations_chronological()
        logger.info("Dreamscape processed %d conversations", dres.get("processed_count", 0))

        # 6. Update MMORPG engine (basic XP increment per processed convo)
        mmorpg = MMORPGEngine()
        recent_convs = memory.get_recent_conversations(limit=50)
        for conv in recent_convs:
            mmorpg.update_from_conversation(conv['id'])

        # 7. Optional Discord notification
        try:
            dm = DiscordManager()
            if dm.config.get("enabled"):
                asyncio.run(dm.send_dreamscape_update(
                    f"📚 Nightly pipeline complete – {ingested} ingested, {res.get('updated_count')} stats updated, {dres.get('processed_count')} dreamscape processed."
                ))
        except Exception as e:
            logger.warning(f"Discord update failed: {e}")

    logger.info("Nightly pipeline completed ✅")

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Run nightly conversation scraping + analytics pipeline")
    p.add_argument("--headless", action="store_true", help="Run Chrome headless while scraping")
    p.add_argument("--max", type=int, default=None, help="Scrape only first N threads (testing)")
    args = p.parse_args()

    run_pipeline(headless=args.headless, max_threads=args.max) 