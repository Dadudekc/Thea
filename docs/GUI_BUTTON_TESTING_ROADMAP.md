# Dreamscape GUI Button-Validation Roadmap

Goal: Guarantee that every interactive control in the desktop UI works after every commit.

---
## 1. Scope & Inventory (Day 0-1)
1. Enumerate all panels.
2. Auto-extract button list and export to `docs/gui_button_matrix.csv`.

## 2. Test-Case Matrix (Day 1-3)
Document expected outcome for each button.

## 3. Manual Validation Pass (Day 3-4)
Run checklist, file issues with label `gui/button`.

## 4. Automated Regression Layer (Day 4-8)
* Signal-presence test (`tests/test_gui_button_connections.py`).
* Headless functional smoke tests with `pytest-qt`.
* Optional visual snapshot tests.

## 5. Semi-Automated End-to-End (Day 8-10)
Wrap network-dependent buttons behind `pytest -m e2e`.

## 6. Continuous Integration (Day 10-11)
Add GitHub Action `gui-regression.yml` running GUI tests in off-screen mode.

## 7. Documentation & Handoff (Day 11-12)
Deliver usage guide and hold demo.

### Sprint Timeline
| Day | Activity |
|-----|----------|
| 0   | Kick-off & ticket breakdown |
| 1-3 | Inventory + Matrix |
| 3-4 | Manual validation |
| 4-8 | Automated layer |
| 8-10| Semi-auto e2e |
| 10-11| CI wiring |
| 11-12| Docs & retro |

### Definition of Done
1. Matrix covers 100 % buttons.
2. Baseline manual run complete; defects filed.
3. Automated tests green.
4. CI job passes.
5. Guide documented. 