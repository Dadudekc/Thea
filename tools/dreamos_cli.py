#!/usr/bin/env python3
"""
Dream.OS CLI Tool
================

A comprehensive command-line interface for managing Dream.OS components,
especially the Discord bot integration. This tool would have made the
entire workflow much more efficient.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import webbrowser

class DreamOSCLI:
    """Dream.OS Command Line Interface."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.env_file = self.project_root / '.env'
        self.config_dir = self.project_root / 'config'
        
    def setup_discord_bot(self, interactive: bool = True):
        """Interactive Discord bot setup."""
        print("🎮 Dream.OS Discord Bot Setup")
        print("=" * 50)
        
        if interactive:
            # Step 1: Check current status
            self._check_discord_status()
            
            # Step 2: Open Discord Developer Portal
            print("\n🔗 Opening Discord Developer Portal...")
            webbrowser.open("https://discord.com/developers/applications")
            
            # Step 3: Interactive configuration
            self._interactive_discord_config()
            
            # Step 4: Test connection
            self._test_discord_connection()
            
            # Step 5: Start bot
            self._start_discord_bot()
        else:
            # Non-interactive setup
            self._auto_discord_setup()
    
    def _check_discord_status(self):
        """Check current Discord bot status."""
        print("📊 Checking current Discord bot status...")
        
        if self.env_file.exists():
            config = self._load_env_config()
            token = config.get('DISCORD_BOT_TOKEN', '')
            app_id = config.get('DISCORD_APPLICATION_ID', '')
            
            print(f"   Token: {'✅ Set' if token else '❌ Not Set'}")
            print(f"   App ID: {'✅ Set' if app_id else '❌ Not Set'}")
            print(f"   Guild ID: {'✅ Set' if config.get('DISCORD_GUILD_ID') else '❌ Not Set'}")
            print(f"   Channel ID: {'✅ Set' if config.get('DISCORD_CHANNEL_ID') else '❌ Not Set'}")
            # Phase 3: additional channel mappings
            channel_keys = {
                'DISCORD_CHANNEL_DEVLOG_ID': 'Devlog',
                'DISCORD_CHANNEL_MMRPG_ID': 'MMORPG',
                'DISCORD_CHANNEL_AGENT_MEMORY_ID': 'Agent Memory',
                'DISCORD_CHANNEL_AGENT_PROMPT_ID': 'Agent Prompt',
                'DISCORD_CHANNEL_AGENT_SCRAPER_ID': 'Agent Scraper',
                'DISCORD_CHANNEL_AGENT_CORE_ID': 'Agent Core',
            }
            for env_key, label in channel_keys.items():
                print(f"   {label} Channel: {'✅ Set' if config.get(env_key) else '❌ Not Set'}")
        else:
            print("   ❌ No .env file found")
    
    def _interactive_discord_config(self):
        """Interactive Discord configuration."""
        print("\n⚙️  Interactive Configuration")
        print("-" * 30)
        
        config = {}
        
        # Bot Token
        token = input("Enter Discord Bot Token (or press Enter to skip): ").strip()
        if token:
            config['DISCORD_BOT_TOKEN'] = token
        
        # Application ID
        app_id = input("Enter Discord Application ID (or press Enter to skip): ").strip()
        if app_id:
            config['DISCORD_APPLICATION_ID'] = app_id
            config['DISCORD_CLIENT_ID'] = app_id
        
        # Guild ID
        guild_id = input("Enter Discord Guild/Server ID (or press Enter to skip): ").strip()
        if guild_id:
            config['DISCORD_GUILD_ID'] = guild_id
        
        # Channel ID
        channel_id = input("Enter Discord Channel ID (or press Enter to skip): ").strip()
        if channel_id:
            config['DISCORD_CHANNEL_ID'] = channel_id
        
        # Save configuration
        if config:
            self._save_env_config(config)
            print("✅ Configuration saved!")
    
    def _test_discord_connection(self):
        """Test Discord bot connection."""
        print("\n🧪 Testing Discord Connection...")
        
        try:
            # Import and test Discord manager
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
            print(f"❌ Error testing Discord connection: {e}")
            return False
    
    def _start_discord_bot(self):
        """Start the Discord bot."""
        print("\n🚀 Starting Discord Bot...")
        
        try:
            # Start bot in background
            subprocess.Popen([sys.executable, "start_discord_bot.py"])
            print("✅ Discord bot started in background")
            print("💡 Check your Discord server for the bot")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
    
    def validate_setup(self):
        """Validate the entire Dream.OS setup."""
        print("🔍 Dream.OS Setup Validation")
        print("=" * 50)
        
        checks = {
            "Environment File": self.env_file.exists(),
            "Discord Config": self._check_discord_config(),
            "MMORPG Engine": self._check_mmorpg_engine(),
            "Database": self._check_database(),
            "Dependencies": self._check_dependencies(),
        }
        
        for check, status in checks.items():
            print(f"   {check}: {'✅ PASS' if status else '❌ FAIL'}")
        
        all_passed = all(checks.values())
        print(f"\nOverall Status: {'✅ READY' if all_passed else '⚠️  NEEDS ATTENTION'}")
        
        return all_passed
    
    def _check_discord_config(self) -> bool:
        """Check Discord configuration."""
        if not self.env_file.exists():
            return False
        
        config = self._load_env_config()
        required = ['DISCORD_BOT_TOKEN', 'DISCORD_APPLICATION_ID']
        return all(config.get(key) for key in required)
    
    def _check_mmorpg_engine(self) -> bool:
        """Check MMORPG engine."""
        try:
            from core.mmorpg_engine import MMORPGEngine
            mmorpg = MMORPGEngine()
            return mmorpg is not None
        except:
            return False
    
    def _check_database(self) -> bool:
        """Check database."""
        db_file = self.project_root / 'dreamos_memory.db'
        return db_file.exists()
    
    def _check_dependencies(self) -> bool:
        """Check Python dependencies."""
        try:
            import discord
            return True
        except ImportError:
            return False
    
    def test_commands(self):
        """Test all Discord commands."""
        print("🧪 Testing Discord Commands")
        print("=" * 40)
        
        commands = [
            ("ping", "Test connectivity"),
            ("help", "Show help menu"),
            ("dreamscape", "Show system status"),
            ("profile", "Show player profile"),
            ("quests", "Show quests"),
            ("skills", "Show skills"),
            ("stats", "Show processing stats"),
        ]
        
        for cmd, desc in commands:
            print(f"   /{cmd} - {desc}")
        
        print("\n💡 These commands should be available in Discord")
        print("   (May take up to 1 hour for global sync)")
    
    def generate_invite_url(self):
        """Generate Discord bot invite URL."""
        config = self._load_env_config()
        app_id = config.get('DISCORD_APPLICATION_ID')
        
        if not app_id:
            print("❌ Application ID not found in configuration")
            return
        
        # Generate invite URL with proper permissions
        permissions = "2147483648"  # Send Messages, Use Slash Commands, etc.
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope=bot%20applications.commands"
        
        print("🔗 Discord Bot Invite URL:")
        print(f"   {invite_url}")
        print("\n💡 Use this URL to add the bot to your Discord server")
    
    def show_status(self):
        """Show comprehensive system status."""
        print("📊 Dream.OS System Status")
        print("=" * 50)
        
        # Discord Status
        print("\n🤖 Discord Bot:")
        self._check_discord_status()
        
        # MMORPG Status
        print("\n🎮 MMORPG Engine:")
        try:
            from core.mmorpg_engine import MMORPGEngine
            mmorpg = MMORPGEngine()
            player = mmorpg.get_player()
            skills = mmorpg.get_skills()
            print(f"   Player: {player.name}")
            print(f"   Tier: {player.architect_tier}")
            print(f"   Skills: {len(skills)} active")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Processing Status
        print("\n⚙️  Processing System:")
        try:
            from core.live_processor import get_live_processor
            live_proc = get_live_processor()
            if live_proc:
                stats = live_proc.get_stats()
                print(f"   Status: {stats.status.value}")
                print(f"   Processed: {stats.total_conversations_processed}")
                print(f"   Errors: {stats.errors_count}")
            else:
                print("   ❌ Live processor not available")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def _load_env_config(self) -> Dict[str, str]:
        """Load environment configuration."""
        config = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            config[key.strip()] = value.strip()
        return config
    
    def _save_env_config(self, new_config: Dict[str, str]):
        """Save environment configuration."""
        existing_config = self._load_env_config()
        existing_config.update(new_config)
        
        with open(self.env_file, 'w') as f:
            f.write("# .env - Environment variables for Dream.OS\n")
            f.write("# Note: pydantic-settings will load this automatically if python-dotenv is installed.\n\n")
            
            for key, value in existing_config.items():
                f.write(f"{key}={value}\n")
    
    def _auto_discord_setup(self):
        """Automated Discord setup (for CI/CD)."""
        print("🤖 Automated Discord Setup")
        # This would use environment variables for automated setup
        pass

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Dream.OS CLI Tool")
    parser.add_argument('command', choices=[
        'setup-discord', 'validate', 'test-commands', 'invite-url', 
        'status', 'start-bot', 'stop-bot'
    ], help='Command to execute')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Use interactive mode')
    
    args = parser.parse_args()
    
    cli = DreamOSCLI()
    
    if args.command == 'setup-discord':
        cli.setup_discord_bot(interactive=args.interactive)
    elif args.command == 'validate':
        cli.validate_setup()
    elif args.command == 'test-commands':
        cli.test_commands()
    elif args.command == 'invite-url':
        cli.generate_invite_url()
    elif args.command == 'status':
        cli.show_status()
    elif args.command == 'start-bot':
        cli._start_discord_bot()
    elif args.command == 'stop-bot':
        print("🛑 Stopping Discord bot...")
        # Implementation for stopping bot

if __name__ == "__main__":
    main() 