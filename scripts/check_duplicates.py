"""Symbol-level & signature duplicate checker.

Usage:
    python scripts/check_duplicates.py            # human-readable table
    python scripts/check_duplicates.py --json     # JSON output (CI)

Rules:
• Walks the repo (excluding .git, __pycache__, data/, outputs/).  
• Builds SHA-256 of each *.py file **and** Tools DB rows.  
• Flags duplicates where the same hash occurs more than once *across sources*.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

from rich.console import Console
from rich.table import Table

# Lazy import to avoid circular dep in some contexts
def _get_db_rows():
    try:
        from tools_db import connect
        conn = connect()
        return conn.execute("SELECT name, signature FROM tools;").fetchall()
    except Exception:
        return []


EXCLUDE_DIRS = {".git", "__pycache__", "data", "outputs"}
ROOT = Path(__file__).resolve().parents[1]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def gather_hashes() -> Dict[str, List[str]]:
    """Return mapping hash -> list of identifiers."""
    coll: Dict[str, List[str]] = defaultdict(list)

    # On-disk .py files
    for file in ROOT.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in file.parts):
            continue
        code = file.read_text(encoding="utf-8", errors="ignore")
        h = sha256_text(code)
        coll[h].append(str(file.relative_to(ROOT)))

    # DB entries
    for row in _get_db_rows():
        sig = row["signature"] or ""
        if sig:
            coll[sig].append(f"[DB] {row['name']}")
    return coll


def find_duplicates() -> Dict[str, List[str]]:
    coll = gather_hashes()
    return {h: paths for h, paths in coll.items() if len(paths) > 1}


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Detect duplicate source files/signatures")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    dups = find_duplicates()

    if args.json:
        json.dump(dups, sys.stdout, indent=2)
        sys.exit(1 if dups else 0)

    console = Console()
    if not dups:
        console.print("[green]✔ No duplicate code detected.[/green]")
        sys.exit(0)

    table = Table(title="Duplicate Source Detected", show_lines=True)
    table.add_column("SHA-256")
    table.add_column("Occurrences")
    for h, paths in dups.items():
        table.add_row(h[:10] + "…", "\n".join(paths))
    console.print(table)
    sys.exit(1)


if __name__ == "__main__":
    main() 