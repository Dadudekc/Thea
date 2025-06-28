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
    QComboBox, QLineEdit, QTextEdit, QDateEdit, QSpinBox)

from core.mmorpg_engine import MMORPGEngine, Quest
from core.mmorpg_models import Quest as QuestModel, QuestType


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

        # Buttons (expanded CRUD)
        btns = QHBoxLayout()
        self.new_btn = QPushButton("＋ New")
        self.edit_btn = QPushButton("✎ Edit")
        self.delete_btn = QPushButton("🗑 Delete")
        self.complete_btn = QPushButton("✓ Complete")

        self.new_btn.clicked.connect(self._new_quest)
        self.edit_btn.clicked.connect(self._edit_quest)
        self.delete_btn.clicked.connect(self._delete_quest)
        self.complete_btn.clicked.connect(self._complete_quest)

        for b in (self.new_btn, self.edit_btn, self.delete_btn, self.complete_btn):
            btns.addWidget(b)
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

    # ---------- dialogs ----------
    class _QuestDialog(QDialog):
        def __init__(self, parent: QWidget, quest: QuestModel | None = None):
            super().__init__(parent)
            self.setWindowTitle("Quest")
            self.quest = quest
            layout = QFormLayout(self)
            self.title_edit = QLineEdit(quest.title if quest else "")
            self.desc_edit = QTextEdit(quest.description if quest else "")
            self.type_combo = QComboBox()
            for qt in QuestType:
                self.type_combo.addItem(qt.value, qt)
            if quest:
                self.type_combo.setCurrentText(quest.quest_type.value)
            self.diff_spin = QSpinBox()
            self.diff_spin.setRange(1, 10)
            self.diff_spin.setValue(quest.difficulty if quest else 1)
            self.xp_spin = QSpinBox()
            self.xp_spin.setRange(1, 10000)
            self.xp_spin.setValue(quest.xp_reward if quest else 10)

            layout.addRow("Title", self.title_edit)
            layout.addRow("Description", self.desc_edit)
            layout.addRow("Type", self.type_combo)
            layout.addRow("Difficulty", self.diff_spin)
            layout.addRow("XP", self.xp_spin)

            btn_box = QHBoxLayout()
            ok = QPushButton("OK")
            cancel = QPushButton("Cancel")
            ok.clicked.connect(self.accept)
            cancel.clicked.connect(self.reject)
            btn_box.addWidget(ok)
            btn_box.addWidget(cancel)
            layout.addRow(btn_box)

        def data(self):
            qt = self.type_combo.currentData()
            return {
                "title": self.title_edit.text(),
                "description": self.desc_edit.toPlainText(),
                "quest_type": qt,
                "difficulty": self.diff_spin.value(),
                "xp_reward": self.xp_spin.value(),
            }

    def _new_quest(self):
        dlg = self._QuestDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.data()
        import uuid, datetime
        q = QuestModel(
            id=str(uuid.uuid4())[:8],
            created_at=datetime.datetime.now(),
            completed_at=None,
            skill_rewards={},
            status="available",
            conversation_id=None,
            **data,
        )
        self.engine.add_quest(q)
        self._refresh()

    def _edit_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        quest = self.engine.game_state.quests.get(qid)
        if not quest:
            return
        dlg = self._QuestDialog(self, quest)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.engine.update_quest(qid, **dlg.data())
        self._refresh()

    def _delete_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        if QMessageBox.question(self, "Delete Quest", "Permanently delete this quest?") != QMessageBox.StandardButton.Yes:
            return
        self.engine.delete_quest(qid)
        self._refresh()

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