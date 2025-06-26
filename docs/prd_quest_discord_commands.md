# Feature PRD – Quest Discord Commands

| Item | Details |
|------|---------|
| **Owner** | Victor |
| **Stakeholders** | Game Design, Community Team |
| **Status** | Draft |
| **Target Phase / Week** | Phase 3 – Week 2 |
| **Related Issues** | – |

---

## 1. Problem Statement
Users need an in-Discord interface to view, accept and complete MMORPG quests generated from their ChatGPT conversations, without leaving the chat environment.

## 2. Goals & Success Metrics
* **Primary Goal** – Provide `/quests` slash command set for list/accept/complete quests.
* **Success**: ≥90 % of quests accepted/ completed via Discord within first day; No duplicate quest state; DB reflects status changes.

## 3. User Stories
| Role | Story | Priority |
|------|-------|----------|
| Player | As a player I can list available quests so I know what to work on. | P0 |
| Player | I can accept a quest which moves it to *active* state. | P0 |
| Player | I can mark a quest complete and receive XP/skill rewards. | P0 |

## 4. Solution Overview
Extend existing `MMORPGEngine` with quest state helpers; wire `/quests` command in `DiscordManager` to engine methods. No new DB schema required (quests already in `GameState`).

## 5. Data Flow
Slash command → DiscordManager → MMORPGEngine → update GameState → optional Discord embed confirmation.

## 6. Technical Notes
* Concurrency: commands are lightweight; single-process bot instance sufficient.
* Validation: ensure quest ID exists and status transitions valid.

## 7. Open Questions
1. Do we need role-based permissions for completing quests? (Assume any member)

## 8. Timeline
| Milestone | ETA |
|-----------|-----|
| PRD Approved | T+0d |
| Dev Complete | T+1d |
| Docs & Tests | T+1d |

## 9. Acceptance Criteria
* `/quests list` returns two embeds: available & active.
* `/quests accept <id>` moves quest to *active*; confirmation message.
* `/quests complete <id>` moves quest to *completed*, XP applied.
* Unit tests cover engine transitions.

## 10. Rollback Plan
Disable quest sub-commands in Discord bot; revert engine changes (no schema changes).

--- 