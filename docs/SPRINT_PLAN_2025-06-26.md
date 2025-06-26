# Dream.OS Sprint Plan – 2025-06-26

## Context
Browser automation has been unified but headless login is still flaky. We need a reliable pipeline that can scrape the full ChatGPT history (~1 300 threads), refresh cookies automatically in CI, and broadcast progress through Discord.

## North-Star
By the end of this sprint every nightly GitHub workflow should be able to:
1. Refresh ChatGPT cookies in headless mode without manual intervention.
2. Execute `full_historical_scrape.py` (or an incremental variant) and ingest **all** conversations.
3. Post DevLog and DSUpdate events to the Agent-3 Discord channels.

## Work Breakdown

### Day 0 – Environment Stabilisation
- Purge UC cache (`$env:APPDATA\undetected_chromedriver\undetected`).
- Pin driver: `setx UCDRIVER_VERSION_MAIN 137` (matches local Chrome).
- Commit & push current state (unified login, all-time filter).

### Day 1 – Reliable Login & Cookies
- New helper `scripts/debug_login.py` – headed UC, live status polling.
- Add `--slow_mode` option in `LoginHandler` (1 s pauses between field inputs).
- Detect & handle Cloudflare "Verify you are human" page.

### Day 2 – Headless Hardening
- Pass extra UC flags: `--enable-unsafe-webgpu`, `--disable-software-rasterizer`, etc.
- Expose `--headless` + `--use_undetected` toggles at every CLI entry-point.
- Update `docs/automated_login_guide.md` with the "headed first run → headless CI" pattern.

### Day 3 – UX & Observability
- Replace manual polling with `rich` progress bars (countdown for manual login wait).
- Set `PYTHONIOENCODING=utf-8` in Windows launch scripts; wrap emoji log messages.
- Fix `DiscordBridge` coroutine warning (wrap in `handle_sync`).

### Day 4 – Scroll Robustness & Tests
- Auto-screenshot + HTML dump when < 100 convos detected after scroll loop.
- Add `tests/test_conversation_scroll.py` mocking sidebar to assert min conversation count.

## Known Blockers
- Persistent UC cache corruption on Windows.
- ChatGPT occasionally rate-limits history API; may require rotating proxies / multiple account cookies.

## Success Criteria
- Nightly CI run completes cookie refresh + ingest > 1 200 conversations **without manual input**.
- DevLog summarising the run appears in #dreamscape-devlog (Agent-3 persona).
- No red warnings in the log (emoji errors, coroutine warnings, etc.). 