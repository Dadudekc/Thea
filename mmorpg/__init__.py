'''Dreamscape MMORPG package.

This namespace groups game-mechanic helpers that sit on top of the core
`MMORPGEngine` (located in `core.mmorpg_engine`).  Utilities placed here are
intentionally thin wrappers so that the core engine remains framework-agnostic
and testable.
'''

try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError as _PkgNF
    try:
        __version__ = _pkg_version(__name__)
    except _PkgNF:
        __version__ = "0.0.0"
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

"""MMORPG subsystem package (reusable helpers and utilities).""" 