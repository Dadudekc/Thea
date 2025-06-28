#!/usr/bin/env python3
"""
Dream.OS Memory Manager
=======================

Core memory system for persistent conversation storage, indexing, and retrieval.
Enables multi-memory context sharing across agents.
"""

import glob
import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from shutil import copy2
import sqlite3
import random
import string
from datetime import datetime
import json
import dataclasses
import enum
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import storage and processor modules
from .memory_storage import MemoryStorage
from .memory_content_processor import MemoryContentProcessor
from .memory_prompt_processor import MemoryPromptProcessor

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Core memory management system for Dream.OS.
    
    Handles:
    - Conversation ingestion and indexing
    - Context retrieval and search
    - Memory persistence across agents
    """
    
    def __init__(self, db_path: str = "dreamos_memory.db"):
        """
        Initialize the Memory Manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.storage = MemoryStorage(db_path)
        self.content_processor = MemoryContentProcessor(self.storage)
        self.prompt_processor = MemoryPromptProcessor(self.storage)
        # EDIT START legacy-shim
        # Expose the underlying SQLite connection and DB path so existing tests that
        # reach into these internals keep passing until they are refactored.
        self.conn = self.storage.conn
        self.db_path = db_path
        # EDIT END legacy-shim
    
    def _normalize_conversation_json(self, raw: Any, file_path: str) -> Dict[str, Any]:
        """Convert multiple raw JSON shapes into a uniform conversation dict.

        Supported formats:
        1. Raw list[dict|str]  -> assume ChatGPT-like messages list.
        2. Dict with "messages" -> already normalised.
        3. Dict with "mapping"  -> ChatGPT official export format.
        4. Anything else        -> wrap as a single system message string.
        """
        from datetime import datetime
        import hashlib
        from pathlib import Path

        # Helper to fabricate an ID from the filename for repeatability
        file_stem = Path(file_path).stem
        fallback_id = hashlib.md5(file_stem.encode()).hexdigest()[:12]

        # Case 1: list of messages or strings
        if isinstance(raw, list):
            messages = []
            for item in raw:
                if isinstance(item, dict):
                    role = item.get("role") or item.get("author_role") or "user"
                    content = item.get("content") or item.get("text") or item.get("message") or ""
                else:  # string or unknown
                    role = "system"
                    content = str(item)
                messages.append({"role": role, "content": content})

            return {
                "id": fallback_id,
                "title": file_stem,
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
            }

        # Case 2: already in desired format
        if isinstance(raw, dict) and isinstance(raw.get("messages"), list):
            return raw

        # Case 3: ChatGPT official export with `mapping`
        if isinstance(raw, dict) and "mapping" in raw:
            mapping = raw.get("mapping", {})
            messages = []
            for node in mapping.values():
                msg = node.get("message") if isinstance(node, dict) else None
                if not msg:
                    continue
                author = msg.get("author", {}) if isinstance(msg, dict) else {}
                role = author.get("role", "unknown")
                content_dict = msg.get("content", {}) if isinstance(msg, dict) else {}
                parts = content_dict.get("parts", []) if isinstance(content_dict, dict) else []
                content = "\n".join(parts) if isinstance(parts, list) else str(parts)
                messages.append({"role": role, "content": content})

            return {
                "id": raw.get("id", fallback_id),
                "title": raw.get("title", file_stem),
                "timestamp": raw.get("create_time") or datetime.now().isoformat(),
                "messages": messages,
            }

        # Fallback: treat as a plain string
        return {
            "id": fallback_id,
            "title": file_stem,
            "timestamp": datetime.now().isoformat(),
            "messages": [{"role": "system", "content": str(raw)}],
        }
    
    def ingest_conversations(self, conversations_dir: str = "data/conversations") -> int:
        """
        Ingest conversations from JSON files into the memory database.
        
        Args:
            conversations_dir: Directory containing conversation JSON files
            
        Returns:
            Number of conversations ingested
        """
        try:
            conversation_files = glob.glob(f"{conversations_dir}/*.json")
            logger.info(f"📥 Found {len(conversation_files)} conversation files to ingest")
            
            ingested_count = 0
            
            for file_path in conversation_files:
                try:
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    
                    # Use normalizer to accommodate multiple JSON shapes
                    convo_data = self._normalize_conversation_json(raw_data, file_path)
                    
                    # Extract conversation ID from filename if not in data
                    if 'id' not in convo_data:
                        filename = Path(file_path).stem
                        if '_' in filename:
                            convo_data['id'] = filename.split('_')[-1]
                        else:
                            convo_data['id'] = hashlib.md5(filename.encode()).hexdigest()[:12]
                    
                    # Prepare conversation data
                    conversation = self.content_processor.prepare_conversation_data(convo_data, convo_data['id'])
                    
                    # Store conversation
                    if self.storage.store_conversation(conversation):
                        # Index the content for search
                        self.content_processor.index_conversation_content(conversation['id'], conversation)
                        
                        # Extract and store prompts
                        self.prompt_processor.extract_and_store_prompts(conversation['id'], convo_data)
                        
                        # Flatten messages to content/word counts if provided
                        msgs = convo_data.get('messages', [])
                        convo_data['content'] = "\n".join(msg.get('content', '') for msg in msgs)
                        convo_data['message_count'] = len(msgs)
                        convo_data['word_count'] = sum(len(m.get('content', '').split()) for m in msgs)
                        
                        ingested_count += 1
                        logger.info(f"[OK] Ingested: {conversation['title']} (ID: {conversation['id']})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to ingest {file_path}: {e}")
                    continue
            
            logger.info(f"🎉 Successfully ingested {ingested_count} conversations")
            return ingested_count
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest conversations: {e}")
            return 0
    
    def store_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Store a conversation in the memory system.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            True if stored successfully, False otherwise
        """
        return self.storage.store_conversation(conversation_data)
    
    # Search and retrieval operations
    def get_context_window(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get relevant context for a query."""
        return self.storage.search_conversations(query, limit)
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID."""
        return self.storage.get_conversation_by_id(conversation_id)
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations."""
        return self.storage.get_recent_conversations(limit)
    
    def get_conversations_chronological(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversations in chronological order (oldest first).
        This is important for storyline progression where the earliest
        conversations should be processed first.
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of conversations in chronological order
        """
        return self.storage.get_conversations_chronological(limit)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        return self.storage.get_conversation_stats()
    
    # Prompt operations
    def get_prompts_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get prompts for a specific conversation."""
        return self.storage.get_prompts_by_conversation(conversation_id)
    
    def search_prompts(self, query: str = None, category: str = None, prompt_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search prompts with filters."""
        return self.prompt_processor.search_prompts(query, category, prompt_type, limit)
    
    def get_prompt_categories(self) -> List[str]:
        """Get list of available prompt categories."""
        return self.prompt_processor.get_prompt_categories()
    
    def get_prompt_types(self) -> List[str]:
        """Get list of available prompt types."""
        return self.prompt_processor.get_prompt_types()
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Get prompt statistics."""
        return self.prompt_processor.get_prompt_stats()
    
    def close(self):
        """Close the memory manager and database connection."""
        self.storage.close()
        # EDIT START release-handle
        # Ensure the connection handle is released for Windows file deletion.
        self.conn = None
        # EDIT END release-handle
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_conversations_count(self) -> int:
        """Return the total number of conversations."""
        return self.storage.get_conversations_count()

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        stats = self.get_conversation_stats()
        stats['total_tags'] = len(self.get_tags())
        stats['total_templates'] = len(self.get_templates())
        # Total analyses
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        stats['total_analyses'] = cursor.fetchone()[0]
        # Recent conversations (last 7 days)
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE timestamp >= datetime('now', '-7 days')")
        stats['recent_conversations'] = cursor.fetchone()[0]
        return stats

    # EDIT START legacy-helpers
    def _extract_content(self, conversation: Dict[str, Any]) -> str:
        """Backward-compat extraction used only by legacy unit tests.

        It builds a plain-text representation in this order:
        1. full_conversation field if present.
        2. each message in `messages` list.
        3. each item in `responses` list.
        Segments are separated by blank lines (\n\n).
        """
        parts: list[str] = []
        if conversation.get("full_conversation"):
            parts.append(str(conversation["full_conversation"]).strip())
        # messages
        for msg in conversation.get("messages", []):
            parts.append(str(msg.get("content", "")).strip())
        # responses (older export shape)
        for resp in conversation.get("responses", []):
            # Some shapes nest content under 'content', others are raw strings
            if isinstance(resp, dict):
                parts.append(str(resp.get("content", "")).strip())
            else:
                parts.append(str(resp).strip())
        return "\n\n".join(filter(None, parts))

    def _chunk_content(self, content: str, chunk_size: int = 50) -> List[str]:
        """Split content into word-sized chunks for search indexing (legacy tests)."""
        words = content.split()
        if not words:
            return []
        chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks if chunks else [content]
    # EDIT END legacy-helpers

    def save_game_state(self, state: Any) -> None:
        """Persist MMORPG game state as JSON blob under the `settings` table.

        The payload can be a dataclass (will be serialised via `asdict`) or a
        plain ``dict``.  It is stored under the key ``mmorpg_game_state`` so
        multiple subsystems can fetch it consistently.
        """
        key = "mmorpg_game_state"
        # Convert dataclass → dict if necessary
        if dataclasses.is_dataclass(state):
            from dataclasses import asdict
            payload = asdict(state)
        else:
            payload = state
        try:
            import enum, datetime as _dt

            def _json_default(o):
                if isinstance(o, enum.Enum):
                    return o.value
                if isinstance(o, (datetime, _dt.datetime)):
                    return o.isoformat()
                return str(o)

            self.set_setting(key, json.dumps(payload, default=_json_default), "Serialized MMORPG engine state")
        except Exception as exc:
            logger.warning("⚠️ Failed to save game state: %s", exc)

    def load_game_state(self) -> Optional[Dict[str, Any]]:
        """Return the previously stored game state dict, or None if missing."""
        import json, typing

        key = "mmorpg_game_state"
        raw = self.get_setting(key)
        if not raw:
            return None
        try:
            return typing.cast(Dict[str, Any], json.loads(raw))
        except Exception as exc:
            logger.warning("⚠️ Failed to parse stored game state: %s", exc)
            return None

    # ---------------------------------------------------------------------
    # Settings (lightweight accessors shared by MMORPGEngine) --------------
    # ---------------------------------------------------------------------
    def get_setting(self, key: str, default: Any = None):
        """Return a stored setting value or *default* when missing.

        Exposed here (and mirrored in MemoryNexus) so that upstream modules
        such as ``MMORPGEngine`` can persist small blobs like the serialized
        game state without importing the heavier legacy adapter.
        """
        cursor = self.storage.conn.cursor()
        try:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        except sqlite3.OperationalError as err:
            if "no such table" in str(err):
                # Bootstrap minimal settings table for fresh DBs used in unit tests
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT, description TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)"
                )
                self.storage.conn.commit()
                return default
            raise

    def set_setting(self, key: str, value: Any, description: str | None = None):
        """Insert or update a setting row."""
        cursor = self.storage.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)",
            (key, value, description),
        )
        self.storage.conn.commit()

    # ------------------------------------------------------------------
    # Optimised concurrent ingestion (ported from experimental branch)
    # ------------------------------------------------------------------
    def ingest_conversations_async(
        self,
        conversations_dir: str = "data/conversations",
        max_workers: int = 8,
    ) -> int:
        """Parse and ingest many conversation JSON files concurrently.

        This method off-loads the expensive *disk IO → JSON → normalise* work
        onto a thread-pool, then serialises DB writes + indexing to avoid
        SQLite write-locks.
        """
        from pathlib import Path
        from datetime import datetime
        import hashlib, json as _json

        files = list(Path(conversations_dir).glob("*.json"))
        if not files:
            logger.info("📂 No conversation files found for async ingestion")
            return 0

        # Pre-fetch existing IDs to skip duplicates quickly
        existing_ids: set[str] = set()
        try:
            cur = self.storage.conn.cursor()
            cur.execute("SELECT id FROM conversations")
            existing_ids = {row[0] for row in cur.fetchall()}
        except Exception as dup_exc:
            logger.debug("Could not pre-load existing IDs: %s", dup_exc)

        logger.info(
            "🚀 Async ingestion starting – %s files, max_workers=%s",
            len(files),
            max_workers,
        )

        # Attempt to use orjson if available for speed
        try:
            import orjson as _orjson

            def _json_load(b: bytes):
                return _orjson.loads(b)
        except ModuleNotFoundError:
            def _json_load(b: bytes):
                return _json.loads(b)

        def _load(path: Path):
            try:
                raw_bytes = path.read_bytes()
                raw = _json_load(raw_bytes)
                convo = self._normalize_conversation_json(raw, str(path))
                # Skip known duplicates early
                if convo.get("id") in existing_ids:
                    return None
                # Ensure ID
                if "id" not in convo:
                    convo["id"] = hashlib.md5(path.stem.encode()).hexdigest()[:12]
                return (path, convo)
            except Exception as exc:
                logger.warning("⚠️ Failed to load %s: %s", path, exc)
                return None

        # Phase-1: parallel JSON load / normalisation
        loaded: list[tuple[Path, dict]] = []
        if max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                for fut in as_completed([pool.submit(_load, p) for p in files]):
                    res = fut.result()
                    if res:
                        loaded.append(res)
        else:
            for p in files:
                res = _load(p)
                if res:
                    loaded.append(res)

        # Phase-2: prepare bulk rows + deferred indexing/prompt extraction
        rows: list[tuple] = []
        post_tasks: list[tuple[dict, dict]] = []  # (conversation, raw_convo)
        for path, convo_data in loaded:
            conversation = self.content_processor.prepare_conversation_data(
                convo_data, convo_data["id"]
            )
            rows.append(
                (
                    conversation["id"],
                    conversation["title"],
                    conversation["timestamp"],
                    conversation["captured_at"],
                    conversation["model"],
                    conversation["tags"],
                    conversation.get("summary"),
                    conversation.get("content"),
                    conversation.get("url"),
                    conversation.get("message_count", 0),
                    conversation.get("word_count", 0),
                    datetime.now().isoformat(),
                )
            )
            post_tasks.append((conversation, convo_data))

        # Bulk insert
        inserted = self.storage.conversation_storage.store_conversations_bulk(rows)
        skipped = len(files) - inserted

        # One outer transaction for index + prompt writes
        conn = self.storage.conn
        conn.execute("BEGIN")
        try:
            for conversation, raw_convo in post_tasks:
                self.content_processor.index_conversation_content(conversation["id"], conversation)
                self.prompt_processor.extract_and_store_prompts(conversation["id"], raw_convo)
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error("❌ Index/prompt transaction rolled back: %s", exc)

        logger.info(
            "🏁 Async ingestion finished – %s ingested, %s duplicates skipped",
            inserted,
            skipped,
        )
        return inserted

    # ---------------------------------------------------------------------
    # Template management (exposed at base level so GUI can use it) --------
    # ---------------------------------------------------------------------
    def create_template(self, name: str, template_content: str, description: str = "", category: str = "general") -> int:
        """Create a new Jinja/markdown template and persist it.

        Returns the new template row ID.
        """
        self._ensure_templates_table()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO templates (name, description, template_content, category)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, template_content, category),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_templates(self, category: str | None = None) -> List[Dict[str, Any]]:
        """Return templates, optionally filtered by *category*."""
        self._ensure_templates_table()
        cursor = self.conn.cursor()
        if category:
            cursor.execute("SELECT * FROM templates WHERE category = ? ORDER BY name", (category,))
        else:
            cursor.execute("SELECT * FROM templates ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    # Internal -----------------------------------------------------------------
    def _ensure_templates_table(self):
        """Create the `templates` table the first time it is accessed.

        Many unit-test DBs start empty; we lazily bootstrap the schema to avoid
        import-order headaches.
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    template_content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        except Exception as exc:
            logger.debug("Failed to create templates table: %s", exc)

# LEGACY ADAPTER ==============================================================
# A compatibility layer for the former `MemoryNexus` interface used heavily in
# older tests.  It subclasses `MemoryManager` and implements thin wrappers that
# delegate to the modern storage/processor methods.  The goal is to keep the
# legacy tests green while we gradually migrate external callers.

class MemoryNexus(MemoryManager):
    """Backward-compatibility facade built on top of MemoryManager."""

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------
    def __init__(self, db_path: str = "dreamos_memory.db"):
        super().__init__(db_path)
        self.conn = self.storage.conn  # Convenience alias
        self._ensure_legacy_tables()
        
        # EDIT START SessionLocal-compat
        # Provide a lightweight SessionLocal callable that legacy tests can
        # invoke to obtain an object exposing ``close()``. Internally this
        # delegates to ``MemoryNexus.close()`` so the SQLite handle is
        # released before temp files are deleted on Windows.
        self.SessionLocal = lambda: self
        # EDIT END SessionLocal-compat

    def _ensure_legacy_tables(self):
        """Create legacy tables that are not part of the modern schema."""
        cursor = self.conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT,
                message_index INTEGER,
                word_count INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#007bff',
                description TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversation_tags (
                conversation_id TEXT NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (conversation_id, tag_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                template_content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                usage_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                result_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                template_used TEXT,
                processing_time REAL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            """
        )
        # Insert default artifacts if missing
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value, description) VALUES ('database_version', '1.0', 'Current database schema version')"
        )
        cursor.execute(
            "INSERT OR IGNORE INTO templates (id, name, description, template_content, category, usage_count) VALUES (1, 'Basic Summary', 'Generate a basic summary', 'Summary: {{ conversation.title }}', 'summary', 0)"
        )
        self.conn.commit()
        # Ensure `source` column exists in conversations
        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN source TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

    # ---------------------------------------------------------------------
    # Conversation CRUD -----------------------------------------------------
    # ---------------------------------------------------------------------
    def _generate_convo_id(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(CAST(id AS INTEGER)), 0) + 1 FROM conversations")
        return cursor.fetchone()[0]

    def save_conversation(self, conversation_data: Dict[str, Any]) -> int:
        """Insert or update a conversation. Returns its integer ID."""
        # If a conversation with same URL exists, treat as update
        if conversation_data.get('url'):
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM conversations WHERE url = ?", (conversation_data['url'],))
            existing = cursor.fetchone()
            if existing:
                conversation_data['id'] = existing[0]
        # Assign new ID if still missing
        if 'id' not in conversation_data or conversation_data['id'] is None:
            conversation_data['id'] = self._generate_convo_id()
        # Flatten messages to content/word counts if provided
        msgs = conversation_data.get('messages', [])
        conversation_data['content'] = "\n".join(msg.get('content', '') for msg in msgs)
        conversation_data['message_count'] = len(msgs)
        conversation_data['word_count'] = sum(len(m.get('content', '').split()) for m in msgs)
        self.store_conversation(conversation_data)  # inherited
        # Persist individual messages
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_data['id'],))
            for idx, msg in enumerate(msgs):
                cursor.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, timestamp, message_index, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conversation_data['id'],
                        msg.get('role', 'user'),
                        msg.get('content', ''),
                        (msg.get('timestamp') or datetime.now()).isoformat(),
                        idx,
                        len(msg.get('content', '').split()),
                    ),
                )
            # Update source
            cursor.execute("UPDATE conversations SET source = ? WHERE id = ?", (conversation_data.get('source', 'chatgpt'), conversation_data['id']))
            self.conn.commit()
        except Exception as e:
            logger.warning(f"⚠️ Failed to persist messages for conversation {conversation_data['id']}: {e}")
        return int(conversation_data['id'])

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        convo = self.get_conversation_by_id(conversation_id)
        if convo is None:
            return None
        # Attach messages for legacy callers
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY message_index",
            (conversation_id,),
        )
        convo['messages'] = [dict(row) for row in cursor.fetchall()]
        # Attach tag IDs (legacy expects raw list of ints)
        cursor.execute("SELECT tag_id FROM conversation_tags WHERE conversation_id = ?", (conversation_id,))
        convo['tags'] = [row[0] for row in cursor.fetchall()]
        return convo

    def get_conversations(self, limit: int = 10, source: str = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM conversations"
        params: List[Any] = []
        if source:
            query += " WHERE source = ?"
            params.append(source)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def delete_conversation(self, convo_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (convo_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete conversation {convo_id}: {e}")
            return False

    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = self.storage.search_conversations(query, limit=limit)
        for res in results:
            try:
                res['id'] = int(res['id'])
            except (ValueError, TypeError):
                pass
        return results

    def advanced_search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Run advanced boolean search using the storage layer."""
        results = self.storage.advanced_search(query, limit=limit)
        for res in results:
            try:
                res['id'] = int(res['id'])
            except (ValueError, TypeError):
                pass
        return results

    # ---------------------------------------------------------------------
    # Tag management --------------------------------------------------------
    # ---------------------------------------------------------------------
    def create_tag(self, name: str, color: str = "#007bff", description: str = "") -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tags (name, color, description) VALUES (?, ?, ?) ",
            (name, color, description),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_tags(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY usage_count DESC, name")
        return [dict(row) for row in cursor.fetchall()]

    def add_tag_to_conversation(self, conversation_id: int, tag_id: int):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id) VALUES (?, ?)",
                (conversation_id, tag_id),
            )
            cursor.execute(
                "UPDATE tags SET usage_count = usage_count + 1 WHERE id = ?", (tag_id,)
            )
            self.conn.commit()
        except Exception as e:
            logger.warning(f"⚠️ Failed to add tag {tag_id} to conversation {conversation_id}: {e}")

    def remove_tag_from_conversation(self, conversation_id: int, tag_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM conversation_tags WHERE conversation_id = ? AND tag_id = ?",
            (conversation_id, tag_id),
        )
        self.conn.commit()

    # ---------------------------------------------------------------------
    # Analysis --------------------------------------------------------------
    # ---------------------------------------------------------------------
    def save_analysis_result(self, conversation_id: int, analysis_type: str, result_data: str, template_used: str = None, processing_time: float = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_results (conversation_id, analysis_type, result_data, template_used, processing_time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, analysis_type, json.dumps(result_data), template_used, processing_time),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_analysis_results(self, conversation_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM analysis_results WHERE conversation_id = ?", (conversation_id,))
        results = []
        for row in cursor.fetchall():
            data = dict(row)
            try:
                data['result_data'] = json.loads(data['result_data'])
            except Exception:
                pass
            results.append(data)
        return results

    # ---------------------------------------------------------------------
    # Statistics & utilities --------------------------------------------------
    # ---------------------------------------------------------------------
    def backup_database(self, dst_path: str = None) -> bool:
        try:
            dst_dir = Path(dst_path).parent if dst_path else Path("data/backups")
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_path or str(dst_dir / f"dreamscape_backup_{int(datetime.now().timestamp())}.db")
            copy2(self.storage.db_path, dst)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to backup database: {e}")
            return False

# LEGACY ADAPTER END ==========================================================

def main():
    """Main function for testing."""
    with MemoryManager() as mm:
        # Test ingestion
        count = mm.ingest_conversations()
        print(f"Ingested {count} conversations")
        
        # Test retrieval
        conversations = mm.get_recent_conversations(5)
        print(f"Retrieved {len(conversations)} recent conversations")
        
        # Test stats
        stats = mm.get_conversation_stats()
        print(f"Stats: {stats}")

if __name__ == "__main__":
    main() 