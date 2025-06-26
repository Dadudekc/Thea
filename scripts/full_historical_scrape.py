#!/usr/bin/env python3
"""
full_historical_scrape.py
purpose : End-to-end import of ALL ChatGPT history → Dream.OS
updated : 2025-06-26  (v2)

Highlights
────────
• Resumable (idempotent) runs  • Quieter terminal  • Robust scroll detection
• Progress bar  • Auth-failure forensics (HTML + PNG) • Optional log file
"""

from __future__ import annotations
import os, sys, argparse, json, logging, time, traceback
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Project bootstrap so script can run standalone
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.scraper_orchestrator import ScraperOrchestrator
from core.memory_manager import MemoryManager
from core.dreamscape_processor import DreamscapeProcessor
from core.conversation_stats_updater import ConversationStatsUpdater

# --------------------------------------------------------------------------- #
#  3rd-party (optional) helpers
# --------------------------------------------------------------------------- #
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = lambda x, **_: x  # fallback – no progress bar

try:
    from tenacity import retry, stop_after_attempt, wait_fixed  # type: ignore
except ImportError:  # lightweight fallback
    def retry(*_, **__):                     # noqa: E302
        def deco(fn): return fn
        return deco
    stop_after_attempt = wait_fixed = None   # type: ignore

# --------------------------------------------------------------------------- #
#  CLI + logging
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    today = datetime.now().date().isoformat()
    p = argparse.ArgumentParser(description="Full historical scraper for ChatGPT.")
    p.add_argument("--max-conversations", type=int, default=1300)
    p.add_argument("--cookies-file", default="data/chatgpt_cookies.pkl")
    p.add_argument("--output-json", default=f"outputs/all_convos_{today}.json")
    p.add_argument("--headless", action="store_true", default=False)
    p.add_argument("--env-login", action="store_true", help="Attempt automated credential login only (skip manual)")
    p.add_argument("--wait-secs", type=int, default=120, help="Manual-login window")
    p.add_argument("--scroll-timeout", type=int, default=2, help="Pause between scrolls (s)")
    p.add_argument("--pause", type=float, default=0.75, help="Courtesy delay between convo fetches (s)")
    p.add_argument("--resume", action="store_true", help="Skip JSONs already on disk")
    p.add_argument("--log-file", default=None, help="Write detailed log here")
    p.add_argument("--verbose", action="store_true", help="Console INFO level")
    p.add_argument("--run-dreamscape", action="store_true")
    return p.parse_args()


def configure_logging(args: argparse.Namespace) -> None:
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            *( [logging.FileHandler(args.log_file, encoding="utf-8")]
               if args.log_file else [] )
        ],
    )
    # Silence selenium / urllib spew
    for noisy in ("selenium", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.ERROR)


logger = logging.getLogger("full_historical_scrape")


# --------------------------------------------------------------------------- #
#  Utility helpers
# --------------------------------------------------------------------------- #
def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def robust_scroll(driver, pause: int, max_scrolls: int = 200) -> None:
    """Scroll until height and item-count stop growing."""
    last_h = driver.execute_script("return document.body.scrollHeight")
    last_items = 0
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_h = driver.execute_script("return document.body.scrollHeight")
        items = len(driver.find_elements("css selector", ".conversation-list-item"))
        if new_h == last_h and items == last_items:
            break
        last_h, last_items = new_h, items


def is_logged_in(driver) -> bool:
    try:
        return ("chat.openai.com" in driver.current_url and
                driver.find_elements("css selector", ".conversation-list-item"))
    except Exception:
        return False


def save_debug_artifacts(driver, stem="auth_debug") -> None:
    html = driver.page_source
    (Path("outputs") / f"{stem}.html").write_text(html, encoding="utf-8")
    try:
        driver.save_screenshot(str(Path("outputs") / f"{stem}.png"))
    except Exception:
        pass


# --------------------------------------------------------------------------- #
#  Retry wrappers (no-op if tenacity missing)
# --------------------------------------------------------------------------- #
def _retry(**kw):
    if retry is stop_after_attempt is None:  # tenacity missing
        def deco(fn): return fn
        return deco
    return retry(**kw)


@_retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_conversation(orchestrator, url):
    return orchestrator.extract_conversation_content(url)


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    configure_logging(args)
    start = time.time()

    orch = ScraperOrchestrator(headless=args.headless, use_undetected=True)
    if not orch.initialize_browser().success:
        logger.error("Browser init failed, aborting.")
        return
    orch.cookie_manager.cookie_file = args.cookies_file

    # --- login --------------------------------------------------------------
    if args.env_login:
        username = os.getenv("CHATGPT_USERNAME")
        password = os.getenv("CHATGPT_PASSWORD")
    else:
        username = password = None

    try:
        login_res = orch.login_and_save_cookies(
            username=username,
            password=password,
            allow_manual=not args.env_login,
            manual_timeout=args.wait_secs,
        )
    except Exception:
        logger.exception("Fatal during login")
        save_debug_artifacts(orch.driver)
        return

    if login_res.metadata and login_res.metadata.get("requires_manual_login"):
        logger.info("Manual login needed – waiting up to %s s", args.wait_secs)
        for waited in range(0, args.wait_secs, 5):
            if is_logged_in(orch.driver):
                logger.info("Login complete after %s s", waited)
                break
            time.sleep(5)
        else:
            logger.error("Timed out waiting for manual login")
            save_debug_artifacts(orch.driver)
            return
        orch.cookie_manager.save_cookies(orch.driver)

    # --- scrape list --------------------------------------------------------
    robust_scroll(orch.driver, pause=args.scroll_timeout)
    index_res = orch.extract_conversations(max_conversations=args.max_conversations)
    if not index_res.success:
        logger.error("Conversation index extraction failed: %s", index_res.error)
        return

    conversations = index_res.data or []
    logger.info("Total conversations reported: %d", len(conversations))

    conv_dir = Path("data/conversations")
    ensure_dirs(conv_dir)
    mem = MemoryManager()
    new_files: list[str] = []

    # --- main loop ----------------------------------------------------------
    loop_iter = tqdm(conversations, desc="Downloading", unit="conv") if not isinstance(tqdm, type(lambda: None)) else conversations

    for conv in loop_iter:
        dest_file = conv_dir / f"{conv.id}.json"

        if args.resume and dest_file.exists():
            continue
        if mem.get_conversation_by_id(conv.id):
            continue

        content_res = fetch_conversation(orch, conv.url)
        if not content_res.success:
            logger.warning("Skip %s: %s", conv.id, content_res.error)
            continue

        payload = content_res.data or {}
        payload.update({"id": conv.id, "url": conv.url})
        try:
            dest_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            new_files.append(str(dest_file))
        except Exception:
            logger.warning("Write failed for %s\n%s", dest_file, traceback.format_exc())
            continue

        time.sleep(args.pause)

    orch.close()

    # --- output list --------------------------------------------------------
    out_json = Path(args.output_json)
    ensure_dirs(out_json.parent)
    out_json.write_text(json.dumps(new_files, indent=2), encoding="utf-8")

    # --- ingest -------------------------------------------------------------
    ingested = mem.ingest_conversations(str(conv_dir))
    if args.run_dreamscape:
        DreamscapeProcessor().process_conversations_chronological().close()
    ConversationStatsUpdater(mem).update_all_conversation_stats()

    elapsed = time.time() - start
    logger.warning("✅ Done. New %d | Ingested %d | Total %d | %.1fs",
                   len(new_files), ingested, mem.get_conversations_count(), elapsed)

    # simple devlog
    devlog = Path("outputs/devlogs") / f"{datetime.now().date()}-scrape.md"
    ensure_dirs(devlog.parent)
    devlog.write_text(
        f"""# Scrape run {datetime.now().isoformat()}

New JSONs      : {len(new_files)}
Ingested       : {ingested}
Total in DB    : {mem.get_conversations_count()}
Elapsed (s)    : {elapsed:.1f}
""",
        encoding="utf-8",
    )

    mem.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        logger.exception("Uncaught fatal: %s", exc)
        raise
