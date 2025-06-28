#!/usr/bin/env python3
"""
Scrape Pipeline Watchdog
=======================

Monitors recent conversation ingestion activity and dispatches alerts if the
scraper pipeline appears stalled.  The watchdog keeps a rolling count of
consecutive nights with *no* new conversations ingested.  After each run it
updates that counter in the `settings` table so that state persists across
invocations.

• A **warning** alert is sent after the first miss.
• A **critical** alert is sent once the miss counter reaches the configurable
  `--max-misses` threshold (default: 3).
• If the pipeline recovers (≥1 new conversation in the last *threshold* hours)
  the counter resets to zero and a recovery notification is dispatched.

Designed to be executed daily via Windows Task Scheduler, cron, or a CI job.

Usage
-----
python scripts/maintenance/watchdog_scrape.py  # default 24h window, 3-night max
python watchdog_scrape.py --hours 12 --max-misses 2
"""
from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from core.discord_bridge import DiscordBridge
from core.memory_manager import MemoryNexus
from core.models import DSUpdate

logger = logging.getLogger("watchdog.scrape")
logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"))


class ScrapeWatchdog:
    """Watches the conversations table for fresh activity."""

    def __init__(self, db_path: str, hours: int = 24, max_misses: int = 3):
        self.db_path = db_path
        self.window_hours = hours
        self.max_misses = max_misses
        self.mm = MemoryNexus(db_path)
        self.bridge = DiscordBridge()

    # ------------------------------------------------------------------
    # Persistent miss counter helpers (reuses settings key/value table)
    # ------------------------------------------------------------------
    _MISS_KEY = "watchdog_scrape_miss_count"

    def _get_miss_count(self) -> int:
        raw = self.mm.get_setting(self._MISS_KEY, 0)
        try:
            return int(raw)
        except Exception:
            return 0

    def _set_miss_count(self, val: int):
        self.mm.set_setting(self._MISS_KEY, str(val), "Consecutive scrape misses")

    # ------------------------------------------------------------------
    # Main check logic
    # ------------------------------------------------------------------
    def run_check(self):
        logger.info(
            "⏱️  Running scrape watchdog (window=%sh, max_misses=%s)",
            self.window_hours,
            self.max_misses,
        )

        cursor = self.mm.conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM conversations
            WHERE timestamp >= datetime('now', ?)
        """,
            (f"-{self.window_hours} hours",),
        )
        new_convos = cursor.fetchone()[0] or 0
        logger.info("Found %s new conversations in the last %s h", new_convos, self.window_hours)

        misses = self._get_miss_count()

        if new_convos == 0:
            misses += 1
            self._set_miss_count(misses)

            level = "CRITICAL" if misses >= self.max_misses else "WARN"
            emoji = "🚨" if level == "CRITICAL" else "⚠️"
            msg = (
                f"{emoji} Scrape pipeline alert – No new conversations ingested in the "
                f"last {self.window_hours} h (miss #{misses}/{self.max_misses})."
            )
            logger.warning(msg)
            self._send_discord(level.lower(), msg)
        else:
            if misses > 0:
                # Pipeline recovered – reset counter and notify.
                self._set_miss_count(0)
                msg = (
                    f"✅ Scrape pipeline recovered – {new_convos} new conversations "
                    f"in the last {self.window_hours} h. Counter reset."
                )
                logger.info(msg)
                self._send_discord("info", msg)
            else:
                logger.info("Pipeline healthy – no action required.")

    # ------------------------------------------------------------------
    # Discord helper
    # ------------------------------------------------------------------
    def _send_discord(self, kind: str, message: str):
        try:
            update = DSUpdate(kind=kind, msg=message)
            self.bridge.handle_sync(update)
        except Exception as exc:
            logger.debug("Discord alert skipped: %s", exc)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scrape pipeline watchdog")
    p.add_argument("--db", default="dreamos_memory.db", help="Path to SQLite DB")
    p.add_argument("--hours", type=int, default=24, help="Look-back window in hours")
    p.add_argument("--max-misses", type=int, default=3, help="Max consecutive misses before critical alert")
    return p.parse_args()


def main():
    args = parse_args()
    wd = ScrapeWatchdog(db_path=args.db, hours=args.hours, max_misses=args.max_misses)
    wd.run_check()


if __name__ == "__main__":
    main() 