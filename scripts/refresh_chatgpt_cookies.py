#!/usr/bin/env python3
"""Refresh ChatGPT cookies and emit Discord alert.

Usage (local):
    python scripts/refresh_chatgpt_cookies.py

CI will invoke the script with `--ci` so we can tweak behaviour (e.g. shorter
timeouts, hard-exit on failure).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scrapers.browser_manager import BrowserManager  # type: ignore
from scrapers.login_handler import LoginHandler
from scrapers.cookie_manager import CookieManager

# Discord
from core.discord_bridge import DiscordBridge
from core.models import DSUpdate

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(REPO_ROOT / "logs" / "refresh_chatgpt_cookies.log"),
    ],
)
logger = logging.getLogger(__name__)


def emit_dsupdate(success: bool, duration: float):
    """Helper to dispatch DSUpdate alerts (non-blocking)."""

    bridge = DiscordBridge()
    msg = (
        f"🔐 Cookie refresh successful in {duration:.1f}s." if success else
        "❌ Cookie refresh failed. Manual intervention required."
    )
    kind = "lore"  # maps to general info feed
    try:
        bridge.handle_sync(DSUpdate(kind=kind, msg=msg))
    except Exception as e:
        logger.debug(f"[DSUpdate] emit skipped: {e}")


def refresh_cookies(headless: bool = True, timeout: int = 60) -> bool:
    """Perform automated login and persist cookies."""
    start = time.time()

    browser = BrowserManager(headless=headless, use_undetected=True)
    driver = browser.create_driver()

    cm = CookieManager()
    lh = LoginHandler(timeout=timeout)

    try:
        ok = lh.ensure_login_with_cookies(driver, cm, allow_manual=False)
        duration = time.time() - start
        if ok:
            logger.info("[OK] Login + cookie refresh complete (%.1fs)", duration)
        else:
            logger.error("[FAIL] Login flow failed (%.1fs)", duration)
        emit_dsupdate(ok, duration)
        return ok
    finally:
        browser.close_driver()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh ChatGPT cookies.")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--ci", action="store_true", help="Optimise for CI (shorter timeout, fail fast)")
    args = parser.parse_args()

    success = refresh_cookies(headless=not args.no_headless, timeout=30 if args.ci else 60)
    sys.exit(0 if success else 1) 