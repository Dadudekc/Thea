#!/usr/bin/env python3
"""
API Settings Panel Component
Handles OpenAI and ChatGPT configuration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QSpinBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

class APISettingsWidget(QWidget):
    """Widget for API configuration settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the API settings UI."""
        layout = QVBoxLayout(self)
        
        # OpenAI settings
        openai_group = QGroupBox("OpenAI Configuration")
        openai_layout = QFormLayout(openai_group)
        
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("Enter your OpenAI API key")
        self.openai_key.textChanged.connect(self._on_setting_changed)
        openai_layout.addRow("API Key:", self.openai_key)
        
        self.default_model = QComboBox()
        self.default_model.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"])
        self.default_model.setCurrentText("gpt-4o")
        self.default_model.currentTextChanged.connect(self._on_setting_changed)
        openai_layout.addRow("Default model:", self.default_model)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 8000)
        self.max_tokens.setValue(2000)
        self.max_tokens.valueChanged.connect(self._on_setting_changed)
        openai_layout.addRow("Max tokens:", self.max_tokens)
        
        layout.addWidget(openai_group)
        
        # ChatGPT settings
        chatgpt_group = QGroupBox("ChatGPT Scraper")
        chatgpt_layout = QFormLayout(chatgpt_group)
        
        self.chatgpt_username = QLineEdit()
        self.chatgpt_username.setPlaceholderText("ChatGPT username/email")
        self.chatgpt_username.textChanged.connect(self._on_setting_changed)
        chatgpt_layout.addRow("Username:", self.chatgpt_username)
        
        self.chatgpt_password = QLineEdit()
        self.chatgpt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.chatgpt_password.setPlaceholderText("ChatGPT password")
        self.chatgpt_password.textChanged.connect(self._on_setting_changed)
        chatgpt_layout.addRow("Password:", self.chatgpt_password)
        
        self.headless_mode = QCheckBox("Run browser in headless mode")
        self.headless_mode.setChecked(True)
        self.headless_mode.toggled.connect(self._on_setting_changed)
        chatgpt_layout.addRow("Headless mode:", self.headless_mode)
        
        layout.addWidget(chatgpt_group)
        layout.addStretch()
    
    def _on_setting_changed(self):
        """Emit signal when settings change."""
        self.settings_changed.emit(self.get_settings())
    
    def get_settings(self) -> dict:
        """Get current API settings."""
        return {
            'openai_key': self.openai_key.text(),
            'default_model': self.default_model.currentText(),
            'max_tokens': self.max_tokens.value(),
            'chatgpt_username': self.chatgpt_username.text(),
            'chatgpt_password': self.chatgpt_password.text(),
            'headless_mode': self.headless_mode.isChecked()
        }
    
    def set_settings(self, settings: dict):
        """Set API settings from dictionary."""
        if 'openai_key' in settings:
            self.openai_key.setText(settings['openai_key'])
        if 'default_model' in settings:
            self.default_model.setCurrentText(settings['default_model'])
        if 'max_tokens' in settings:
            self.max_tokens.setValue(settings['max_tokens'])
        if 'chatgpt_username' in settings:
            self.chatgpt_username.setText(settings['chatgpt_username'])
        if 'chatgpt_password' in settings:
            self.chatgpt_password.setText(settings['chatgpt_password'])
        if 'headless_mode' in settings:
            self.headless_mode.setChecked(settings['headless_mode']) 