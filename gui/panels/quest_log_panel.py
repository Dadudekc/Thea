from __future__ import annotations

"""Qt-only Quest Log panel (MVP)
Replaces the previous Tkinter-based TaskPanel so the sidebar "Quest Log" button
shows an interactive table to create / update / complete tasks.
"""

from typing import List, Optional
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QComboBox, QLineEdit, QTextEdit, QDateEdit)

from core.mmorpg_engine import MMORPGEngine, Quest
from core.mmorpg_models import Quest as QuestModel


class QuestLogPanel(QWidget):
    """Qt Quest Log panel MVP."""

    tasks_changed = pyqtSignal()

    def __init__(self, engine: MMORPGEngine, parent: QWidget | None = None):
        super().__init__(parent)
        self.engine = engine
        self._build_ui()
        self._refresh()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        header = QLabel("📋 Quest Log")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        root.addWidget(header)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Status", "XP", "Difficulty"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(0, 5):
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        root.addWidget(self.table)

        # Buttons (only complete for now)
        btns = QHBoxLayout()
        self.complete_btn = QPushButton("✓ Complete")
        self.complete_btn.clicked.connect(self._complete_quest)
        btns.addWidget(self.complete_btn)
        btns.addStretch(1)
        root.addLayout(btns)

    # ---------- helpers ----------
    def _set_item(self, row: int, col: int, text: str):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, col, item)

    def _get_selected_quest_id(self) -> Optional[str]:
        if not self.table.selectionModel().hasSelection():
            return None
        row = self.table.selectionModel().selectedRows()[0].row()
        return self.table.item(row, 0).text()

    # ---------- data ops ----------
    def _refresh(self):
        quests: List[QuestModel] = self.engine.get_active_quests() + self.engine.get_quests_by_status("available")
        self.table.setRowCount(len(quests))
        for row, q in enumerate(quests):
            self._set_item(row, 0, q.id)
            self._set_item(row, 1, q.title)
            self._set_item(row, 2, q.status)
            self._set_item(row, 3, str(q.xp_reward))
            self._set_item(row, 4, str(q.difficulty))
        self.tasks_changed.emit()

    # ---------- slots ----------
    def _complete_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        if self.engine.complete_quest(qid):
            QMessageBox.information(self, "Quest", "Quest completed!")
        else:
            QMessageBox.warning(self, "Quest", "Unable to complete quest.")
        self._refresh() 