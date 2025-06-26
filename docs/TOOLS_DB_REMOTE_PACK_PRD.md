# PRD · Remote Tool Pack Import (Phase 5.2)

**Owner:** Tools-DB Agent  
**Stakeholders:** DevOps, Docs, Discord, QA  
**Status:** Draft → Auto-approved

---

## 1. Problem Statement
Developers want to share Dream.OS CLI tools across projects or download community-made utilities without copy-pasting source files into `tools/`. We need a safe, single-command way to ingest a "tool pack" from a URL (raw file, GitHub gist, zip) while preserving signature-based governance.

## 2. Goals
| # | Goal | Metric | Acceptance |
|---|------|--------|------------|
| R1 | Import single `.py` or `.zip` via URL | `dreamos tools import <url>` succeeds | Unit test downloads public raw URL |
| R2 | Compute signature + new `version` row | Signature stored matches SHA-256 | Parity test passes |
| R3 | Record `origin_url` & `owner` metadata | Columns populated | `tools show` displays fields |
| R4 | Skip duplicates (signature match) | Duplicate not inserted | Test proves only 1 row |

## 3. Non-Goals
• Private auth/SSH Git fetch (future).  
• Zip contents deeper than 1-level – only top-level `.py` files.

## 4. Success Metrics
* Import command completes <3s for raw file, <10s for <200 KB zip.  
* 100 % signature coverage.  
* Zero schema migrations required by other agents.

## 5. Solution Overview
1. **Schema** – add `origin_url` column (`TEXT`).  
2. **Importer API** – new function `import_from_url(url, owner='external')` that:
   * Detects zip vs single file.
   * Downloads content with `requests` (existing dep).  
   * For each `.py` file → call existing insert logic (version/signature).
3. **CLI** – `dreamos tools import <url> [--owner alice]` (sub-command under `tools`).
4. **Docs** – update Showcase with example importing a GitHub raw link.

## 6. Milestones (0.5 day)
| Hours | Deliverable |
|-------|-------------|
| 1 | Schema migration + helper API |
| 1 | CLI sub-command + unit tests |
| 0.5 | Docs & checklist update |

## 7. Risks
* Malicious code import – mitigated by warning user and recording origin URL.  
* Zip bomb – enforce max 200 KB download.

---

> **Next Action:** implement schema migration, API, CLI + tests now. 