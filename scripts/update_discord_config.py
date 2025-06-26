#!/usr/bin/env python3
"""
Update Discord Configuration
===========================

Manually update Discord configuration with bot token, guild ID, and channel ID.
"""

import json
import sys
from pathlib import Path

def update_config():
    """Update Discord configuration."""
    print("🎮 Discord Configuration Update")
    print("=" * 40)
    
    # Get inputs
    bot_token = input("Enter Bot Token: ").strip()
    guild_id = input("Enter Guild ID (Server ID): ").strip()
    channel_id = input("Enter Channel ID: ").strip()
    
    if not bot_token or not guild_id or not channel_id:
        print("❌ All fields are required")
        return False
    
    # Load existing config
    config_path = Path("config/discord_config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Config file not found")
        return False
    
    # Update config
    config.update({
        'enabled': True,
        'bot_token': bot_token,
        'guild_id': guild_id,
        'channel_id': channel_id,
        'auto_connect': True
    })
    
    # Save config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Configuration updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
        return False

if __name__ == "__main__":
    success = update_config()
    sys.exit(0 if success else 1) 