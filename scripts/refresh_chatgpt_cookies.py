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

from core.scraper_orchestrator import ScraperOrchestrator

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


def refresh_cookies(
    headless: bool = False,
    timeout: int = 60,
    env_login: bool = False,
    wait_secs: int = 30,
) -> bool:
    """Perform automated login and persist cookies using ScraperOrchestrator."""

    start = time.time()

    orch = ScraperOrchestrator(headless=headless, use_undetected=True)

    try:
        # Initialise browser early so we can apply longer timeout to login handler
        init_res = orch.initialize_browser()
        if not init_res.success:
            logger.error("Browser initialisation failed: %s", init_res.error)
            return False

        # Apply custom timeout to underlying LoginHandler if provided
        if timeout is not None:
            try:
                orch.login_handler.timeout = timeout
            except AttributeError:
                pass

        # Orchestrator.login_and_save_cookies reuses the shared LoginHandler path
        res = orch.login_and_save_cookies(
            allow_manual=not env_login,
            manual_timeout=wait_secs,
        )

        ok = res.success
        duration = time.time() - start
        if ok:
            logger.info("[OK] Login + cookie refresh complete (%.1fs)", duration)
        else:
            logger.error("[FAIL] Login flow failed (%.1fs)", duration)
        emit_dsupdate(ok, duration)
        return ok
    finally:
        orch.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh ChatGPT cookies.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (CI-friendly)")
    parser.add_argument("--ci", action="store_true", help="Optimise for CI (shorter timeout, fail fast)")
    parser.add_argument(
        "--env_login",
        action="store_true",
        help="Attempt automated credential login using environment variables and skip manual fallback",
    )
    parser.add_argument(
        "--wait_secs",
        type=int,
        default=30,
        help="Max seconds to wait for manual login when --env_login is not provided",
    )
    args = parser.parse_args()

    success = refresh_cookies(
        headless=args.headless,
        timeout=30 if args.ci else 60,
        env_login=args.env_login,
        wait_secs=args.wait_secs,
    )
    sys.exit(0 if success else 1)
