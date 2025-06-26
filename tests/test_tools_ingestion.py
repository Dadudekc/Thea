"""Sanity test for Tools Database ingestion.

This verifies that the ingestion script can scan the on-disk `tools/` folder
and populate an SQLite DB with at least one tool entry.
"""
import sys, pathlib
root_dir = pathlib.Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from pathlib import Path

from tools_db import connect, list_tools
from tools_db.ingest_tools import run as ingest_run


def test_ingest_tools(tmp_path: Path):
    """Running ingestion on a temp DB should yield at least one tool record."""
    db_path = tmp_path / "tools.db"

    # Run the ingestion into our temporary file
    ingest_run(db_path)

    conn = connect(db_path)
    names = list_tools(conn)
    assert names, "No tools ingested — expected at least one tool found in tools folder." 