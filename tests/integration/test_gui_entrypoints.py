#!/usr/bin/env python3
"""End-to-end smoke test: GUI entry-points

Validates that Thea's main window can be instantiated in an off-screen
Qt environment and that all primary panels are present in the stacked
widget. This corresponds to the *Beta Release Checklist* item:
  ▸ End-to-end tests pass (`tests/integration/test_gui_entrypoints.py`)

The test deliberately avoids interacting with heavy subsystems (Discord,
LiveProcessor) and focuses on UI construction wiring.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Force Qt to use an off-screen platform so the test runs headless in CI
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Ensure repo root on sys.path so `python -m pytest` anywhere works
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import AFTER setting the Qt platform to avoid side-effects
from gui.main_window import TheaMainWindow  # noqa: E402  pylint: disable=wrong-import-position


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="module")
def main_window():
    """Provide a main window instance for the module, close after tests."""
    app = _get_app()
    window = TheaMainWindow()
    # Do not show() – keep headless
    yield window
    window.close()
    # avoid errors on PyQt6 shutdown
    app.quit()


def test_main_window_starts(main_window):
    """Main window instantiates without raising and has expected attributes."""
    assert main_window.windowTitle()  # default title exists
    # Check a couple of core panels are registered
    expected_panels = {"dashboard", "conversations", "multi_model", "templates"}
    assert expected_panels.issubset(set(main_window.panel_indices))


def test_conversations_panel_loads(main_window):
    """Conversations panel can request data without crashing."""
    conv_panel = main_window.conversations_panel
    # We only check that the method runs – not the DB contents
    conv_panel.load_all_conversations()
    # After loading, rowCount >= 0 (method didn't raise)
    assert conv_panel.conversations_table.rowCount() >= 0 