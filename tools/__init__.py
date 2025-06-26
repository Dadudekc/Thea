"""Tools namespace package with dynamic loader.

If a requested submodule does not physically exist on disk, we look up its
source code in the Tools Database and materialise it at import time.
This enables safe deletion of individual tool files while keeping backwards
compatibility for `import tools.<name>` statements.
"""
from __future__ import annotations

import importlib.util
import sys
from types import ModuleType
from typing import List

from tools_db import connect, load_tool_code


__all__: List[str] = []  # Will be extended dynamically


def _materialise(name: str) -> ModuleType | None:
    code = load_tool_code(connect(), name)
    if code is None:
        return None

    module_name = f"{__name__}.{name}"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    exec(code, mod.__dict__)
    sys.modules[module_name] = mod
    __all__.append(name)
    return mod


def __getattr__(attr: str):  # noqa: D401
    """Lazy-load submodules from Tools DB when accessed."""
    mod = _materialise(attr)
    if mod is None:
        raise AttributeError(f"module '{__name__}' has no attribute '{attr}'") from None
    return mod


def __dir__():  # noqa: D401
    return sorted(list(globals().keys()) + __all__) 