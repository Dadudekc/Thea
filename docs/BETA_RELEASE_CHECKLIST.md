# Dream.OS Beta-Ready Checklist

Target Date: **2025-07-07**

This checklist consolidates tasks from the PRD and sprint roadmap (TASK‑241 → TASK‑250) required for a beta release.

## Core Integration
- [ ] Connect all core modules to the GUI
- [ ] End‑to‑end tests pass (`tests/integration/test_gui_entrypoints.py`)

## MMORPG and Context Intelligence
- [ ] Quest system operational with XP dispatch
- [ ] Context engine active and tested (`tests/context/test_context_engine.py`)
- [ ] Conversation extraction complete (`data/all_convos.json`)
- [ ] Advanced search enabled (`tests/search/test_advanced_querying.py`)

## Discord Integration
- [ ] Devlog updates with rich embeds
- [ ] Rate‑limit handling tested (`tests/discord/test_ratelimits.py`)

## Analytics Panel v1.1
- [ ] Topic cloud widget
- [ ] Time‑series chart
- [ ] CSV/PDF export
- [ ] Sample data renders in under 300 ms

## Quest‑Log CRUD Panel
- [ ] New Quest dialog
- [ ] Edit Quest dialog
- [ ] Delete Quest flow
- [ ] XP reward dispatch to MMORPG engine (`mmorpg/xp_dispatcher.py`)

## Reliability & Tooling
- [ ] Browser driver hard‑pinned (`BrowserManager.py`)
- [ ] Scrape pipeline watchdog alerting for three nights

## Testing & Optimization
- [ ] Regression suite (unit + integration)
- [ ] Response time benchmark < 2 s
- [ ] CI pipeline green (`ci/test_ci_integrity.py`)

## Documentation
- [ ] README and user guides updated
- [ ] PRDs marked "Done" or "v1.1 Released"

---
Generated on `2025-06-27`
