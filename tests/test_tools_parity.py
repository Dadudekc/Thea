"""Parity test: ensure every on-disk tool file exists in Tools DB with identical source code."""
import hashlib
from pathlib import Path
import sys

from tools_db import connect, fetch_tool

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_tools_parity():
    conn = connect()

    mismatches = []
    missing = []

    for file_path in TOOLS_DIR.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        name = file_path.stem  # matches ingest convention
        on_disk = file_path.read_text(encoding="utf-8")

        row = fetch_tool(conn, name)
        if row is None:
            missing.append(name)
            continue

        if sha256(row["code"]) != sha256(on_disk):
            mismatches.append(name)

    assert not missing, f"{len(missing)} tools missing from DB: {missing}"
    assert not mismatches, f"{len(mismatches)} tools differ between DB and disk: {mismatches}" 