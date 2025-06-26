"""One-shot migration that converts on-disk tools to DB-backed stubs.

Run this script once after the Tools Database has been fully ingested and
parity verified.  It will:

1. Run the parity checker (aborts on mismatch).
2. For every `tools/*.py` **excluding**:
     • __init__.py (kept)
     • dreamos_toolbelt.py  (left as physical file)
   it replaces the file contents with a tiny stub that lazy-loads the real
   implementation from the Tools Database at import time.
3. Prints a summary of converted files.

You can customise the skip list via `--keep name1,name2`.
"""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from scripts.check_tools_parity import main as check_parity
from tools_db import load_tool_code, connect

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"

DEFAULT_KEEP = {"__init__", "dreamos_toolbelt"}

STUB_TEMPLATE = textwrap.dedent(
    """
    """Auto-generated stub for tool '{name}'.

    The full implementation is stored in the Tools Database.  This stub loads
    the source code on first import so existing `import tools.{name}`
    statements continue to work after on-disk cleanup.
    """

    from __future__ import annotations
    import importlib.util as _util, sys as _sys

    from tools_db import load_tool_code as _load, connect as _connect

    _code = _load(_connect(), "{name}")
    if _code is None:
        raise ImportError(f"Tool '{{__name__}}' not found in Tools DB")

    _spec = _util.spec_from_loader(__name__, loader=None)
    _mod = _util.module_from_spec(_spec)  # type: ignore[arg-type]
    exec(_code, _mod.__dict__)
    _sys.modules[__name__] = _mod

    # Re-export everything at module level for convenience
    globals().update(_mod.__dict__)
    """
)


def do_conversion(keep: set[str]):
    conn = connect()
    converted = []

    for file_path in TOOLS_DIR.glob("*.py"):
        stem = file_path.stem
        if stem in keep:
            continue
        if stem == "__init__":
            continue

        stub_code = STUB_TEMPLATE.format(name=stem)
        file_path.write_text(stub_code, encoding="utf-8")
        converted.append(stem)

    return converted


def main():
    parser = argparse.ArgumentParser(description="Convert tool files to DB stubs")
    parser.add_argument("--keep", help="Comma-separated list of tool names to keep on disk")
    args = parser.parse_args()

    keep = DEFAULT_KEEP.copy()
    if args.keep:
        keep.update(n.strip() for n in args.keep.split(",") if n.strip())

    # Step 1: parity verification
    try:
        check_parity()
    except SystemExit as e:
        if e.code != 0:
            raise SystemExit("Parity check failed — aborting conversion") from None

    # Step 2: replace files with stubs
    converted = do_conversion(keep)

    if converted:
        print(f"✅ Converted {len(converted)} tools → DB stubs: {', '.join(converted)}")
    else:
        print("Nothing converted (maybe all tools in keep list)")


if __name__ == "__main__":
    main() 