"""
Settings Panel for Thea GUI
Manages application settings and configuration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict

from .settings.general_settings import GeneralSettingsWidget
from .settings.api_settings import APISettingsWidget
from .settings.memory_settings import MemorySettingsWidget

class SettingsPanel(QWidget):
    """Panel for managing application settings."""
    
    # Signals
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {}
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Settings tabs
        self.create_settings_tabs(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
    
    def create_header(self, parent_layout):
        """Create the header section."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_settings_tabs(self, parent_layout):
        """Create the settings tabs."""
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.general_settings = GeneralSettingsWidget()
        self.general_settings.settings_changed.connect(self._on_settings_changed)
        self.tab_widget.addTab(self.general_settings, "General")
        
        # API settings tab
        self.api_settings = APISettingsWidget()
        self.api_settings.settings_changed.connect(self._on_settings_changed)
        self.tab_widget.addTab(self.api_settings, "API")
        
        # Memory settings tab
        self.memory_settings = MemorySettingsWidget()
        self.memory_settings.settings_changed.connect(self._on_settings_changed)
        self.tab_widget.addTab(self.memory_settings, "Memory")
        
        # Discord settings tab
        self.create_discord_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_discord_tab(self):
        """Create the Discord settings tab."""
        discord_widget = QWidget()
        discord_layout = QVBoxLayout(discord_widget)
        
        # Discord settings group
        discord_group = QWidget()
        discord_group_layout = QVBoxLayout(discord_group)
        
        # Discord configuration
        from PyQt6.QtWidgets import QFormLayout, QGroupBox, QLineEdit, QCheckBox, QPushButton
        
        config_group = QGroupBox("Discord Bot Configuration")
        config_layout = QFormLayout(config_group)
        
        self.discord_token = QLineEdit()
        self.discord_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.discord_token.setPlaceholderText("Enter your Discord bot token")
        config_layout.addRow("Bot Token:", self.discord_token)
        
        self.discord_enabled = QCheckBox("Enable Discord bot")
        self.discord_enabled.setChecked(False)
        config_layout.addRow("Enable bot:", self.discord_enabled)
        
        self.test_discord_btn = QPushButton("Test Connection")
        self.test_discord_btn.clicked.connect(self.test_discord_connection)
        config_layout.addRow("", self.test_discord_btn)
        
        discord_group_layout.addWidget(config_group)
        discord_layout.addWidget(discord_group)
        discord_layout.addStretch()
        
        self.tab_widget.addTab(discord_widget, "Discord")
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons."""
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.reset_btn.setStyleSheet("QPushButton { padding: 8px 16px; }")
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _on_settings_changed(self):
        """Handle settings changes from child widgets."""
        # This could be used to track unsaved changes
        pass
    
    def load_settings(self):
        """Load settings from configuration."""
        # Load default settings
        self.settings = {
            'general': {
                'auto_save': True,
                'auto_refresh': True,
                'refresh_interval': 300,
                'theme': 'Light',
                'font_size': 12
            },
            'api': {
                'openai_key': '',
                'default_model': 'gpt-4o',
                'max_tokens': 2000,
                'chatgpt_username': '',
                'chatgpt_password': '',
                'headless_mode': True
            },
            'memory': {
                'db_path': 'dreamos_memory.db',
                'backup_enabled': True,
                'backup_interval': 7,
                'auto_index': True,
                'chunk_size': 1000,
                'max_chunks': 100
            },
            'discord': {
                'token': '',
                'enabled': False
            }
        }
        
        self.apply_settings_to_ui()
    
    def apply_settings_to_ui(self):
        """Apply loaded settings to UI components."""
        if 'general' in self.settings:
            self.general_settings.set_settings(self.settings['general'])
        if 'api' in self.settings:
            self.api_settings.set_settings(self.settings['api'])
        if 'memory' in self.settings:
            self.memory_settings.set_settings(self.settings['memory'])
        if 'discord' in self.settings:
            self.discord_token.setText(self.settings['discord'].get('token', ''))
            self.discord_enabled.setChecked(self.settings['discord'].get('enabled', False))
    
    def save_settings(self):
        """Save current settings."""
        try:
            # Collect settings from all widgets
            self.settings = {
                'general': self.general_settings.get_settings(),
                'api': self.api_settings.get_settings(),
                'memory': self.memory_settings.get_settings(),
                'discord': {
                    'token': self.discord_token.text(),
                    'enabled': self.discord_enabled.isChecked()
                }
            }
            
            # Emit signal with saved settings
            self.settings_saved.emit(self.settings)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_settings()
    
    def test_discord_connection(self):
        """Test Discord bot connection."""
        token = self.discord_token.text()
        if not token:
            QMessageBox.warning(self, "Warning", "Please enter a Discord bot token first.")
            return
        
        # TODO: Implement actual Discord connection test
        QMessageBox.information(self, "Test Connection", "Discord connection test would be implemented here.")
    
    def get_settings(self) -> Dict:
        """Get current settings."""
        return self.settings 