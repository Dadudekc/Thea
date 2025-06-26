"""
Tools Database
==============

Light-weight package that stores the source code and metadata for reusable CLI tools
inside a standalone SQLite database.  All heavy lifting (connection pooling, schema
creation) is delegated to the existing `core.database_schema_manager.DatabaseSchemaManager`
so we avoid duplicate logic.

This scaffold exposes just enough helpers for Phase 1 ingestion & Phase 2 CLI work:

• `ToolsDatabaseManager` – subclass overriding `create_schema()` for a simple `tools` table.
• `connect()` – convenience wrapper honouring the `TOOLS_DB_PATH` env var.
• `list_tools()` – return all tool names.
• `fetch_tool()` / `load_tool_code()` – basic accessors for later dynamic import.

NOTE: No external dependencies beyond the standard library + existing core module.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import List, Optional

from core.database_schema_manager import DatabaseSchemaManager

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = Path(os.getenv("TOOLS_DB_PATH", "data/tools.db"))

# ---------------------------------------------------------------------------
# Schema Manager
# ---------------------------------------------------------------------------

class ToolsDatabaseManager(DatabaseSchemaManager):
    """Create/verify the schema for the Tools Database."""

    def create_schema(self, connection: sqlite3.Connection):
        """Override default schema with a dedicated `tools` table."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS tools (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            version     INTEGER NOT NULL DEFAULT 1,
            signature   TEXT,
            origin_url  TEXT,
            description TEXT DEFAULT '',
            code        TEXT NOT NULL,
            readme      TEXT,
            added_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, version)
        );
        """
        cursor = connection.cursor()
        cursor.executescript(schema_sql)
        # Migration: ensure new columns exist in case table pre-dates versioning
        existing_cols = {row[1] for row in connection.execute("PRAGMA table_info(tools);").fetchall()}
        alter_stmts = []
        if "version" not in existing_cols:
            alter_stmts.append("ALTER TABLE tools ADD COLUMN version INTEGER DEFAULT 1;")
        if "signature" not in existing_cols:
            alter_stmts.append("ALTER TABLE tools ADD COLUMN signature TEXT;")
        if "origin_url" not in existing_cols:
            alter_stmts.append("ALTER TABLE tools ADD COLUMN origin_url TEXT;")
        if alter_stmts:
            for stmt in alter_stmts:
                connection.execute(stmt)
        connection.commit()

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def connect(db_path: Optional[Path] = None) -> sqlite3.Connection:  # pragma: no cover
    """Return a SQLite connection with schema ensured.

    If the `tools` table is currently empty (fresh DB), automatically ingest
    on-disk tools so parity tests can run without requiring a prior explicit
    `ingest_tools.run()` call.  This keeps the fast path unchanged for existing
    installations while making first-time CI runs idempotent.
    """
    manager = ToolsDatabaseManager()
    conn = manager.init_database(str(db_path or DEFAULT_DB_PATH))

    # EDIT START auto-ingest
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM tools LIMIT 1;")
        if cur.fetchone() is None:  # Empty table ⇒ ingest now
            from tools_db.ingest_tools import _iter_sources  # local import to avoid cycles
            import hashlib, logging as _log

            added = 0
            for name, desc, code, readme in _iter_sources():
                sig = hashlib.sha256(code.encode("utf-8")).hexdigest()
                cur.execute(
                    "INSERT OR IGNORE INTO tools (name, version, signature, description, code, readme) VALUES (?, 1, ?, ?, ?, ?);",
                    (name, sig, desc, code, readme),
                )
                if cur.rowcount:
                    added += 1
            conn.commit()
            if added:
                _log.getLogger(__name__).info("[ToolsDB] Auto-ingested %s tool(s) on first use", added)
    except Exception as e:  # pragma: no cover
        # Failing to auto-ingest should not break consumers; log and proceed.
        import logging as _log
        _log.getLogger(__name__).warning("[ToolsDB] Auto-ingest failed: %s", e)
    # EDIT END auto-ingest

    return conn


def list_tools(conn: sqlite3.Connection) -> List[str]:
    """Return a sorted list of tool names (latest versions only)."""
    rows = conn.execute(
        "SELECT name FROM tools GROUP BY name ORDER BY name ASC;"
    ).fetchall()
    return [row[0] for row in rows]


def fetch_tool(conn: sqlite3.Connection, name: str, version: Optional[int] = None) -> Optional[sqlite3.Row]:
    """Return the latest (or specific) version of a tool."""
    if version is None:
        return conn.execute("SELECT * FROM tools WHERE name = ? ORDER BY version DESC LIMIT 1;", (name,)).fetchone()
    return conn.execute("SELECT * FROM tools WHERE name = ? AND version = ?;", (name, version)).fetchone()


def load_tool_code(conn: sqlite3.Connection, name: str) -> Optional[str]:
    """Return the raw source code for a tool (or None)."""
    row = fetch_tool(conn, name)
    return None if row is None else row["code"] 