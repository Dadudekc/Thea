#!/usr/bin/env python3
"""
Complete Discord Bot Setup
=========================

Complete the Discord bot setup by configuring guild and channel IDs.
Assumes bot token is already available via environment variable or config.
"""

import json
import os
import sys
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🎮 Complete Discord Bot Setup for Dream.OS")
    print("=" * 60)
    print()

def get_guild_info():
    """Get guild and channel information."""
    print("📋 Server & Channel Setup")
    print("-" * 40)
    print("1. Create a test server in Discord (if you haven't already)")
    print("2. Invite your bot to the server using the OAuth2 URL")
    print("3. Get the server ID (right-click server name -> Copy ID)")
    print("4. Get the channel ID (right-click channel -> Copy ID)")
    print()
    
    guild_id = input("Enter server (guild) ID: ").strip()
    channel_id = input("Enter channel ID: ").strip()
    
    return guild_id, channel_id

def generate_oauth_url():
    """Generate OAuth2 URL for bot invitation."""
    print("\n🔗 Bot Invitation Setup")
    print("-" * 40)
    print("To invite your bot to your server:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Select your application")
    print("3. Go to 'OAuth2' -> 'URL Generator'")
    print("4. Select scopes: 'bot' and 'applications.commands'")
    print("5. Select permissions: 'Send Messages', 'Use Slash Commands', 'Embed Links'")
    print("6. Copy the generated URL and open it in a browser")
    print("7. Select your server and authorize the bot")
    print()

def update_config(guild_id, channel_id):
    """Update the Discord configuration."""
    config_path = Path("config/discord_config.json")
    
    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update with new values
        config.update({
            'enabled': True,
            'guild_id': guild_id,
            'channel_id': channel_id,
            'auto_connect': True
        })
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def test_configuration():
    """Test the configuration."""
    print("\n🔍 Testing Configuration")
    print("-" * 40)
    
    config_path = Path("config/discord_config.json")
    if not config_path.exists():
        print("❌ Configuration file not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"Enabled: {config.get('enabled', False)}")
        print(f"Bot Token: {'Set' if config.get('bot_token') else 'Not Set'}")
        print(f"Guild ID: {config.get('guild_id', 'Not Set')}")
        print(f"Channel ID: {config.get('channel_id', 'Not Set')}")
        
        if config.get('enabled') and config.get('bot_token') and config.get('guild_id') and config.get('channel_id'):
            print("✅ Configuration looks complete!")
            return True
        else:
            print("⚠️  Configuration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    """Main setup function."""
    print_banner()
    
    # Generate OAuth URL instructions
    generate_oauth_url()
    
    # Get guild and channel info
    guild_id, channel_id = get_guild_info()
    
    if not guild_id or not channel_id:
        print("❌ Guild ID and Channel ID are required")
        return False
    
    # Update configuration
    if not update_config(guild_id, channel_id):
        return False
    
    # Test configuration
    if not test_configuration():
        return False
    
    print("\n🎉 Discord Bot Setup Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Make sure your bot is invited to your server")
    print("2. Run: python core/discord_manager.py")
    print("3. Test bot connection")
    print("4. Start the main application")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 