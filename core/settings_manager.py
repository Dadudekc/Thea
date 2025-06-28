#!/usr/bin/env python3
"""
Settings Manager - Handles application settings persistence.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class SettingsManager:
    """Manages application settings with persistence."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.settings_file = self.config_dir / "settings.json"
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        default_settings = {
            "theme": "Dark",
            "auto_save": True,
            "auto_refresh": True,
            "refresh_interval": 300,
            "font_size": 12,
            # Prefer API by default but allow users to switch to 'scraper'
            "prompt_send_method": "api",
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded_settings)
                    return default_settings
            except Exception as e:
                print(f"Warning: Failed to load settings: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save settings: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value and save."""
        self.settings[key] = value
        self._save_settings()
    
    def get_theme(self) -> str:
        """Get the current theme setting."""
        return self.get_setting("theme", "Dark")
    
    def set_theme(self, theme: str):
        """Set the theme and save."""
        self.set_setting("theme", theme)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update multiple settings at once."""
        self.settings.update(new_settings)
        self._save_settings()

# Global settings manager instance
settings_manager = SettingsManager() 