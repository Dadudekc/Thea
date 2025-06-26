# Contributing to Dream.OS

Welcome! Please follow these guard-rails to keep the codebase lean and unified.

## 1. Planning First
1. Write a short **PRD** in `docs/` (problem, goals, exit criteria).  
2. Draft a **Roadmap** (milestones / owners).  
3. Tag related agents in the PR description.

## 2. Reuse Before Rebuild
* Run `python scripts/check_duplicates.py` – ensure you're not duplicating existing logic.  
* Search `core/`, `tools_db/`, and `templates/` before creating new modules.

## 3. Tools Database Law
* All reusable CLI tools **must** be ingested into `data/tools.db` via `tools_db.ingest_tools`.  
* Physical files under `tools/` should be thin stubs after migration.  
* Updating a tool creates a new `version` row – never overwrite.

## 4. Pre-Commit & CI
* Install hooks: `pre-commit install`.  
* Commits failing duplicate or parity checks are rejected.  
* GitHub Actions re-runs these checks on every pull request.

## 5. Code Style
* Black formatting, flake8 lint, type hints mandatory.

## 6. Commit Messages
`feat(<area>): <short description>`

Thanks for contributing!  
— Dream.OS Core Maintainers 