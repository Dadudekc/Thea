"""DevLog Panel – create, save, and post devlog updates.

This Qt panel wraps the existing tools.devlog_tool.DevLogTool so users can
compose devlog entries directly from the GUI and instantly push rich embeds to
Discord.  Saved markdown files appear in the list below for quick reference.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QListWidget, QHBoxLayout, QFileDialog
)

from tools.devlog_tool import DevLogTool, DevLogPost


class DevLogPanel(QWidget):
    """Qt panel for devlog authoring and Discord posting."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.tool = DevLogTool()
        self._build_ui()
        self._refresh_list()

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        title_lbl = QLabel("📢 DevLog Updates")
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        root.addWidget(title_lbl)

        # ---- form fields ----
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Title")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Short description")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma-separated)")
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Main update details …")
        self.content_edit.setMinimumHeight(140)

        root.addWidget(self.title_edit)
        root.addWidget(self.desc_edit)
        root.addWidget(self.tags_edit)
        root.addWidget(self.content_edit)

        # ---- action buttons ----
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Locally")
        self.post_btn = QPushButton("🚀 Post to Discord")
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.post_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        # Connect
        self.save_btn.clicked.connect(lambda: self._handle_submit(post_to_discord=False))
        self.post_btn.clicked.connect(lambda: self._handle_submit(post_to_discord=True))

        # ---- list of devlogs ----
        self.list_widget = QListWidget()
        root.addWidget(QLabel("Recent DevLogs:"))
        root.addWidget(self.list_widget, 1)
        self.list_widget.itemDoubleClicked.connect(self._open_selected_file)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _collect_tags(self) -> List[str]:
        text = self.tags_edit.text().strip()
        return [t.strip() for t in text.split(",") if t.strip()] if text else []

    def _handle_submit(self, post_to_discord: bool):
        title = self.title_edit.text().strip()
        desc = self.desc_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        if not (title and desc and content):
            QMessageBox.warning(self, "Validation", "Title, description, and content are required.")
            return

        post = self.tool.create_devlog(
            title=title,
            description=desc,
            content=content,
            tags=self._collect_tags(),
        )

        md_path = self.tool.save_local(post)

        ok = True
        if post_to_discord:
            embed = self.tool._build_embed(post)
            formatted = self.tool.format_for_discord(post)
            try:
                ok = asyncio.run(self.tool.post_to_discord(formatted, embed_data=embed))
            except RuntimeError:
                # running inside existing loop – fallback
                loop = asyncio.get_event_loop()
                ok = loop.create_task(self.tool.post_to_discord(formatted, embed_data=embed))
            except Exception as e:
                ok = False
                QMessageBox.critical(self, "Discord Error", str(e))

        self._refresh_list()
        self._reset_fields()
        msg = "DevLog saved and posted!" if (post_to_discord and ok) else "DevLog saved!"
        QMessageBox.information(self, "Success", msg + f"\nSaved to: {md_path}")

    def _reset_fields(self):
        self.title_edit.clear()
        self.desc_edit.clear()
        self.tags_edit.clear()
        self.content_edit.clear()

    def _refresh_list(self):
        self.list_widget.clear()
        for md_file in sorted(self.tool.output_dir.glob("*.md"), reverse=True):
            self.list_widget.addItem(md_file.name)

    def _open_selected_file(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        path = self.tool.output_dir / item.text()
        if not path.exists():
            QMessageBox.warning(self, "File Missing", "Cannot locate file on disk.")
            self._refresh_list()
            return
        # Ask the user where to open; fallback to default system opener
        QFileDialog.getOpenFileName(self, "Open DevLog", str(path), "Markdown (*.md)") 