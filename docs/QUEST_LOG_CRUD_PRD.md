# PRD · Quest-Log CRUD Panel (Phase 6 Sprint Δ)

Owner GUI Agent × Core Agent × MMORPG Engine  
Status Draft → Review

---

## 1 · Problem
Users can view quests in the database but cannot create, edit, or delete them through the GUI. XP rewards are also not yet wired to the MMORPG engine.

## 2 · Goals
| # | Goal | Metric | Acceptance |
|---|------|--------|------------|
| Q1 | New Quest dialog | Modal opens & inserts row | Integration test passes, quest appears in list |
| Q2 | Edit Quest dialog | Updates `tasks` row | Changes persist, list refreshes |
| Q3 | Delete Quest | Removes row + cascade history | Row gone, undo not required |
| Q4 | XP reward dispatch | Creates `xp_gain` event to `mmorpg_engine` | Unit test shows level-up hook |

## 3 · Non-Goals
• Guild / party quests.  
• Mobile UI tweaks.

## 4 · Success Metrics
* CRUD latency < 200 ms.  
* 95 % unit test coverage on dialog logic.

## 5 · Solution Outline
1. **Model layer** – extend `core.task_models` with `Quest` dataclass + DAO.  
2. **GUI** – new `QuestDialog` (PyQt QDialog): fields title, description, due date, XP, tag.  
3. **Panel** – existing `gui/panels/task_panel.py` gets CRUD toolbar.  
4. **Engine hook** – `mmorpg_engine.award_xp(player_id, amount)` called after quest marked completed.

## 6 · Milestones (3 days)
| Day | Deliverable |
|-----|-------------|
| 1 | Model + DAO + unit tests |
| 1 | Dialog UI + validations |
| 1 | Panel wiring + XP hook + integration tests |

## 7 · Risks
* Data loss on delete → add confirmation dialog.  
* Race condition with XP award → use DB transaction.

---

> After Q4 passes tests we will mark Quest-Log CRUD as **DONE** in the consolidated roadmap. 