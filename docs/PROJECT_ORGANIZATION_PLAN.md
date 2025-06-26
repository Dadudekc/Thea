# Project-Wide Organization Plan

Last updated: <!-- AUTO:date -->

This document ensures every Dream.OS agent (GUI, Memory, Scraper, Discord, Tools-DB) shares a single vocabulary, directory layout and workflow.  **Follow this guide before adding new files or features.**

---

## 1. Directory Conventions
| Path | Purpose | Owner |
|------|---------|-------|
| `core/` | Pure domain logic & shared services | Core Agent |
| `gui/` | PyQt6 interface | GUI Agent |
| `scrapers/` | Web automation & data extraction | Scraper Agent |
| `tools/` | CLI entry points only (thin stubs) | Tools-DB Agent |
| `tools_db/` | DB layer & ingestion | Tools-DB Agent |
| `docs/` | All specs, PRDs, guides | Docs Agent |
| `scripts/` | One-off utilities / migrations | Whoever adds (must label owner in header) |
| `tests/` | Pytest suite | QA Agent |

---

## 2. File Naming & Ownership Tags
Every new file must contain a top-of-file comment:
```python
# owner: <agent>  |  purpose: <short desc>  |  created: YYYY-MM-DD
```
Agents: `core`, `gui`, `scraper`, `discord`, `tools-db`, `qa`, `docs`.

---

## 3. Planning & Roadmap Flow
1. Draft **PRD** → commit to `docs/`.  
2. Draft **Roadmap** → append to PRD *or* create `ROADMAP_<feature>.md`.  
3. Tag relevant agents in PR (e.g., `[core][tools-db]`).  
4. Code only begins after PRD merged.

---

## 4. Duplicate Detection Checklist
Before adding a new module/function:
1. `grep_search` repo for existing symbol.  
2. Confirm no matching functionality in `core/` or `tools_db/`.  
3. If overlap, extend existing module instead of duplicating.  
4. Record decision in PR description.

---

## 5. Release Milestones
| Phase | Exit Criteria |
|-------|---------------|
| 3 | Discord bot passes Day 5 validation, Tools-DB governance merged |
| 4 | GUI autopilot & remote packs live |
| 5 | Cloud sync & plugin marketplace |

---

## 6. Communication Hooks
* **Shared Slack channel:** #dreamos-dev  
* **Weekly triage:** Monday 10:00 UTC – rotate facilitator.  
* **PR title format:** `feat(<area>): <description>`.

---

> **Canonical home for this doc:** `docs/PROJECT_ORGANIZATION_PLAN.md`. Update it in the *first* commit of any structural change.

# Dream.OS – Project Organization & Planning Guide 📋

_Updated: {{ date }}_

## 1. Guiding Principles
1. **Reuse over Reinvent** – always search for an existing abstraction before creating a new one.
2. **Plan before Build** – every feature goes through a lightweight PRD & design review.
3. **Single Source of Truth** – one authoritative module for each capability (e.g. `core.memory_manager`, **`core.mmorpg_engine` for quests/guilds**).
4. **Incremental, End-to-End Flow** – ship vertical slices that deliver user value, even if internal APIs remain provisional.
5. **Automate Everything** – nightly pipelines, linters, CI, documentation generation.

## 2. Repository Layout (high-level)
| Directory | Purpose |
|-----------|---------|
| `core/` | Domain & service logic (memory, MMORPG, processors, routers) |
| `scrapers/` | Browser/HTTP scraping components (no DB writes) |
| `scripts/` | Orchestration, one-off CLI tools, nightly pipelines |
| `gui/` | PyQt GUI panes |
| `tools/` | Typer CLI & misc developer utilities |
| `docs/` | All documentation – roadmaps, PRDs, ADRs |
| `tests/` | Pytest suites |
| `data/` | Raw input (conversations, cookies) – **never committed** |
| `outputs/` | Generated artefacts (analytics JSON, devlogs, screenshots) |

## 3. Feature Lifecycle
1. **Idea → Ticket** Document in the backlog (`docs/FEATURE_BACKLOG.md`).
2. **PRD** Fill in `docs/FEATURE_PRD_TEMPLATE.md`; save as `docs/prd_<feature>.md`.
3. **Design Review** Async review; approvals by ≥1 maintainer.
4. **Implementation** Follow _operations guide_ Edit Handling rules.
5. **Testing** Add/extend pytest cases; lint & type-check pass.
6. **Docs & Demo** Update README / wiki; record demo GIF or CLI transcript.
7. **Release Note** Add bullet to `docs/CHANGELOG.md`.

## 4. Avoiding Duplication
+ Use `tools/scraper_cli.py fix-imports` & ripgrep before new code.
+ Shared utilities live in `core/utils/`.
+ New SQL tables require a migration script in `migrations/`.

## 5. Coding & Style Conventions
• Black, isort, flake8, mypy.  
• Functions ≤ 40 lines; modules ≤ 400 lines.  
• Structured logging – never bare `print` in `core/`.

## 6. Branch & Release Strategy
• `main` = always green.  
• Feature branches: `feat/<area>/<short-desc>` → PR → squash merge.  
• Nightly GitHub Action runs `scripts/nightly_conversation_pipeline.py`.

## 7. Roadmap Integration
Phase roadmaps (e.g., `PHASE_3_ROADMAP.md`) list **WHAT** & **WHEN**.  This guide defines **HOW** we execute each milestone.  Week-0 always includes:
1. Review & update this guide.  
2. Ensure backlog tickets & PRDs exist for every Week-1 deliverable.

---
_Maintainers: Victor 🛡️, Alice 🚀_ 