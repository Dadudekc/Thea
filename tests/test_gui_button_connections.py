#!/usr/bin/env python3
"""Regression test ensuring all GUI buttons are wired to something.

If a button has no slots connected to its `clicked` signal the test will
fail, serving as an early warning that the UI lost functionality.

Run with `pytest -q tests/test_gui_button_connections.py`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Force Qt to render off-screen so tests work in CI / headless environments
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QPushButton
from gui.main_window import TheaMainWindow


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_all_buttons_have_slots():
    app = _get_app()
    window = TheaMainWindow()

    unconnected: list[str] = []
    for btn in window.findChildren(QPushButton):
        # PyQt6: the bound signal object lives on the class; we access via the instance attribute
        signal = btn.clicked
        if signal is None:
            unconnected.append(btn.text())
        else:
            if btn.receivers(signal) == 0:
                unconnected.append(btn.text())

    # Clean-up the widgets to avoid side-effects for other tests
    window.close()
    if unconnected:
        raise AssertionError(
            "\n".join([
                "The following buttons have no slots connected to their 'clicked' signal:",
                *unconnected,
            ])
        ) 