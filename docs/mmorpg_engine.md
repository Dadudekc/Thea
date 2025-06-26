# MMORPG Engine Overview

The `MMORPGEngine` serves as the single authoritative source for all game mechanics, state, and business logic in Dream.OS.

## Quest Management (v3)

* `accept_quest(quest_id: str) -> Quest`: Accept a quest and move it to the active list.
* `complete_quest(quest_id: str) -> Quest`: Mark an active quest as completed and award XP.
* `get_active_quests() -> List[Quest]`: Retrieve all active quests for the current player.
* `get_quests_by_status(status: str) -> List[Quest]`: Filter quests by `active`, `completed`, or `failed`.
* `create_guild(name: str) -> Guild`: Create a new guild and register it with the engine.
* `join_guild(guild_id: str) -> GuildMembership`: Join an existing guild.
* `get_guild_info(guild_id: str) -> Guild`: Fetch guild data including member roster and quests.

> **NOTE:** Prior versions relied on `TaskTracker`. That file has been removed; all quest state now resolves exclusively through `MMORPGEngine` and the underlying `GameState` dataclass.

## Single-Source-of-Truth Doctrine

`MMORPGEngine` must remain the *only* module with write access to quest and guild state. External consumers (GUI, Discord, CLI, tests) **must never** manipulate quest dictionaries directly. Always route calls through the public API above.

---

_Last updated: 2025-06-25 – Quest refactor sweep._ 