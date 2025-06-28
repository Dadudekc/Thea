# Dream.OS Beta-Ready Checklist

Target Date: **2025-07-07**

This checklist consolidates tasks from the PRD and sprint roadmap (TASK‑241 → TASK‑250) required for a beta release.

## Core Integration
- [x] Connect all core modules to the GUI ✅ _(Agent 3 complete)_
- [x] End-to-end tests pass (`tests/integration/test_gui_entrypoints.py`) ✅

## MMORPG and Context Intelligence
- [x] Scrape pipeline watchdog alerting for three nights — ✅ Implemented 2025-06-27 (Agent-1)
- [x] Quest system operational with XP dispatch ✅ Completed 2025-06-27 (Agent-2)
- [x] Context engine active and tested (`tests/context/test_context_engine.py`) ✅
- [x] Conversation extraction complete (`data/all_convos.json`) ✅ Completed 2025-06-27 (Agent-2)
- [x] Browser driver hard-pinned (`BrowserManager.py`) ✅ Completed 2025-06-27 by Agent 2
- [x] XP reward dispatch to MMORPG engine (`mmorpg/xp_dispatcher.py`) ✅ Completed 2025-06-27 by Agent 2

## Discord Integration
- [ ] Devlog updates with rich embeds (`DiscordBridge.handle_sync` → embeds show title, link, snippet)
- [ ] Live-processing alerts posted to #story and #quests channels
- [ ] Import-button summary posted to #devlog (files ingested, total count)
- [ ] Bot slash-commands (`/quest`, `/skill`, `/lore`) return expected JSON
- [ ] Rate-limit handling tested (`tests/discord/test_ratelimits.py`)
- [ ] Token / guild / channel IDs read from unified `.env` / Settings panel

## Analytics Panel v1.1
- [ ] Topic cloud widget
- [ ] Time-series chart
- [ ] CSV/PDF export
- [ ] Sample data renders in under 300 ms

## Quest-Log CRUD Panel
- [ ] New Quest dialog
- [ ] Edit Quest dialog
- [ ] Delete Quest flow
- [x] XP reward dispatch to MMORPG engine (`mmorpg/xp_dispatcher.py`) ✅ Completed 2025-06-27 by Agent 2

## Reliability & Tooling
- [x] Browser driver hard-pinned (`BrowserManager.py`) ✅ Completed 2025-06-27 by Agent 2
- [x] Scrape pipeline watchdog alerting for three nights — ✅ Implemented 2025-06-27 (Agent-1)

## Testing & Optimization
- [ ] Regression suite (unit + integration)
- [ ] Response time benchmark < 2 s
- [ ] CI pipeline green (`ci/test_ci_integrity.py`)

## Documentation
- [ ] README and user guides updated
- [ ] PRDs marked "Done" or "v1.1 Released"

---
Generated on `2025-06-27`
Updated on `2025-06-27` - Conversation extraction completed, Quest system operational