#!/usr/bin/env python3
"""
Discord Bot Setup Wizard
========================

A specialized wizard for setting up Discord bots with minimal user interaction.
This would have made the entire Discord setup process much more efficient.
"""

import asyncio
import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Optional
import requests
import time

class DiscordWizard:
    """Discord Bot Setup Wizard."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.env_file = self.project_root / '.env'
        self.config_file = self.project_root / 'config' / 'discord_config.json'
        
    def run_wizard(self):
        """Run the complete Discord setup wizard."""
        print("🧙‍♂️ Discord Bot Setup Wizard")
        print("=" * 50)
        print("This wizard will guide you through setting up your Discord bot.")
        print("It will open the Discord Developer Portal and help you configure everything.")
        
        # Step 1: Check prerequisites
        if not self._check_prerequisites():
            return False
        
        # Step 2: Create Discord application
        app_data = self._create_discord_application()
        if not app_data:
            return False
        
        # Step 3: Configure bot
        bot_data = self._configure_bot(app_data)
        if not bot_data:
            return False
        
        # Step 4: Set up OAuth2
        oauth_data = self._setup_oauth2(app_data)
        if not oauth_data:
            return False
        
        # Step 5: Save configuration
        self._save_configuration(app_data, bot_data, oauth_data)
        
        # Step 6: Test setup
        self._test_setup()
        
        # Step 7: Generate invite link
        self._generate_invite_link(app_data['id'])
        
        print("\n🎉 Discord Bot Setup Complete!")
        print("Your bot is ready to be added to Discord servers.")
        
        return True
    
    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met."""
        print("\n📋 Checking Prerequisites...")
        
        checks = {
            "Python 3.8+": sys.version_info >= (3, 8),
            "discord.py": self._check_discord_py(),
            "Internet Connection": self._check_internet(),
            "Write Permissions": self._check_write_permissions(),
        }
        
        for check, status in checks.items():
            print(f"   {check}: {'✅ PASS' if status else '❌ FAIL'}")
        
        all_passed = all(checks.values())
        if not all_passed:
            print("\n❌ Some prerequisites are not met.")
            print("Please fix the issues above and try again.")
        
        return all_passed
    
    def _check_discord_py(self) -> bool:
        """Check if discord.py is installed."""
        try:
            import discord
            return True
        except ImportError:
            return False
    
    def _check_internet(self) -> bool:
        """Check internet connectivity."""
        try:
            requests.get("https://discord.com", timeout=5)
            return True
        except:
            return False
    
    def _check_write_permissions(self) -> bool:
        """Check if we can write to the project directory."""
        try:
            test_file = self.project_root / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
            return True
        except:
            return False
    
    def _create_discord_application(self) -> Optional[Dict]:
        """Guide user through creating Discord application."""
        print("\n🔧 Creating Discord Application...")
        
        # Open Discord Developer Portal
        print("Opening Discord Developer Portal...")
        webbrowser.open("https://discord.com/developers/applications")
        
        print("\nPlease follow these steps:")
        print("1. Click 'New Application'")
        print("2. Name it 'Dream.OS Bot' or similar")
        print("3. Click 'Create'")
        print("4. Copy the Application ID from the General Information page")
        
        app_id = input("\nEnter the Application ID: ").strip()
        if not app_id or not app_id.isdigit():
            print("❌ Invalid Application ID")
            return None
        
        return {
            'id': app_id,
            'name': 'Dream.OS Bot',
            'created_at': time.time()
        }
    
    def _configure_bot(self, app_data: Dict) -> Optional[Dict]:
        """Guide user through bot configuration."""
        print("\n🤖 Configuring Bot...")
        
        print("Please follow these steps:")
        print("1. In the left sidebar, click 'Bot'")
        print("2. Click 'Add Bot'")
        print("3. Configure the bot settings:")
        print("   - Username: Dream.OS Bot")
        print("   - Public Bot: OFF")
        print("   - Require OAuth2 Code Grant: OFF")
        print("4. Under 'Privileged Gateway Intents':")
        print("   - Turn ON 'Message Content Intent'")
        print("   - Turn ON 'Server Members Intent'")
        print("   - Turn ON 'Presence Intent'")
        print("5. Click 'Reset Token' and copy the new token")
        
        token = input("\nEnter the Bot Token: ").strip()
        if not token or len(token) < 50:
            print("❌ Invalid Bot Token")
            return None
        
        return {
            'token': token,
            'username': 'Dream.OS Bot',
            'intents': ['message_content', 'server_members', 'presence']
        }
    
    def _setup_oauth2(self, app_data: Dict) -> Optional[Dict]:
        """Guide user through OAuth2 setup."""
        print("\n🔐 Setting up OAuth2...")
        
        print("Please follow these steps:")
        print("1. In the left sidebar, click 'OAuth2'")
        print("2. Click 'URL Generator'")
        print("3. Under 'Scopes', check:")
        print("   - bot")
        print("   - applications.commands")
        print("4. Under 'Bot Permissions', check:")
        print("   - Read Messages/View Channels")
        print("   - Send Messages")
        print("   - Use Slash Commands")
        print("   - Embed Links")
        print("   - Attach Files")
        print("   - Read Message History")
        print("   - Add Reactions")
        print("5. Copy the generated URL")
        
        invite_url = input("\nEnter the Invite URL: ").strip()
        if not invite_url or 'discord.com' not in invite_url:
            print("❌ Invalid Invite URL")
            return None
        
        return {
            'invite_url': invite_url,
            'scopes': ['bot', 'applications.commands'],
            'permissions': '2147483648'
        }
    
    def _save_configuration(self, app_data: Dict, bot_data: Dict, oauth_data: Dict):
        """Save all configuration to files."""
        print("\n💾 Saving Configuration...")
        
        # Save to .env file
        env_content = f"""# Discord Bot Configuration
DISCORD_BOT_TOKEN={bot_data['token']}
DISCORD_APPLICATION_ID={app_data['id']}
DISCORD_CLIENT_ID={app_data['id']}
DISCORD_PUBLIC_KEY=your_public_key_here

# Bot will be enabled by default
DREAMOS_ENABLED=true
"""
        
        # Append to existing .env or create new
        if self.env_file.exists():
            with open(self.env_file, 'a') as f:
                f.write(f"\n# Discord Bot Configuration (Auto-generated)\n")
                f.write(f"DISCORD_BOT_TOKEN={bot_data['token']}\n")
                f.write(f"DISCORD_APPLICATION_ID={app_data['id']}\n")
                f.write(f"DISCORD_CLIENT_ID={app_data['id']}\n")
        else:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
        
        # Update Discord config
        discord_config = {
            "enabled": True,
            "bot_token": bot_data['token'],
            "application_id": app_data['id'],
            "guild_id": "",
            "channel_id": "",
            "prefix": "/",
            "auto_connect": True,
            "features": {
                "dreamscape_updates": True,
                "conversation_sync": True,
                "quest_notifications": True,
                "memory_sharing": True,
                "guild_system": True,
                "trading_system": True
            }
        }
        
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(discord_config, f, indent=2)
        
        print("✅ Configuration saved!")
    
    def _test_setup(self):
        """Test the Discord setup."""
        print("\n🧪 Testing Setup...")
        
        try:
            from core.discord_manager import DiscordManager
            dm = DiscordManager()
            
            if dm.config['enabled'] and dm.config['bot_token']:
                print("✅ Discord manager loaded successfully")
                print("✅ Bot configuration looks good")
                return True
            else:
                print("❌ Discord configuration incomplete")
                return False
                
        except Exception as e:
            print(f"❌ Error testing setup: {e}")
            return False
    
    def _generate_invite_link(self, app_id: str):
        """Generate and display invite link."""
        print("\n🔗 Bot Invite Link:")
        
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions=2147483648&scope=bot%20applications.commands"
        
        print(f"   {invite_url}")
        print("\n💡 Use this link to add your bot to Discord servers")
        print("   The bot will appear offline until you start it")

def main():
    """Main wizard entry point."""
    wizard = DiscordWizard()
    success = wizard.run_wizard()
    
    if success:
        print("\n🎉 Setup complete! You can now:")
        print("1. Use the invite link to add the bot to your server")
        print("2. Run 'python start_discord_bot.py' to start the bot")
        print("3. Test commands like /ping in Discord")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 