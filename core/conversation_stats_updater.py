#!/usr/bin/env python3
"""Conversation Statistics Updater
=================================
Centralised helper that extracts individual messages from raw conversation
content and normalises them into the `messages` table while maintaining word
and token counts.  Also exposes high-level summary helpers used by the GUI,
CLI and analytics pipeline.

This version removes earlier duplicate method definitions and an accidental
`finally:` block that broke static analysis.  The public surface is unchanged
so no callers need to be updated.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper class
# ---------------------------------------------------------------------------


class ConversationStatsUpdater:
    """Updates conversation statistics by extracting/storing messages."""

    # ---------------------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------------------

    def __init__(self, memory_manager: "MemoryManager") -> None:  # type: ignore
        self.memory_manager = memory_manager
        self.storage = memory_manager.storage  # Short-hand to SQLite connection

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_all_conversation_stats(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Refresh stats for *all* conversations (or first *limit*).

        Returns a dict so callers (GUI, CLI) can show progress details.
        """
        try:
            conversations = self.memory_manager.get_conversations_chronological(limit=limit)
            total_conversations = len(conversations)
            if not conversations:
                return {"success": True, "updated_count": 0, "total_conversations": 0}

            updated_count: int = 0
            errors: List[str] = []

            for convo in conversations:
                try:
                    result = self.update_conversation_stats(convo["id"])
                    if result.get("success"):
                        updated_count += 1
                    else:
                        errors.append(
                            f"{convo.get('title', 'Untitled')}: {result.get('error', 'unknown error')}"
                        )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Failed to update stats for %s", convo.get("id"))
                    errors.append(f"{convo.get('title', 'Untitled')}: {exc}")

            return {
                "success": True,
                "updated_count": updated_count,
                "total_conversations": total_conversations,
                "errors": errors,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Bulk stats update failed")
            return {"success": False, "error": str(exc)}

    def update_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Extract messages from a single conversation and persist metrics."""
        try:
            conversation = self.memory_manager.get_conversation_by_id(conversation_id)
            if not conversation:
                return {"success": False, "error": f"Conversation {conversation_id} not found"}

            messages = self._extract_messages_from_content(conversation.get("content", ""))
            if not messages:
                return {"success": False, "error": "No messages found"}

            # Reset + insert fresh messages
            self._clear_existing_messages(conversation_id)
            stored_messages = self._store_messages(conversation_id, messages)

            total_words = sum(msg["word_count"] for msg in stored_messages)
            self._update_conversation_counts(conversation_id, len(stored_messages))
            self._update_conversation_word_count(conversation_id, total_words)

            return {
                "success": True,
                "messages_stored": len(stored_messages),
                "total_words": total_words,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Stat update failed for %s", conversation_id)
            return {"success": False, "error": str(exc)}

    def get_conversation_stats_summary(self, *, trend: bool = False) -> Dict[str, Any]:
        """Aggregate project-wide statistics.

        When *trend* is True additional recent-window metrics (daily/weekly/
        monthly) and rolling averages are included.  Works directly against the
        DB for speed.
        """
        cursor = self.storage.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations WHERE message_count > 0")
        conversations_with_messages = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT SUM(message_count) as total_messages, SUM(word_count) as total_words
            FROM conversations
            """
        )
        total_messages, total_words = cursor.fetchone()  # type: ignore[misc]
        total_messages = total_messages or 0
        total_words = total_words or 0

        cursor.execute("SELECT COUNT(*) FROM messages")
        actual_messages = cursor.fetchone()[0]

        summary: Dict[str, Any] = {
            "total_conversations": total_conversations,
            "conversations_with_messages": conversations_with_messages,
            "total_messages": total_messages,
            "actual_messages_in_table": actual_messages,
            "total_words": total_words,
            "accuracy": "Good" if total_messages == actual_messages else "Needs Update",
        }

        if trend:
            # Recent windows --------------------------------------------------
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE timestamp >= datetime('now', '-1 day')"
            )
            summary["daily_conversations"] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE timestamp >= datetime('now', '-7 days')"
            )
            summary["weekly_conversations"] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE timestamp >= datetime('now', '-30 days')"
            )
            summary["monthly_conversations"] = cursor.fetchone()[0]

            # Rolling average messages/conv over last 30 days ----------------
            cursor.execute(
                """
                SELECT SUM(message_count), COUNT(*)
                FROM conversations
                WHERE timestamp >= datetime('now', '-30 days')
                """
            )
            recent_msg_sum, recent_conv_count = cursor.fetchone()  # type: ignore[misc]
            recent_msg_sum = recent_msg_sum or 0
            recent_conv_count = recent_conv_count or 0
            summary["avg_messages_per_conversation_last_30_days"] = (
                recent_msg_sum / recent_conv_count if recent_conv_count else 0
            )

        return summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_messages_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse raw transcript text into structured messages."""
        messages: List[Dict[str, Any]] = []
        if not content.strip():
            return messages

        lines = content.split("\n")
        current: Optional[Dict[str, Any]] = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"^(User|Assistant|System|Human|AI):\s*(.+)$", line, re.IGNORECASE)
            if match:
                # Commit previous message
                if current:
                    messages.append(current)

                role = match.group(1).lower()
                if role == "human":
                    role = "user"
                elif role == "ai":
                    role = "assistant"

                current = {
                    "role": role,
                    "content": match.group(2).strip(),
                    "word_count": len(match.group(2).split()),
                }
            elif current:
                # Continuation line
                current["content"] += "\n" + line
                current["word_count"] = len(current["content"].split())

        # Push the last buffered message
        if current:
            messages.append(current)

        # Fallback – treat the whole blob as assistant text
        if not messages:
            messages.append({
                "role": "assistant",
                "content": content.strip(),
                "word_count": len(content.split()),
            })
        return messages

    # ------------------------------------------------------------------
    # DB helper methods
    # ------------------------------------------------------------------

    def _clear_existing_messages(self, conversation_id: str) -> None:
        cursor = self.storage.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        self.storage.conn.commit()

    def _store_messages(self, conversation_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stored: List[Dict[str, Any]] = []
        cursor = self.storage.conn.cursor()

        for idx, msg in enumerate(messages):
            word_count = msg.get("word_count", len(msg["content"].split()))
            token_estimate = len(msg["content"]) // 4  # quick heuristic

            cursor.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, content, message_index, word_count, token_estimate, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    msg["role"],
                    msg["content"],
                    idx,
                    word_count,
                    token_estimate,
                    datetime.now().isoformat(),
                ),
            )
            stored.append({
                "id": cursor.lastrowid,
                "role": msg["role"],
                "content": msg["content"],
                "word_count": word_count,
            })

        self.storage.conn.commit()
        return stored

    def _update_conversation_counts(self, conversation_id: str, message_count: int) -> None:
        cursor = self.storage.conn.cursor()
        cursor.execute(
            """
            UPDATE conversations SET message_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (message_count, conversation_id),
        )
        self.storage.conn.commit()

    def _update_conversation_word_count(self, conversation_id: str, word_count: int) -> None:
        cursor = self.storage.conn.cursor()
        cursor.execute(
            """
            UPDATE conversations SET word_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (word_count, conversation_id),
        )
        self.storage.conn.commit()
 