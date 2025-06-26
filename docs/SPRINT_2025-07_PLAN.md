# Sprint&nbsp;07 · 2025-07-01 → 2025-07-14 📅
Owner Core × GUI × Scraper × Docs | Status → Committed

This sprint consolidates the refactor work we just finished (doc cleanup, driver pinning) and focuses on two high-impact feature deliveries plus a stability objective.

---
## 1 · Objectives & Key Results (OKRs)
| ID | Objective | Key Result | Metric/Target |
|----|-----------|-----------|---------------|
| O1 | Ship Quest-Log CRUD (Phase 6 capstone) | Users can add/edit/delete quests from GUI | Integration tests Q1-Q4 pass, XP event reaches `mmorpg_engine` |
| O2 | Release Analytics Panel v1.1 | Topic cloud + time-series chart + CSV/PDF export | A1-A3 acceptance in PRD met, render < 300 ms |
| O3 | End-to-End Data Reliability | Full historical scrape completes nightly without manual intervention | ≤ 1 recoverable error over 3 consecutive nights |
| O4 | Developer Experience | No "driver version mismatch" CI failures | 100 % green CI on `main` across sprint |

---
## 2 · Backlog Items Committed
| Epic / PRD | Ticket | Description | Owner | Est (pts) |
|------------|--------|-------------|-------|-----------|
| Quest-Log CRUD (PRD Q1-Q4) | TASK-241 | New Quest dialog | GUI | 2 |
|  | TASK-242 | Edit Quest dialog | GUI | 2 |
|  | TASK-243 | Delete Quest flow | GUI | 1 |
|  | TASK-244 | XP reward dispatch hook | Core | 2 |
| Analytics Panel v1.1 (PRD A1-A3) | TASK-245 | Topic cloud widget | Core + GUI | 3 |
|  | TASK-246 | Time-series chart | GUI | 2 |
|  | TASK-247 | CSV/PDF export plumbing | Core | 2 |
| BrowserManager hard-pin | TASK-248 | webdriver-manager fallback | Scraper | 1 |
| Historical scrape reliability | TASK-249 | Pipeline watchdog + alert | Scraper + Core | 3 |
| Documentation | TASK-250 | Update README & user guides for new flows | Docs | 1 |

Velocity target: **18 story points** (historical average ≈ 18-20).

---
## 3 · Milestone Calendar
| Date | Milestone | Deliverable |
|------|-----------|-------------|
| Jul 01 | Sprint kickoff | Backlog grooming complete, branch policies locked |
| Jul 04 | Alpha cut-off | Quest-Log CRUD dialogs functional (no styling) |
| Jul 07 | Beta | Analytics Panel widgets render sample data; scrape pipeline green 3 nights |
| Jul 10 | Code freeze | All tickets merged, 90 % unit-test coverage on new code |
| Jul 12 | QA sign-off | Manual session + regression suite pass |
| Jul 14 | Sprint demo | Live demo, release notes posted, roadmap updated |

---
## 4 · Dependencies & Risks
* Chrome v139 expected mid-July — may require updating driver pin logic (mitigated by webdriver-manager fallback).
* Discord rate-limits could block XP webhook; we'll mock during tests.
* Analytics queries could hit DB index issues; monitor with profiler flag.

---
## 5 · Definition of Done ✅
1. All KRs met with green CI.
2. Docs: PRDs updated with status **"Done"** or **"v1.1 Released"**.
3. CHANGELOG entry & version bump to `0.7.0`.
4. Demo video/GIF recorded and linked in README.

---
> Linked PRDs: `docs/QUEST_LOG_CRUD_PRD.md`, `docs/ANALYTICS_PANEL_V1_1_PRD.md`  
> Updated roadmaps: `PROMPT_SYSTEM_ROADMAP.md`, `TASK_SYSTEM_ROADMAP.md`. 