# PRD · Tools Database Governance & Versioning (Phase 5)

**Owner:** Tools-DB Working Group  
**Stakeholders:** Dreamscape Core, Discord Bot, Memory-Agent, GUI Team, Scraper Team  
**Status:** Draft → Review (auto-approved on merge)

---

## 1. Problem Statement
The Tools DB currently stores a *single* copy of each CLI tool's source code. We lack:
1. **Historical versions** – losing provenance when a tool is updated.  
2. **Governance controls** – no signatures, metadata or ownership records.  
3. **Distribution pipeline** – no mechanism to import external "tool packs".

These gaps jeopardise reproducibility, supply-chain integrity and developer trust.

## 2. Goals (Must-Have)
| # | Goal | Metric | Acceptance |
|---|------|--------|------------|
| G1 | Version every tool insert | `version` column auto-increments | Ingestion test passes; manual update shows `v2` row |
| G2 | Guarantee immutability of past versions | SHA-256 `signature` stored & verified | Parity test extended with signature check |
| G3 | Provide simple API to fetch *latest* or *specific* version | `fetch_tool(name, v=None)` | Passed by unit tests |
| G4 | Support remote "tool pack" import (URL / Git) | `ingest_tools --url https://…` | Demo script imports pack |
| G5 | Governance metadata (owner, origin) | New columns populated | Displayed via `dreamos tools show` |

## 3. Non-Goals
• Binary/package tools (wheel, exe) – out-of-scope.  
• Fine-grained diff visualisation – optional post-MVP.

## 4. Success Metrics
* 100 % of tool updates create new version rows, never overwrite.  
* Parity & governance test suite passes in CI.  
* Remote pack import demonstrated with a public GitHub gist.

## 5. Solution Overview
1. **Schema Upgrade** – extend `tools` table:
   ```sql
   ALTER TABLE tools ADD COLUMN version INTEGER DEFAULT 1;
   ALTER TABLE tools ADD COLUMN signature TEXT;
   ALTER TABLE tools ADD COLUMN owner TEXT DEFAULT 'core';
   CREATE UNIQUE INDEX IF NOT EXISTS idx_tools_name_version ON tools(name, version);
   ```
2. **Ingestion Logic** – compute `sig = sha256(code)`; if (name,sig) exists ➜ skip; else `version = max(version)+1` insert row.
3. **API Update** –
   ```python
   def fetch_tool(conn, name, version: int | None = None):
       # latest if version is None
   ```
4. **Remote Import** – `ingest_tools.py` accepts `--url` (supports raw GitHub link); downloads file(s) and pipes into existing insertion logic.
5. **Governance Enforcement** – pre-commit hook verifies signatures unchanged.

## 6. Milestones & Timeline (1.5 days)
| Day | Deliverable | Agents Engaged |
|-----|-------------|----------------|
| 0.5 | Schema migration & API update | Tools-DB, Memory-Agent |
| 0.5 | Ingestion v2 with versioning + tests | Tools-DB |
| 0.25 | Remote pack import (Git/raw) | Tools-DB |
| 0.25 | Docs & sample demo cast | Docs Agent, Discord Bot (optional notify) |

## 7. Risks & Mitigations
* *DB Lock contention* – mitigate with WAL mode, short-lived writes.  
* *Signature collision* – SHA-256 sufficient for MVP.  
* *Tool pack trust* – warn user if signature missing.

## 8. Open Questions
1. Should we promote previous versions via CLI (`tools list --all`)?  
2. Do we need per-environment allow-lists for remote pack sources?

---

> **Next Step:** Implement schema migration & ingestion v2 as per roadmap. 