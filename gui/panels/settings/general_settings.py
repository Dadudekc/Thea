#!/usr/bin/env python3
"""
General Settings Panel Component
Handles application and UI settings.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QCheckBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import pyqtSignal
from core.settings_manager import settings_manager

class GeneralSettingsWidget(QWidget):
    """Widget for general application settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_saved_settings()
    
    def init_ui(self):
        """Initialize the general settings UI."""
        layout = QVBoxLayout(self)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        self.auto_save = QCheckBox("Auto-save conversations")
        self.auto_save.toggled.connect(self._on_setting_changed)
        app_layout.addRow("Auto-save:", self.auto_save)
        
        self.auto_refresh = QCheckBox("Auto-refresh data")
        self.auto_refresh.toggled.connect(self._on_setting_changed)
        app_layout.addRow("Auto-refresh:", self.auto_refresh)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(30, 3600)
        self.refresh_interval.setSuffix(" seconds")
        self.refresh_interval.valueChanged.connect(self._on_setting_changed)
        app_layout.addRow("Refresh interval:", self.refresh_interval)
        
        layout.addWidget(app_group)
        
        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        ui_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.valueChanged.connect(self._on_setting_changed)
        ui_layout.addRow("Font size:", self.font_size)
        
        layout.addWidget(ui_group)
        layout.addStretch()
    
    def load_saved_settings(self):
        """Load settings from the settings manager."""
        settings = settings_manager.get_all_settings()
        
        # Set values without triggering signals
        self.auto_save.setChecked(settings.get('auto_save', True))
        self.auto_refresh.setChecked(settings.get('auto_refresh', True))
        self.refresh_interval.setValue(settings.get('refresh_interval', 300))
        self.theme_combo.setCurrentText(settings.get('theme', 'Dark'))
        self.font_size.setValue(settings.get('font_size', 12))
    
    def _on_setting_changed(self):
        """Emit signal when settings change."""
        settings = self.get_settings()
        settings_manager.update_settings(settings)
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> dict:
        """Get current general settings."""
        return {
            'auto_save': self.auto_save.isChecked(),
            'auto_refresh': self.auto_refresh.isChecked(),
            'refresh_interval': self.refresh_interval.value(),
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.value()
        }
    
    def set_settings(self, settings: dict):
        """Set general settings from dictionary."""
        if 'auto_save' in settings:
            self.auto_save.setChecked(settings['auto_save'])
        if 'auto_refresh' in settings:
            self.auto_refresh.setChecked(settings['auto_refresh'])
        if 'refresh_interval' in settings:
            self.refresh_interval.setValue(settings['refresh_interval'])
        if 'theme' in settings:
            self.theme_combo.setCurrentText(settings['theme'])
        if 'font_size' in settings:
            self.font_size.setValue(settings['font_size'])
    
    def _on_theme_changed(self):
        """Handle theme changes specifically."""
        theme = self.theme_combo.currentText()
        settings_manager.set_theme(theme)
        self.theme_changed.emit(theme)
        self._on_setting_changed() 