"""
Configuration management for Digital Dreamscape standalone project.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Template directory
TEMPLATE_DIR = PROJECT_ROOT / "templates"

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# Logs directory
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [TEMPLATE_DIR, DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "app_name": "Digital Dreamscape",
    "version": "1.0.0",
    "debug": False,
    "log_level": "INFO",
    "template_dir": str(TEMPLATE_DIR),
    "data_dir": str(DATA_DIR),
    "logs_dir": str(LOGS_DIR),
    "chatgpt": {
        "url": "https://chat.openai.com/",
        "timeout": 30,
        "headless": False,
    },
    "scraping": {
        "max_retries": 3,
        "retry_delay": 5,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    },
    "gui": {
        "window_width": 1200,
        "window_height": 800,
        "theme": "default",
    },
}

def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    if os.getenv("DREAMSCAPE_DEBUG"):
        config["debug"] = True
    
    if os.getenv("DREAMSCAPE_LOG_LEVEL"):
        config["log_level"] = os.getenv("DREAMSCAPE_LOG_LEVEL")
    
    return config

def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific configuration setting."""
    config = get_config()
    keys = key.split(".")
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value 