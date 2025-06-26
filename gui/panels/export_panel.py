from __future__ import annotations
"""Simple Export Center panel (MVP).
Provides buttons to export conversations (CSV) and dreamscape memory (JSON).
"""
from pathlib import Path
import csv
import json
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.memory_api import MemoryAPI
from core.dreamscape_memory import DreamscapeMemory


class ExportPanel(QWidget):
    """Export Center MVP."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.memory_api = MemoryAPI()
        self.dreamscape_mem = DreamscapeMemory()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("📤 Export Center")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        root.addWidget(title)

        btn_row = QHBoxLayout()
        conv_btn = QPushButton("Export Conversations → CSV")
        conv_btn.clicked.connect(self._export_conversations)
        mem_btn = QPushButton("Export Dreamscape → JSON")
        mem_btn.clicked.connect(self._export_memory)
        btn_row.addWidget(conv_btn)
        btn_row.addWidget(mem_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        info = QLabel("Choose a destination file when prompted. Large exports may take a few seconds.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.addWidget(info)

    # ---------- helpers ----------
    def _export_conversations(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Conversations CSV", "conversations.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            convs: List[dict] = self.memory_api.get_conversations(limit=None, offset=0)
            with open(Path(path), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "title", "source", "message_count", "word_count", "model", "created_at"])
                writer.writeheader()
                writer.writerows(convs)
            QMessageBox.information(self, "Export Complete", f"Saved {len(convs)} conversations to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _export_memory(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Dreamscape JSON", "dreamscape_memory.json", "JSON Files (*.json)")
        if not path:
            return
        try:
            data = self.dreamscape_mem.get_full_memory()
            with open(Path(path), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Export Complete", f"Dreamscape memory saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e)) 