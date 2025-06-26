#!/usr/bin/env python3
"""
Memory Settings Panel Component
Handles database and indexing configuration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QSpinBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

class MemorySettingsWidget(QWidget):
    """Widget for memory and database settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the memory settings UI."""
        layout = QVBoxLayout(self)
        
        # Database settings
        db_group = QGroupBox("Database Configuration")
        db_layout = QFormLayout(db_group)
        
        self.db_path = QLineEdit()
        self.db_path.setText("dreamos_memory.db")
        self.db_path.textChanged.connect(self._on_setting_changed)
        db_layout.addRow("Database path:", self.db_path)
        
        self.backup_enabled = QCheckBox("Enable automatic backups")
        self.backup_enabled.setChecked(True)
        self.backup_enabled.toggled.connect(self._on_setting_changed)
        db_layout.addRow("Auto-backup:", self.backup_enabled)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setValue(7)
        self.backup_interval.setSuffix(" days")
        self.backup_interval.valueChanged.connect(self._on_setting_changed)
        db_layout.addRow("Backup interval:", self.backup_interval)
        
        layout.addWidget(db_group)
        
        # Indexing settings
        index_group = QGroupBox("Content Indexing")
        index_layout = QFormLayout(index_group)
        
        self.auto_index = QCheckBox("Auto-index new content")
        self.auto_index.setChecked(True)
        self.auto_index.toggled.connect(self._on_setting_changed)
        index_layout.addRow("Auto-index:", self.auto_index)
        
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(100, 2000)
        self.chunk_size.setValue(1000)
        self.chunk_size.setSuffix(" characters")
        self.chunk_size.valueChanged.connect(self._on_setting_changed)
        index_layout.addRow("Chunk size:", self.chunk_size)
        
        self.max_chunks = QSpinBox()
        self.max_chunks.setRange(10, 1000)
        self.max_chunks.setValue(100)
        self.max_chunks.valueChanged.connect(self._on_setting_changed)
        index_layout.addRow("Max chunks:", self.max_chunks)
        
        layout.addWidget(index_group)
        layout.addStretch()
    
    def _on_setting_changed(self):
        """Emit signal when settings change."""
        self.settings_changed.emit(self.get_settings())
    
    def get_settings(self) -> dict:
        """Get current memory settings."""
        return {
            'db_path': self.db_path.text(),
            'backup_enabled': self.backup_enabled.isChecked(),
            'backup_interval': self.backup_interval.value(),
            'auto_index': self.auto_index.isChecked(),
            'chunk_size': self.chunk_size.value(),
            'max_chunks': self.max_chunks.value()
        }
    
    def set_settings(self, settings: dict):
        """Set memory settings from dictionary."""
        if 'db_path' in settings:
            self.db_path.setText(settings['db_path'])
        if 'backup_enabled' in settings:
            self.backup_enabled.setChecked(settings['backup_enabled'])
        if 'backup_interval' in settings:
            self.backup_interval.setValue(settings['backup_interval'])
        if 'auto_index' in settings:
            self.auto_index.setChecked(settings['auto_index'])
        if 'chunk_size' in settings:
            self.chunk_size.setValue(settings['chunk_size'])
        if 'max_chunks' in settings:
            self.max_chunks.setValue(settings['max_chunks']) 