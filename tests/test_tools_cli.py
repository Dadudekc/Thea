"""CLI tests for Tools Database integration."""
import sys, pathlib
root_dir = pathlib.Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from pathlib import Path

import subprocess, os

import pytest

from tools_db.ingest_tools import run as ingest_run


@pytest.fixture(scope="module")
def populated_db(tmp_path_factory):
    """Setup a populated tools DB and return its path."""
    db_path = tmp_path_factory.mktemp("tools_db") / "tools.db"
    ingest_run(db_path)
    return str(db_path)


def test_tools_list_cli(populated_db, monkeypatch):
    """Running `python -m tools.dreamos_toolbelt tools list` should succeed."""
    monkeypatch.setenv("TOOLS_DB_PATH", populated_db)

    cmd = [sys.executable, "-m", "tools.dreamos_toolbelt", "tools", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "Available CLI Tools" in result.stdout 