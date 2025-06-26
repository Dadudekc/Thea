#!/usr/bin/env python3
"""
Process Remaining Conversations & Publish DevLog
================================================

Utility script that:
1. Processes EVERY conversation stored in *dreamos_memory.db* via the
   existing `DreamscapeProcessor` (reuse-first).
2. Relies on the built-in DSUpdate emission hooks inside `DreamscapeProcessor`
   and `MMORPGEngine` so story / quest updates automatically flow to Discord
   through `DiscordBridge` ➜ `DiscordManager`.
3. Publishes a concise DevLog entry to the **#dreamscape-devlog** channel
   impersonating **Agent-3** (the persona tag is injected in the title).

The script is designed to be safe to run multiple times – it does **not**
introduce any duplicate quests or memory entries beyond what existing
processors already guard against.

Requirements:
- `DISCORD_BOT_TOKEN` **and** `DISCORD_CHANNEL_AGENT_3` (or a proper
  `config/discord_config.json` entry mapping `channels.agent3`) must be set for
  Discord posting.
- No additional dependencies – reuses current project architecture.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import List

# Ensure repository root is on `sys.path` so direct execution works
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Project imports (reuse-first) ------------------------------------------------
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from tools.devlog_tool import DevLogTool

# ----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path("logs") / "process_remaining_conversations.log"),
    ],
)
logger = logging.getLogger(__name__)


async def _post_devlog(processed: int, total: int, errors: List[str]):
    """Compose and dispatch the DevLog entry to Discord."""

    devlog = DevLogTool()

    title = "[Agent-3] Backlog Processing Run"
    description = "Processed all remaining conversations and dispatched DSUpdate events."

    # Build human-readable content block ------------------------------------------------
    lines: List[str] = [
        f"**Summary**",  # Markdown friendly
        f"• Conversations processed: **{processed} / {total}**",
        f"• Errors encountered: **{len(errors)}**",
    ]
    if errors:
        lines.append("\n**Sample Errors (first 5)**")
        for err in errors[:5]:
            lines.append(f"- {err}")
        if len(errors) > 5:
            lines.append(f"- ...and {len(errors) - 5} more")

    content = "\n".join(lines)

    post = devlog.create_devlog(
        title=title,
        description=description,
        content=content,
        tags=["dreamscape", "automation", "backlog"],
    )

    discord_msg = devlog.format_for_discord(post)

    # Attempt semantic channel dispatch first (requires connected bot) --------
    try:
        if devlog.discord.is_connected:
            await devlog.discord.send_update("agent3", discord_msg)
            logger.info("[OK] DevLog sent via connected bot")
            return
    except Exception as e:
        logger.warning(f"[WARN] Bot dispatch failed – falling back to REST: {e}")

    # Fallback: REST API helper inside DevLogTool -----------------------------
    chan_id = devlog.discord.config.get("channels", {}).get("agent3")
    success = await devlog.post_to_discord(discord_msg, channel_id=chan_id)
    if success:
        logger.info("[OK] DevLog posted via REST fallback")
    else:
        logger.error("[ERROR] Failed to post DevLog update to Discord")


async def main():
    """Entry-point coroutine."""
    logger.info("=== Dreamscape Backlog Processing : START ===")

    dsp = DreamscapeProcessor()
    mmrpg = MMORPGEngine()

    # Retrieve ALL conversations (limit=None triggers unlimited fetch)
    conversations = dsp.memory_manager.get_conversations_chronological(limit=None)
    total_conversations = len(conversations)

    processed_count = 0
    errors: List[str] = []

    for convo in conversations:
        try:
            result = dsp.process_conversation_for_dreamscape(
                convo["id"], convo.get("content", "")
            )
            if result.get("success"):
                processed_count += 1

                # --- Quest lifecycle (emit DSUpdate 'quests') ---------------
                quest = mmrpg.generate_quest_from_conversation(
                    convo["id"], convo.get("content", "")
                )
                if quest:
                    # Activate then immediately complete to broadcast update
                    mmrpg.accept_quest(quest.id)
                    mmrpg.complete_quest(quest.id)
                    logger.debug(
                        f"Quest '{quest.title}' generated & completed for conversation {convo['id']}"
                    )
            else:
                errors.append(
                    f"{convo.get('title', 'Untitled')}: {result.get('error', 'unknown error')}"
                )
        except Exception as exc:
            errors.append(f"{convo.get('title', 'Untitled')}: {exc}")
            logger.exception("[ERROR] Exception while processing conversation")

    # Close resources ---------------------------------------------------------
    dsp.close()

    logger.info(
        f"Processing complete: {processed_count}/{total_conversations} conversations processed"
    )

    # Publish DevLog ----------------------------------------------------------
    await _post_devlog(processed_count, total_conversations, errors)

    logger.info("=== Dreamscape Backlog Processing : END ===")


if __name__ == "__main__":
    asyncio.run(main()) 