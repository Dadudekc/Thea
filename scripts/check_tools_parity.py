"""CLI script to validate parity between on-disk tool files and Tools Database.

Exit codes:
0 → parity verified
1 → missing or mismatched tools
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from tools_db import connect, fetch_tool

console = Console()

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"


def sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:  # pragma: no cover
    conn = connect()

    mismatches = []
    missing = []

    for file_path in TOOLS_DIR.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        name = file_path.stem
        on_disk = file_path.read_text(encoding="utf-8")
        row = fetch_tool(conn, name)

        if row is None:
            missing.append(name)
            continue

        if sha256(row["code"]) != sha256(on_disk):
            mismatches.append(name)

    if not missing and not mismatches:
        console.print("[green]✅ Tools parity verified — DB matches on-disk files.[/green]")
        sys.exit(0)

    table = Table(title="Tools Parity Issues")
    table.add_column("Type")
    table.add_column("Name")
    for m in missing:
        table.add_row("Missing", m)
    for m in mismatches:
        table.add_row("Mismatch", m)
    console.print(table)
    sys.exit(1)


if __name__ == "__main__":
    main() 