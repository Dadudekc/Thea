#!/usr/bin/env python3
"""
Discord Bot Setup Script
========================

Interactive script to set up Discord bot configuration.
Helps create bot application, get token, and validate setup.
"""

import json
import os
import sys
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🎮 Discord Bot Setup for Dream.OS")
    print("=" * 60)
    print()

def get_bot_token():
    """Get bot token from user input."""
    print("📋 Step 1: Discord Bot Token")
    print("-" * 40)
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click 'New Application'")
    print("3. Give it a name (e.g., 'Dream.OS Bot')")
    print("4. Go to 'Bot' section")
    print("5. Click 'Add Bot'")
    print("6. Copy the token")
    print()
    
    token = input("Enter your Discord bot token: ").strip()
    
    if not token:
        print("❌ No token provided. Setup cancelled.")
        return None
    
    return token

def get_guild_info():
    """Get guild and channel information."""
    print("\n📋 Step 2: Server & Channel Setup")
    print("-" * 40)
    print("1. Create a test server in Discord")
    print("2. Invite your bot to the server")
    print("3. Get the server ID (right-click server name -> Copy ID)")
    print("4. Get the channel ID (right-click channel -> Copy ID)")
    print()
    
    guild_id = input("Enter server (guild) ID: ").strip()
    channel_id = input("Enter channel ID: ").strip()
    
    return guild_id, channel_id

def validate_config(config):
    """Validate the configuration."""
    print("\n🔍 Step 3: Configuration Validation")
    print("-" * 40)
    
    errors = []
    
    if not config.get('bot_token'):
        errors.append("❌ Bot token is missing")
    else:
        print("✅ Bot token configured")
    
    if not config.get('guild_id'):
        errors.append("❌ Guild ID is missing")
    else:
        print("✅ Guild ID configured")
    
    if not config.get('channel_id'):
        errors.append("❌ Channel ID is missing")
    else:
        print("✅ Channel ID configured")
    
    if errors:
        print("\n❌ Configuration errors found:")
        for error in errors:
            print(f"  {error}")
        return False
    
    print("\n✅ Configuration is valid!")
    return True

def test_discord_import():
    """Test Discord.py import."""
    try:
        import discord
        print(f"✅ Discord.py {discord.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Discord.py: {e}")
        print("Run: pip install discord.py>=2.0.0")
        return False

def save_config(config):
    """Save configuration to file."""
    config_path = Path("config/discord_config.json")
    
    try:
        # Ensure config directory exists
        config_path.parent.mkdir(exist_ok=True)
        
        # Save configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def create_env_example():
    """Create .env.example file with Discord token."""
    env_example = """# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here

# Other environment variables...
"""
    
    try:
        with open(".env.example", 'w') as f:
            f.write(env_example)
        print("✅ Created .env.example file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env.example: {e}")
        return False

def main():
    """Main setup function."""
    print_banner()
    
    # Test Discord.py import
    if not test_discord_import():
        return False
    
    # Load existing config
    config_path = Path("config/discord_config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("📁 Loaded existing configuration")
        except Exception as e:
            print(f"❌ Failed to load existing config: {e}")
            config = {}
    else:
        config = {}
    
    # Get bot token
    token = get_bot_token()
    if not token:
        return False
    
    # Get guild and channel info
    guild_id, channel_id = get_guild_info()
    
    # Update configuration
    config.update({
        'enabled': True,
        'bot_token': token,
        'guild_id': guild_id,
        'channel_id': channel_id,
        'auto_connect': True
    })
    
    # Validate configuration
    if not validate_config(config):
        return False
    
    # Save configuration
    if not save_config(config):
        return False
    
    # Create .env.example
    create_env_example()
    
    print("\n🎉 Discord Bot Setup Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Add your bot token to .env file")
    print("2. Run: python core/discord_manager.py")
    print("3. Test bot connection")
    print("4. Start the main application")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 