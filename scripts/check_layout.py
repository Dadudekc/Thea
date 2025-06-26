"""Repo layout auditor.

This script enforces Dream.OS directory conventions (see PROJECT_ORGANIZATION_PLAN.md).
It prints a table of unexpected top-level directories or files and exits with
non-zero status if any issues are found.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Set

from rich.table import Table
from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]

# Approved root directories / files (must stay lowercase for comparison)
APPROVED_DIRS: Set[str] = {
    "core",
    "gui",
    "scrapers",
    "tools",
    "tools_db",
    "tests",
    "scripts",
    "docs",
    "demos",
    "data",
    "examples",  # transitional until full migration to demos/
}
APPROVED_FILES: Set[str] = {
    "README.md",
    "requirements.txt",
    "setup.py",
    "CONTRIBUTING.md",
    ".pre-commit-config.yaml",
}


def main() -> None:  # pragma: no cover
    console = Console()
    unexpected = []

    for item in ROOT.iterdir():
        name = item.name
        if item.is_dir():
            if name.lower() not in APPROVED_DIRS and not name.startswith("."):
                unexpected.append(name + "/")
        else:
            if name not in APPROVED_FILES and not name.startswith(".") and not name.endswith(".db"):
                unexpected.append(name)

    if not unexpected:
        console.print("[green]✔ Layout check passed — no unexpected root items.[/green]")
        sys.exit(0)

    table = Table(title="Unexpected root-level items detected")
    table.add_column("Path")
    for path in unexpected:
        table.add_row(path)
    console.print(table)
    console.print("[red]✖ Layout check failed.[/red]")
    sys.exit(1)


if __name__ == "__main__":
    main() 