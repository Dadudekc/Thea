"""Ingest existing on-disk tools into the Tools Database.

Phase-0 scaffold — provides a callable `run()` function so automated
pipelines or future CLI integrations can execute ingestion without
invoking this file as a script.

Usage (stand-alone):
    python -m tools_db.ingest_tools  # uses default paths

The script scans:
    • tools/*.py                     → core tool modules
    • tools/templates/**            → ancillary Jinja/templates as text
and stores each artifact into the SQLite DB with basic metadata.

NOTE: Advanced features like versioning and README extraction will be
added in Phase 1.  This scaffold is just enough to unblock DB creation
and verify round-trip storage.
"""

from __future__ import annotations

import logging, hashlib
from pathlib import Path
import argparse, sys

from tools_db import connect

logger = logging.getLogger(__name__)

TOOLS_SRC_DIR = Path("tools")
TEMPLATE_SRC_DIR = TOOLS_SRC_DIR / "templates"


def _iter_sources():
    """Yield tuples of (name, description, code, readme) for each tool file."""
    for file_path in TOOLS_SRC_DIR.glob("*.py"):
        if file_path.name == "__init__.py":
            continue  # skip package init stub

        code_text = file_path.read_text(encoding="utf-8")
        # First non-empty line of triple-quoted docstring becomes description
        desc = ""
        lines = code_text.strip().splitlines()
        if lines and lines[0].startswith("\"\"\""):
            desc_lines = []
            for line in lines[1:]:
                if line.startswith("\"\"\""):
                    break
                desc_lines.append(line)
            desc = " ".join(l.strip() for l in desc_lines).strip()
        name = file_path.stem
        yield name, desc, code_text, None  # readme stub

    # Store templates (optional): treat each template as a tool with suffix
    if TEMPLATE_SRC_DIR.exists():
        for tpl in TEMPLATE_SRC_DIR.rglob("*.j2"):
            code_text = tpl.read_text(encoding="utf-8")
            name = tpl.relative_to(TOOLS_SRC_DIR).as_posix()
            desc = "Jinja2 template"
            yield name, desc, code_text, None


def run(db_path=None):  # pragma: no cover
    """Ingest all tools into the database and print a summary."""
    conn = connect(db_path)
    cursor = conn.cursor()

    added, skipped = 0, 0

    for name, desc, code, readme in _iter_sources():
        sig = hashlib.sha256(code.encode("utf-8")).hexdigest()

        latest = cursor.execute(
            "SELECT version, signature FROM tools WHERE name = ? ORDER BY version DESC LIMIT 1;",
            (name,),
        ).fetchone()

        if latest and latest["signature"] == sig:
            skipped += 1  # identical version already stored
            continue

        new_version = 1 if latest is None else (latest["version"] + 1)

        cursor.execute(
            "INSERT INTO tools (name, version, signature, description, code, readme) VALUES (?, ?, ?, ?, ?, ?);",
            (name, new_version, sig, desc, code, readme),
        )
        added += 1

    conn.commit()
    logger.info(f"🗄️  Tools ingestion complete. Added: {added}, Skipped: {skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest on-disk tools into DB")
    parser.add_argument("--db", help="Custom DB path")
    parser.add_argument("--force", action="store_true", help="Force ingest even if unchanged (updates signature)")
    args = parser.parse_args()

    if args.force:
        # Remove existing rows to guarantee fresh insertions
        conn_force = connect(args.db)
        conn_force.execute("DELETE FROM tools;")
        conn_force.commit()
        conn_force.close()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    run(args.db) 