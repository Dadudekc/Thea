#!/usr/bin/env python3
"""
Dream.OS Discord Bot Startup Script
==================================

Quick startup script for the Discord bot.
"""

import os
from pathlib import Path

# Load environment variables
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Start the Discord manager
if __name__ == "__main__":
    from core.discord_manager import DiscordManager
    import asyncio
    
    dm = DiscordManager()
    
    if dm.config['enabled']:
        print("🚀 Starting Discord Bot...")
        try:
            asyncio.run(dm.connect())
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Discord bot is disabled in configuration") 