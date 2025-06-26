#!/usr/bin/env python3
"""
First-Time Discord Bot Setup for Dream.OS
=========================================

Complete guided setup for new users to configure Discord bot integration.
Saves all configuration to .env file for easy reuse.
"""

import json
import os
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print welcome banner."""
    print("=" * 70)
    print("🎮 Welcome to Dream.OS Discord Bot Setup!")
    print("=" * 70)
    print("This script will guide you through setting up your Discord bot")
    print("for the Dream.OS MMORPG platform. All settings will be saved")
    print("to a .env file for easy reuse.")
    print()

def check_prerequisites():
    """Check if Discord.py is installed."""
    print("🔍 Checking Prerequisites...")
    try:
        import discord
        print(f"✅ Discord.py {discord.__version__} is installed")
        return True
    except ImportError:
        print("❌ Discord.py not installed")
        print("Installing Discord.py...")
        os.system("pip install discord.py>=2.0.0")
        try:
            import discord
            print(f"✅ Discord.py {discord.__version__} installed successfully")
            return True
        except ImportError:
            print("❌ Failed to install Discord.py")
            return False

def create_discord_application():
    """Guide user through creating Discord application."""
    print("\n📋 Step 1: Create Discord Application")
    print("-" * 50)
    print("1. Opening Discord Developer Portal...")
    
    # Open Discord Developer Portal
    try:
        webbrowser.open("https://discord.com/developers/applications")
        print("✅ Opened Discord Developer Portal in your browser")
    except:
        print("⚠️  Please manually open: https://discord.com/developers/applications")
    
    print("\n2. In the Developer Portal:")
    print("   • Click 'New Application'")
    print("   • Name it 'Dream.OS Bot' (or your preferred name)")
    print("   • Click 'Create'")
    print("   • Copy the Application ID (you'll see it in General Information)")
    
    application_id = input("\nEnter your Application ID: ").strip()
    
    if not application_id:
        print("❌ Application ID is required")
        return None
    
    return application_id

def setup_discord_bot(application_id):
    """Guide user through bot setup."""
    print(f"\n🤖 Step 2: Setup Bot for Application {application_id}")
    print("-" * 50)
    
    print("1. In your application:")
    print("   • Go to 'Bot' section in the left sidebar")
    print("   • Click 'Add Bot'")
    print("   • Click 'Yes, do it!' to confirm")
    print("   • Copy the Bot Token (click 'Reset Token' if needed)")
    print("   • Enable these options:")
    print("     ✅ Message Content Intent")
    print("     ✅ Server Members Intent")
    print("     ✅ Presence Intent")
    print("   • Click 'Save Changes'")
    
    bot_token = input("\nEnter your Bot Token: ").strip()
    
    if not bot_token:
        print("❌ Bot Token is required")
        return None
    
    return bot_token

def invite_bot_to_server(application_id):
    """Guide user through bot invitation."""
    print(f"\n🔗 Step 3: Invite Bot to Your Server")
    print("-" * 50)
    
    # Generate OAuth2 URL
    oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={application_id}&permissions=2147483648&scope=bot%20applications.commands"
    
    print("1. Opening OAuth2 URL Generator...")
    try:
        webbrowser.open(f"https://discord.com/developers/applications/{application_id}/oauth2/url-generator")
        print("✅ Opened OAuth2 URL Generator in your browser")
    except:
        print("⚠️  Please manually open the OAuth2 URL Generator")
    
    print("\n2. In the OAuth2 URL Generator:")
    print("   • Select scopes: 'bot' and 'applications.commands'")
    print("   • Select permissions:")
    print("     ✅ Send Messages")
    print("     ✅ Use Slash Commands")
    print("     ✅ Embed Links")
    print("     ✅ Read Message History")
    print("   • Copy the generated URL")
    print("   • Open the URL in a new browser tab")
    print("   • Select your server and authorize the bot")
    
    input("\nPress Enter when you've invited the bot to your server...")

def get_server_and_channel_ids():
    """Guide user to get server and channel IDs."""
    print(f"\n📋 Step 4: Get Server and Channel IDs")
    print("-" * 50)
    
    print("1. Enable Developer Mode in Discord:")
    print("   • Open Discord")
    print("   • Go to User Settings → Advanced")
    print("   • Enable 'Developer Mode'")
    
    print("\n2. Get Server ID:")
    print("   • Right-click on your server name")
    print("   • Click 'Copy Server ID'")
    
    guild_id = input("\nEnter your Server ID: ").strip()
    
    if not guild_id:
        print("❌ Server ID is required")
        return None, None
    
    print("\n3. Get Channel ID:")
    print("   • Right-click on the channel where you want the bot to send messages")
    print("   • Click 'Copy Channel ID'")
    
    channel_id = input("\nEnter your Channel ID: ").strip()
    
    if not channel_id:
        print("❌ Channel ID is required")
        return None, None
    
    return guild_id, channel_id

def create_env_file(application_id, bot_token, guild_id, channel_id):
    """Create .env file with all Discord configuration."""
    print(f"\n💾 Step 5: Saving Configuration")
    print("-" * 50)
    
    env_content = f"""# Dream.OS Discord Bot Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Discord Bot Settings
DISCORD_BOT_TOKEN={bot_token}
DISCORD_APPLICATION_ID={application_id}
DISCORD_GUILD_ID={guild_id}
DISCORD_CHANNEL_ID={channel_id}

# Dream.OS Settings
DREAMOS_ENABLED=true
DREAMOS_AUTO_CONNECT=true

# Other environment variables can be added here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with Discord configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def update_discord_config(application_id, bot_token, guild_id, channel_id):
    """Update Discord configuration file."""
    config_path = Path("config/discord_config.json")
    
    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    
    # Update with new values
    config.update({
        'enabled': True,
        'bot_token': bot_token,
        'application_id': application_id,
        'guild_id': guild_id,
        'channel_id': channel_id,
        'prefix': '/',
        'auto_connect': True,
        'features': {
            'dreamscape_updates': True,
            'conversation_sync': True,
            'quest_notifications': True,
            'memory_sharing': True,
            'guild_system': True,
            'trading_system': True
        },
        'notifications': {
            'quest_completions': True,
            'skill_levels': True,
            'domain_conquests': True,
            'system_errors': True,
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            }
        },
        'performance': {
            'max_concurrent_commands': 10,
            'command_timeout': 30,
            'rate_limit_buffer': 5,
            'memory_limit_mb': 100
        },
        'security': {
            'token_environment_variable': 'DISCORD_BOT_TOKEN',
            'validate_permissions': True,
            'log_sensitive_data': False,
            'input_validation': True
        }
    })
    
    try:
        # Ensure config directory exists
        config_path.parent.mkdir(exist_ok=True)
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Updated Discord configuration file")
        return True
    except Exception as e:
        print(f"❌ Failed to update Discord config: {e}")
        return False

def test_connection():
    """Test the Discord bot connection."""
    print(f"\n🧪 Step 6: Testing Connection")
    print("-" * 50)
    
    print("Testing Discord bot connection...")
    
    try:
        from core.discord_manager import DiscordManager
        dm = DiscordManager()
        
        status = dm.get_status()
        print(f"✅ Discord Manager loaded successfully")
        print(f"   Enabled: {status['enabled']}")
        print(f"   Bot Token: {'Set' if status['bot_token'] else 'Not Set'}")
        print(f"   Channel ID: {status['channel_id']}")
        print(f"   MMORPG Engine: {'Available' if status['mmorpg_engine'] else 'Not Available'}")
        
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_startup_script():
    """Create a startup script for easy bot launching."""
    startup_script = """#!/usr/bin/env python3
\"\"\"
Dream.OS Discord Bot Startup Script
==================================

Quick startup script for the Discord bot.
\"\"\"

import os
from pathlib import Path

# Load environment variables
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

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
            print("\\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Discord bot is disabled in configuration")
"""
    
    try:
        with open('start_discord_bot.py', 'w') as f:
            f.write(startup_script)
        print("✅ Created startup script: start_discord_bot.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def print_completion_message():
    """Print completion message with next steps."""
    print(f"\n🎉 Discord Bot Setup Complete!")
    print("=" * 70)
    print("Your Discord bot is now configured and ready to use!")
    print()
    print("📁 Files Created:")
    print("   • .env - Environment variables (keep this secure)")
    print("   • config/discord_config.json - Bot configuration")
    print("   • start_discord_bot.py - Quick startup script")
    print()
    print("🚀 Next Steps:")
    print("   1. Start the bot: python start_discord_bot.py")
    print("   2. Test commands in Discord: /ping")
    print("   3. Start Dream.OS main application")
    print("   4. Enjoy your MMORPG Discord integration!")
    print()
    print("📚 Available Commands:")
    print("   • /ping - Test bot connectivity")
    print("   • /dreamscape status - Show MMORPG status")
    print("   • /quests - Show available quests")
    print("   • /skills - Show player skills")
    print("   • /domains - Show empire domains")
    print("   • /process - Manual processing")
    print("   • /stats - System statistics")
    print()
    print("🔒 Security Note:")
    print("   Keep your .env file secure and never share your bot token!")
    print("   The .env file contains sensitive information.")
    print()

def main():
    """Main setup function."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    # Step 1: Create Discord Application
    application_id = create_discord_application()
    if not application_id:
        return False
    
    # Step 2: Setup Bot
    bot_token = setup_discord_bot(application_id)
    if not bot_token:
        return False
    
    # Step 3: Invite Bot
    invite_bot_to_server(application_id)
    
    # Step 4: Get IDs
    guild_id, channel_id = get_server_and_channel_ids()
    if not guild_id or not channel_id:
        return False
    
    # Step 5: Create .env file
    if not create_env_file(application_id, bot_token, guild_id, channel_id):
        return False
    
    # Step 6: Update Discord config
    if not update_discord_config(application_id, bot_token, guild_id, channel_id):
        return False
    
    # Step 7: Test connection
    if not test_connection():
        print("⚠️  Connection test failed, but setup may still work")
    
    # Step 8: Create startup script
    create_startup_script()
    
    # Step 9: Print completion message
    print_completion_message()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 