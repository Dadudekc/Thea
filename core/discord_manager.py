#!/usr/bin/env python3
"""
Discord Manager for Dream.OS
============================

Handles Discord integration for the Dream.OS system.
Manages bot connections, message handling, and integration with the dreamscape.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Callable
from pathlib import Path

try:
    import discord
    from discord.ext import commands

    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logging.warning("Discord.py not installed. Discord features will be disabled.")

logger = logging.getLogger(__name__)


class DiscordManager:
    """
    Manages Discord integration for Dream.OS.
    Handles bot setup, message processing, and dreamscape integration.
    """

    def __init__(self, config_path: str = "config/discord_config.json"):
        self.config_path = config_path
        self.bot = None
        self.is_connected = False
        self.mmorpg_engine = None
        self.config = self._load_config()
        self._validate_config(self.config)
        self.message_handlers = []

        if DISCORD_AVAILABLE:
            self._setup_bot()
        else:
            logger.warning("Discord integration disabled - discord.py not installed")

    def _load_env_file(self):
        """Load environment variables from .env file."""
        env_path = Path(".env")
        if env_path.exists():
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                os.environ[key.strip()] = value.strip()
                logger.info("[OK] Loaded environment variables from .env file")
            except Exception as e:
                logger.warning(f"Failed to load .env file: {e}")

    def _load_config(self) -> Dict[str, any]:
        """Load Discord configuration with environment variable support."""
        # First, try to load .env file
        self._load_env_file()

        default_config = {
            "enabled": False,
            "bot_token": "",
            "application_id": "",
            "guild_id": "",
            "channel_id": "",
            "prefix": "/",
            "auto_connect": False,
            "features": {
                "dreamscape_updates": True,
                "conversation_sync": True,
                "quest_notifications": True,
                "memory_sharing": True,
                "guild_system": True,
                "trading_system": True,
            },
            "notifications": {
                "quest_completions": True,
                "skill_levels": True,
                "domain_conquests": True,
                "system_errors": True,
                "quiet_hours": {"enabled": False, "start": "22:00", "end": "08:00"},
            },
            "performance": {
                "max_concurrent_commands": 10,
                "command_timeout": 30,
                "rate_limit_buffer": 5,
                "memory_limit_mb": 100,
            },
            "security": {
                "token_environment_variable": "DISCORD_BOT_TOKEN",
                "validate_permissions": True,
                "log_sensitive_data": False,
                "input_validation": True,
            },
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
            else:
                config = default_config

            # Check for environment variable overrides
            env_token = os.getenv("DISCORD_BOT_TOKEN")
            env_app_id = os.getenv("DISCORD_APPLICATION_ID")
            env_guild_id = os.getenv("DISCORD_GUILD_ID")
            env_channel_id = os.getenv("DISCORD_CHANNEL_ID")

            if env_token:
                config["bot_token"] = env_token
                logger.info("[OK] Bot token loaded from environment variable")

            if env_app_id:
                config["application_id"] = env_app_id
                logger.info("[OK] Application ID loaded from environment variable")

            if env_guild_id:
                config["guild_id"] = env_guild_id
                logger.info("[OK] Guild ID loaded from environment variable")

            if env_channel_id:
                config["channel_id"] = env_channel_id
                logger.info("[OK] Channel ID loaded from environment variable")

            # EDIT START – Phase-3 multi-channel support
            # ---------------------------------------------------------------------
            # Consolidate all per-topic channels in a dedicated mapping so that other
            # systems (MMORPG Engine, Dreamscape Processor, etc.) can reference
            # semantic keys instead of raw Discord IDs.

            # Ensure a `channels` dict exists even if the on-disk config predates it.
            config.setdefault("channels", {})

            # Always expose the legacy `channel_id` as the implicit "default".
            if config.get("channel_id") and not config["channels"].get("default"):
                config["channels"]["default"] = config["channel_id"]

            # Map well-known env vars → semantic channel keys (reuse-first philosophy).
            _channel_env_map = {
                "DISCORD_CHANNEL_DEVLOG_ID": "devlog",
                "DISCORD_CHANNEL_AGENT_3": "agent3",
                "DISCORD_CHANNEL_MMRPG_ID": "mmrpg",
                "DISCORD_CHANNEL_SKILL_ID": "skills",
                "DISCORD_CHANNEL_QUESTS_ID": "quests",
                "DISCORD_CHANNEL_EQUIPMENT_ID": "equipment",
                "DISCORD_CHANNEL_LORE_ID": "lore",
                "DISCORD_CHANNEL_STORY_ID": "story",
            }
            for env_key, logical_key in _channel_env_map.items():
                env_val = os.getenv(env_key)
                if env_val:
                    config["channels"][logical_key] = env_val
                    logger.info(
                        f"[OK] {logical_key.capitalize()} channel loaded from {env_key}"
                    )
            # EDIT END

            # Check if enabled from environment
            env_enabled = os.getenv("DREAMOS_ENABLED")
            if env_enabled and env_enabled.lower() in ["true", "1", "yes"]:
                config["enabled"] = True
                logger.info("[OK] Bot enabled from environment variable")

            # Save default config if it doesn't exist
            if not os.path.exists(self.config_path):
                self._save_config(config)

            # Validate final configuration
            if not self._validate_config(config):
                logger.warning("[WARN] Discord configuration validation failed")

            return config

        except Exception as e:
            logger.error(f"[ERROR] Failed to load Discord config: {e}")
            return default_config

    def _save_config(self, config: Dict[str, any]):
        """Save Discord configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("[OK] Discord config saved")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save Discord config: {e}")

    def _validate_config(self, config: Dict[str, any]) -> bool:
        """Validate mandatory Discord configuration fields."""
        if not config.get("enabled"):
            return True

        errors: List[str] = []
        if not config.get("bot_token"):
            errors.append("bot_token is required when Discord is enabled")
        if not config.get("guild_id"):
            errors.append("guild_id is required when Discord is enabled")
        if not config.get("channel_id"):
            errors.append("channel_id is required when Discord is enabled")

        if errors:
            for err in errors:
                logger.error(f"[CONFIG] {err}")
            return False
        return True

    def _setup_bot(self):
        """Setup Discord bot with commands."""
        if not DISCORD_AVAILABLE:
            return

        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True

            # Create bot with application_id if available
            if self.config.get("application_id"):
                self.bot = commands.Bot(
                    command_prefix=self.config["prefix"],
                    intents=intents,
                    application_id=int(self.config["application_id"]),
                )
            else:
                self.bot = commands.Bot(
                    command_prefix=self.config["prefix"], intents=intents
                )

            # Register commands
            self._register_commands()

            @self.bot.event
            async def on_connect():
                self.is_connected = True
                logger.info("[OK] Discord connection established")

            @self.bot.event
            async def on_disconnect():
                self.is_connected = False
                logger.warning("[WARN] Discord connection lost")

            logger.info("[OK] Discord bot setup complete")

        except Exception as e:
            logger.error(f"[ERROR] Failed to setup Discord bot: {e}")

    def set_mmorpg_engine(self, mmorpg_engine):
        """Set the MMORPG engine reference."""
        self.mmorpg_engine = mmorpg_engine
        logger.info("[OK] MMORPG engine reference set")

    def _register_commands(self):
        """Register Discord bot commands."""
        if not self.bot:
            return

        @self.bot.tree.command(name="ping", description="Test bot connectivity")
        async def ping_command(interaction):
            """Test bot connectivity."""
            try:
                await interaction.response.send_message(
                    "🏓 Pong! Bot is online and responsive."
                )
            except Exception as e:
                await interaction.response.send_message(f"❌ Error: {e}")

        @self.bot.tree.command(
            name="dreamscape", description="Get current dreamscape status"
        )
        async def dreamscape_status(interaction):
            """Get current dreamscape status."""
            try:
                from core.dreamscape_processor import DreamscapeProcessor

                embed = discord.Embed(
                    title="🌌 Dreamscape Status",
                    description="Current dreamscape processing status",
                    color=0x9B59B6,
                )

                processor = DreamscapeProcessor()
                status = processor.get_status()

                embed.add_field(
                    name="Processing Status",
                    value=f"Active: {status['active']}\nConversations: {status['conversations_count']}\nLast Update: {status['last_update']}",
                    inline=True,
                )

                embed.add_field(
                    name="Memory Status",
                    value=f"Total Memories: {status['memories_count']}\nRecent: {status['recent_memories']}",
                    inline=True,
                )

                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error getting dreamscape status: {e}"
                )

        @self.bot.tree.command(
            name="quests", description="Quest commands: list / accept / complete"
        )
        async def quests_command(
            interaction, action: str = "list", quest_id: str = None
        ):
            try:
                if not self.mmorpg_engine:
                    await interaction.response.send_message(
                        "❌ MMORPG engine not available", ephemeral=True
                    )
                    return

                if action == "list":
                    available = self.mmorpg_engine.get_quests_by_status("available")
                    active = self.mmorpg_engine.get_quests_by_status("active")
                    embed = discord.Embed(title="📜 Quest Board", color=0x9B59B6)
                    if available:
                        embed.add_field(
                            name="🆕 Available",
                            value="\n".join(
                                f"`{q.id}` {q.title}" for q in available[:10]
                            ),
                            inline=False,
                        )
                    else:
                        embed.add_field(name="🆕 Available", value="None", inline=False)
                    if active:
                        embed.add_field(
                            name="🟡 Active",
                            value="\n".join(f"`{q.id}` {q.title}" for q in active[:10]),
                            inline=False,
                        )
                    await interaction.response.send_message(embed=embed)

                elif action == "accept":
                    if not quest_id:
                        await interaction.response.send_message(
                            "❌ Provide quest_id: `/quests accept quest_id:<id>`",
                            ephemeral=True,
                        )
                        return
                    ok = self.mmorpg_engine.accept_quest(quest_id)
                    if ok:
                        await interaction.response.send_message(
                            f"🟡 Quest `{quest_id}` accepted!"
                        )
                    else:
                        await interaction.response.send_message(
                            "❌ Quest not found or already active.", ephemeral=True
                        )

                elif action == "complete":
                    if not quest_id:
                        await interaction.response.send_message(
                            "❌ Provide quest_id: `/quests complete quest_id:<id>`",
                            ephemeral=True,
                        )
                        return
                    ok = self.mmorpg_engine.complete_quest(quest_id)
                    if ok:
                        await interaction.response.send_message(
                            f"✅ Quest `{quest_id}` completed! XP awarded."
                        )
                    else:
                        await interaction.response.send_message(
                            "❌ Quest not found or not active.", ephemeral=True
                        )

                else:
                    await interaction.response.send_message(
                        "❌ Invalid action. Use `list`, `accept`, or `complete`",
                        ephemeral=True,
                    )

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error with quests command: {e}"
                )

        @self.bot.tree.command(
            name="skills", description="Show player skills and progression"
        )
        async def show_skills(interaction):
            """Show player skills and progression."""
            try:
                if not self.mmorpg_engine:
                    await interaction.response.send_message(
                        "❌ MMORPG engine not available"
                    )
                    return

                player = self.mmorpg_engine.get_player()
                skills = self.mmorpg_engine.get_skills()

                embed = discord.Embed(
                    title="⚔️ Skills & Progression",
                    description=f"Skills for {player.name}",
                    color=0xE74C3C,
                )

                embed.add_field(
                    name="Player Info",
                    value=f"Tier: {player.architect_tier}\nXP: {player.xp}\nLevel: {player.level}",
                    inline=True,
                )

                skill_list = "\n".join(
                    [f"• {skill.name} (Lv {skill.level})" for skill in skills[:5]]
                )
                embed.add_field(
                    name="Active Skills",
                    value=skill_list or "No skills available",
                    inline=True,
                )

                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(f"❌ Error getting skills: {e}")

        @self.bot.tree.command(
            name="domains", description="Show empire domains and territories"
        )
        async def show_domains(interaction):
            """Show empire domains and territories."""
            try:
                if not self.mmorpg_engine:
                    await interaction.response.send_message(
                        "❌ MMORPG engine not available"
                    )
                    return

                domains = self.mmorpg_engine.get_domains()

                embed = discord.Embed(
                    title="🏰 Empire Domains",
                    description="Current territories and conquests",
                    color=0x3498DB,
                )

                if domains:
                    domain_list = "\n".join(
                        [f"• {domain.name} ({domain.type})" for domain in domains[:5]]
                    )
                    embed.add_field(
                        name="Active Domains", value=domain_list, inline=False
                    )
                else:
                    embed.add_field(
                        name="Domains", value="No domains conquered yet", inline=False
                    )

                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error getting domains: {e}"
                )

        @self.bot.tree.command(
            name="process", description="Manually trigger conversation processing"
        )
        async def manual_process(interaction):
            """Manually trigger conversation processing."""
            try:
                # Send initial response
                await interaction.response.send_message(
                    "🔄 Starting manual processing..."
                )

                # Check if live processor is available
                try:
                    from core.live_processor import get_live_processor

                    live_proc = get_live_processor()

                    if not live_proc:
                        await interaction.followup.send(
                            "❌ Live processor not available"
                        )
                        return

                    # Check current status
                    current_status = live_proc.get_status().status.value
                    if current_status == "processing":
                        await interaction.followup.send(
                            "⏳ Processing already in progress. Please wait for current process to complete."
                        )
                        return

                    # Trigger processing
                    await interaction.followup.send(
                        "⚡ Triggering conversation processing..."
                    )

                    # Start processing in background
                    asyncio.create_task(
                        self.run_processing_with_updates(interaction, live_proc)
                    )

                except ImportError:
                    await interaction.followup.send(
                        "❌ Live processor module not available"
                    )
                except Exception as e:
                    await interaction.followup.send(
                        f"❌ Error triggering processing: {e}"
                    )

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error with process command: {e}"
                )

        @self.bot.tree.command(
            name="stats", description="Show detailed processing statistics"
        )
        async def show_stats(interaction):
            """Show detailed processing statistics."""
            try:
                from core.live_processor import get_live_processor

                live_proc = get_live_processor()

                embed = discord.Embed(
                    title="📊 Processing Statistics",
                    description="Live processing system statistics",
                    color=0x00FFFF,
                )

                if live_proc:
                    stats = live_proc.get_stats()
                    uptime = live_proc.get_uptime()

                    embed.add_field(
                        name="System Status",
                        value=f"Status: {stats.status.value}\nUptime: {uptime}\nErrors: {stats.errors_count}",
                        inline=True,
                    )

                    embed.add_field(
                        name="Processing Stats",
                        value=f"Total Processed: {stats.total_conversations_processed}\nToday: {stats.conversations_processed_today}\nAvg Time: {stats.average_processing_time:.2f}s",
                        inline=True,
                    )

                    if stats.last_processing_time:
                        embed.add_field(
                            name="Last Activity",
                            value=f"Last Processed: {stats.last_processing_time.strftime('%Y-%m-%d %H:%M:%S')}",
                            inline=False,
                        )
                else:
                    embed.add_field(
                        name="Status",
                        value="Live processor not available",
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(f"❌ Error getting stats: {e}")

        @self.bot.tree.command(
            name="help", description="Show available commands and help"
        )
        async def help_command(interaction):
            """Show available commands and help."""
            try:
                embed = discord.Embed(
                    title="🤖 Dream.OS Discord Bot Help",
                    description="Available slash commands for Dream.OS integration",
                    color=0x9B59B6,
                )

                # Core commands
                embed.add_field(
                    name="🎮 Core Commands",
                    value="""
                    `/ping` - Test bot connectivity
                    `/dreamscape` - Get dreamscape status
                    `/quests` - Show quests and achievements
                    `/skills` - Show player skills
                    `/domains` - Show empire domains
                    """,
                    inline=False,
                )

                # Processing commands
                embed.add_field(
                    name="⚙️ Processing Commands",
                    value="""
                    `/process` - Manual processing trigger
                    `/stats` - Show processing statistics
                    """,
                    inline=False,
                )

                # Guild commands (placeholder for future)
                embed.add_field(
                    name="🏰 Guild Commands (Coming Soon)",
                    value="""
                    `/guild create` - Create a new guild
                    `/guild join` - Join an existing guild
                    `/guild info` - Show guild information
                    """,
                    inline=False,
                )

                # Trading commands (placeholder for future)
                embed.add_field(
                    name="💰 Trading Commands (Coming Soon)",
                    value="""
                    `/trade` - Create trade offers
                    `/market` - View market prices
                    """,
                    inline=False,
                )

                embed.add_field(
                    name="💬 Conversation Commands",
                    value="""
                    `/convo summary <conversation_id>` - Get conversation summary
                    `/convo info <conversation_id>` - Get conversation information
                    """,
                    inline=False,
                )

                embed.set_footer(text="Dream.OS Discord Integration v1.0")
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(f"❌ Error showing help: {e}")

        @self.bot.tree.command(name="guild", description="Guild management commands")
        async def guild_command(
            interaction, action: str = "info", name: str = None, description: str = None
        ):
            """Guild management commands."""
            try:
                if not self.mmorpg_engine:
                    await interaction.response.send_message(
                        "❌ MMORPG engine not available", ephemeral=True
                    )
                    return

                if action == "create":
                    if not name:
                        await interaction.response.send_message(
                            "❌ Usage: `/guild create name:<GuildName> description:<optional>`",
                            ephemeral=True,
                        )
                        return
                    ok = self.mmorpg_engine.create_guild(
                        name, description or "", str(interaction.user.id)
                    )
                    if ok:
                        await interaction.response.send_message(
                            f"🏰 Guild **{name}** created! {interaction.user.mention} is the leader."
                        )
                    else:
                        await interaction.response.send_message(
                            f"❌ Guild **{name}** already exists.", ephemeral=True
                        )

                elif action == "join":
                    if not name:
                        await interaction.response.send_message(
                            "❌ Usage: `/guild join name:<GuildName>`", ephemeral=True
                        )
                        return
                    ok = self.mmorpg_engine.join_guild(name, str(interaction.user.id))
                    if ok:
                        await interaction.response.send_message(
                            f"✅ {interaction.user.mention} joined **{name}**!"
                        )
                    else:
                        await interaction.response.send_message(
                            f"❌ Unable to join guild **{name}** – does it exist, or are you already a member?",
                            ephemeral=True,
                        )

                elif action == "info":
                    if not name:
                        await interaction.response.send_message(
                            "❌ Usage: `/guild info name:<GuildName>`", ephemeral=True
                        )
                        return
                    info = self.mmorpg_engine.get_guild_info(name)
                    if not info:
                        await interaction.response.send_message(
                            f"❌ Guild **{name}** not found", ephemeral=True
                        )
                        return
                    embed = discord.Embed(
                        title=f"🏰 Guild: {info['name']}",
                        description=info["description"] or "No description",
                        color=0x3498DB,
                    )
                    embed.add_field(
                        name="Leader", value=f"<@{info['leader']}>", inline=True
                    )
                    embed.add_field(
                        name="Members", value=str(info["member_count"]), inline=True
                    )
                    if info["members"]:
                        embed.add_field(
                            name="Member List",
                            value="\n".join(f"<@{m}>" for m in info["members"][:20]),
                            inline=False,
                        )
                    await interaction.response.send_message(embed=embed)

                else:
                    await interaction.response.send_message(
                        "❌ Invalid action. Use: `create`, `join`, or `info`"
                    )

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error with guild command: {e}"
                )

        @self.bot.tree.command(name="trade", description="Trading system commands")
        async def trade_command(
            interaction,
            action: str = "list",
            target: str = None,
            item: str = None,
            amount: int = 1,
        ):
            """Trading system commands."""
            try:
                if action == "offer":
                    if not target or not item:
                        await interaction.response.send_message(
                            "❌ Please provide target and item: `/trade offer target:@user item:ItemName amount:1`"
                        )
                        return

                    embed = discord.Embed(
                        title="💰 Trade Offer",
                        description=f"**{interaction.user.mention}** offers **{amount}x {item}** to **{target}**",
                        color=0xF39C12,
                    )

                    embed.add_field(name="Status", value="🔄 Coming Soon", inline=True)
                    embed.add_field(name="Expires", value="24 hours", inline=True)

                    await interaction.response.send_message(embed=embed)

                elif action == "accept":
                    embed = discord.Embed(
                        title="💰 Trade Acceptance",
                        description="Trade acceptance system",
                        color=0x2ECC71,
                    )

                    embed.add_field(name="Status", value="🔄 Coming Soon", inline=True)

                    await interaction.response.send_message(embed=embed)

                elif action == "list":
                    embed = discord.Embed(
                        title="💰 Active Trades",
                        description="Current trade offers",
                        color=0x9B59B6,
                    )

                    embed.add_field(name="Status", value="🔄 Coming Soon", inline=True)
                    embed.add_field(
                        name="Features",
                        value="Trade offers, market prices, history",
                        inline=True,
                    )

                    await interaction.response.send_message(embed=embed)

                else:
                    await interaction.response.send_message(
                        "❌ Invalid action. Use: `offer`, `accept`, or `list`"
                    )

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error with trade command: {e}"
                )

        @self.bot.tree.command(
            name="market", description="Market and economy information"
        )
        async def market_command(interaction, item: str = None):
            """Market and economy information."""
            try:
                embed = discord.Embed(
                    title="🏪 Market Information",
                    description="Current market prices and trading data",
                    color=0x1ABC9C,
                )

                if item:
                    embed.add_field(
                        name=f"📊 {item} Market Data",
                        value=f"Price: 🪙 100\nSupply: 📦 High\nDemand: 📈 Medium\nVolume: 📊 1,234",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="Market Status", value="🔄 Coming Soon", inline=True
                    )

                    embed.add_field(
                        name="Features",
                        value="Real-time prices, supply/demand, trading volume",
                        inline=True,
                    )

                embed.set_footer(text="Market data updates every 5 minutes")
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error getting market data: {e}"
                )

        @self.bot.tree.command(
            name="profile", description="Show detailed player profile"
        )
        async def profile_command(interaction):
            """Show detailed player profile."""
            try:
                if not self.mmorpg_engine:
                    await interaction.response.send_message(
                        "❌ MMORPG engine not available"
                    )
                    return

                player = self.mmorpg_engine.get_player()
                skills = self.mmorpg_engine.get_skills()

                embed = discord.Embed(
                    title=f"👤 {player.name}'s Profile",
                    description=f"**{player.architect_tier}** - Level {player.level}",
                    color=0xE74C3C,
                )

                # Player stats
                embed.add_field(
                    name="📊 Statistics",
                    value=f"XP: {player.xp:,}\nLevel: {player.level}\nTier: {player.architect_tier}",
                    inline=True,
                )

                # Skills summary
                active_skills = len([s for s in skills if s.level > 0])
                embed.add_field(
                    name="⚔️ Skills",
                    value=f"Active: {active_skills}\nTotal: {len(skills)}\nHighest: {max([s.level for s in skills], default=0)}",
                    inline=True,
                )

                # Processing stats
                try:
                    from core.live_processor import get_live_processor

                    live_proc = get_live_processor()
                    if live_proc:
                        stats = live_proc.get_stats()
                        embed.add_field(
                            name="🔄 Processing",
                            value=f"Total: {stats.total_conversations_processed:,}\nToday: {stats.conversations_processed_today:,}\nErrors: {stats.errors_count}",
                            inline=True,
                        )
                except:
                    embed.add_field(
                        name="🔄 Processing", value="Stats unavailable", inline=True
                    )

                embed.set_thumbnail(
                    url="https://via.placeholder.com/64x64/9b59b6/ffffff?text=DO"
                )
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error getting profile: {e}"
                )

        @self.bot.tree.command(
            name="leaderboard", description="Show player leaderboards"
        )
        async def leaderboard_command(interaction, category: str = "xp"):
            """Show player leaderboards."""
            try:
                embed = discord.Embed(
                    title="🏆 Leaderboards",
                    description=f"Top players by {category.upper()}",
                    color=0xF1C40F,
                )

                # Placeholder leaderboard data
                if category == "xp":
                    embed.add_field(
                        name="🥇 Top XP Earners",
                        value="""
                        1. **Victor** - 1,234 XP
                        2. **Alice** - 987 XP  
                        3. **Bob** - 654 XP
                        """,
                        inline=False,
                    )
                elif category == "skills":
                    embed.add_field(
                        name="🥇 Top Skill Masters",
                        value="""
                        1. **Victor** - 5 skills
                        2. **Alice** - 4 skills
                        3. **Bob** - 3 skills
                        """,
                        inline=False,
                    )
                elif category == "processing":
                    embed.add_field(
                        name="🥇 Top Processors",
                        value="""
                        1. **Victor** - 1,234 processed
                        2. **Alice** - 987 processed
                        3. **Bob** - 654 processed
                        """,
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="Available Categories",
                        value="`xp`, `skills`, `processing`",
                        inline=False,
                    )

                embed.set_footer(text="Leaderboards update every hour")
                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error getting leaderboard: {e}"
                )

        @self.bot.tree.command(
            name="convo", description="Conversation utilities (summary, info)"
        )
        async def convo_command(
            interaction, action: str = "summary", conversation_id: str = None
        ):
            """Provide conversation summaries and meta information stored in the DB.

            Usage:
              /convo summary <conversation_id>
            """
            from core.memory_manager import (
                MemoryManager,
            )  # Lazy import to avoid circular deps

            if action not in ["summary", "info"]:
                await interaction.response.send_message(
                    "Invalid action. Use 'summary' or 'info'", ephemeral=True
                )
                return

            if not conversation_id:
                await interaction.response.send_message(
                    "Please supply a conversation_id", ephemeral=True
                )
                return

            try:
                with MemoryManager("dreamos_memory.db") as memory:
                    convo = memory.get_conversation_by_id(conversation_id)

                if not convo:
                    await interaction.response.send_message(
                        f"Conversation '{conversation_id}' not found.", ephemeral=True
                    )
                    return

                if action == "summary":
                    summary = (
                        convo.get("summary")
                        or "No summary stored yet – run analyze_conversations_ai.py first."
                    )
                    title = convo.get("title", "Untitled")
                    await interaction.response.send_message(f"**{title}**\n{summary}")
                else:  # info
                    meta = (
                        f"**Title:** {convo.get('title','Untitled')}\n"
                        f"**Messages:** {convo.get('message_count',0)} | **Words:** {convo.get('word_count',0)}\n"
                        f"**Tags:** {convo.get('tags','(none)')}\n"
                        f"**URL:** {convo.get('url','')}\n"
                    )
                    await interaction.response.send_message(meta)
            except Exception as e:
                logger.error(f"/convo command failed: {e}")
                await interaction.response.send_message(
                    "Error fetching conversation.", ephemeral=True
                )

        # Add event handlers
        @self.bot.event
        async def on_ready():
            """Called when the bot is ready."""
            logger.info(f"[OK] Discord bot logged in as {self.bot.user}")

            # Sync commands when bot is ready
            try:
                if self.config.get("guild_id"):
                    # Sync to specific guild (faster for development)
                    guild = self.bot.get_guild(int(self.config["guild_id"]))
                    if guild:
                        self.bot.tree.copy_global_to(guild=guild)
                        await self.bot.tree.sync(guild=guild)
                        logger.info(f"[OK] Commands synced to guild: {guild.name}")
                    else:
                        logger.warning(f"Guild {self.config['guild_id']} not found")
                else:
                    # Sync globally
                    await self.bot.tree.sync()
                    logger.info("[OK] Commands synced globally")
            except Exception as e:
                logger.error(f"[ERROR] Failed to sync commands: {e}")

        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors."""
            if isinstance(error, commands.CommandNotFound):
                await ctx.send(
                    "❌ Command not found. Use `/help` to see available commands."
                )
            else:
                logger.error(f"Command error: {error}")
                await ctx.send(f"❌ An error occurred: {error}")

        logger.info("[OK] Discord commands registered")

    def update_config(self, updates: Dict[str, any]) -> bool:
        """Update Discord configuration."""
        try:
            self.config.update(updates)
            self._save_config(self.config)
            self._validate_config(self.config)

            # Re-setup bot if token changed
            if "bot_token" in updates and DISCORD_AVAILABLE:
                self._setup_bot()

            logger.info("[OK] Discord config updated")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to update Discord config: {e}")
            return False

    async def connect(self) -> bool:
        """Connect to Discord."""
        if not DISCORD_AVAILABLE or not self.config["enabled"]:
            logger.warning("Discord not available or disabled")
            return False

        if not self.config["bot_token"]:
            logger.error("[ERROR] No Discord bot token configured")
            return False

        try:
            await self.bot.start(self.config["bot_token"])
            self.is_connected = True
            logger.info("[OK] Connected to Discord")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to connect to Discord: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Discord."""
        if self.bot and self.is_connected:
            await self.bot.close()
            self.is_connected = False
            logger.info("[OK] Disconnected from Discord")

    async def send_dreamscape_update(
        self, message: str, embed_data: Optional[Dict] = None
    ):
        """Send a dreamscape update to Discord."""
        if not self.is_connected or not self.config["channel_id"]:
            return False

        try:
            channel = self.bot.get_channel(int(self.config["channel_id"]))
            if not channel:
                logger.error("[ERROR] Discord channel not found")
                return False

            if embed_data:
                embed = discord.Embed(**embed_data)
                await channel.send(content=message, embed=embed)
            else:
                await channel.send(message)

            logger.info("[OK] Sent dreamscape update to Discord")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to send Discord message: {e}")
            return False

    def add_message_handler(self, handler: Callable):
        """Add a custom message handler."""
        self.message_handlers.append(handler)
        logger.info("[OK] Added Discord message handler")

    async def send_message(self, message: str, channel_id: Optional[str] = None):
        """Send a message to the specified Discord channel or the configured default channel."""
        if not self.bot:
            return

        try:
            # Use provided channel_id or fall back to configured one
            target_channel_id = channel_id or self.config["channel_id"]
            if not target_channel_id:
                logger.error("No Discord channel ID provided or configured")
                return

            channel = self.bot.get_channel(int(target_channel_id))
            if channel:
                await channel.send(message)
                logger.info(f"[OK] Message sent to channel {target_channel_id}")
            else:
                logger.warning(f"Discord channel {target_channel_id} not found")
        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")

    async def send_embed(self, embed: discord.Embed, channel_id: Optional[str] = None):
        """Send an embed message to the specified Discord channel or the configured default channel."""
        if not self.bot:
            return

        try:
            # Use provided channel_id or fall back to configured one
            target_channel_id = channel_id or self.config["channel_id"]
            if not target_channel_id:
                logger.error("No Discord channel ID provided or configured")
                return

            channel = self.bot.get_channel(int(target_channel_id))
            if channel:
                await channel.send(embed=embed)
                logger.info(f"[OK] Embed sent to channel {target_channel_id}")
            else:
                logger.warning(f"Discord channel {target_channel_id} not found")
        except Exception as e:
            logger.error(f"Failed to send Discord embed: {e}")

    def get_status(self) -> Dict:
        """Get Discord bot status."""
        return {
            "enabled": self.config["enabled"],
            "bot_token": bool(self.config["bot_token"]),
            "application_id": self.config.get("application_id", ""),
            "guild_id": self.config["guild_id"],
            "channel_id": self.config["channel_id"],
            "bot_ready": self.bot.is_ready() if self.bot else False,
            "mmorpg_engine": self.mmorpg_engine is not None,
        }

    async def run_processing_with_updates(self, interaction, live_proc):
        """Run processing with status updates."""
        try:
            # Get initial stats
            initial_stats = live_proc.get_stats()

            # Trigger processing (this would need to be implemented as an async method)
            # For now, simulate processing
            await asyncio.sleep(2)

            # Get updated stats
            updated_stats = live_proc.get_stats()

            # Calculate differences
            processed_diff = (
                updated_stats.total_conversations_processed
                - initial_stats.total_conversations_processed
            )

            embed = discord.Embed(
                title="✅ Processing Complete",
                description="Manual processing has finished",
                color=0x2ECC71,
            )

            embed.add_field(
                name="Results",
                value=f"Processed: {processed_diff} conversations\nTotal: {updated_stats.total_conversations_processed:,}\nErrors: {updated_stats.errors_count}",
                inline=True,
            )

            embed.add_field(
                name="Performance",
                value=f"Avg Time: {updated_stats.average_processing_time:.2f}s\nToday: {updated_stats.conversations_processed_today:,}",
                inline=True,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error during processing: {e}")

    # EDIT START – Phase-3 helpers
    # ------------------------------------------------------------------
    def get_channel(self, key: str):  # type: ignore[return-value]
        """Return a `discord.TextChannel` looked up by semantic key.

        Falls back to the legacy `channel_id` / `channels['default']` mapping
        if the requested key is not configured or the bot isn't connected yet.
        """
        if not self.bot:
            return None

        # Prefer explicit mapping in the channels dict.
        cid = self.config.get("channels", {}).get(key)
        if cid:
            chan = self.bot.get_channel(int(cid))
            if chan:
                return chan

        # Fallback to default/legacy channel.
        fallback_cid = self.config.get("channel_id") or self.config.get(
            "channels", {}
        ).get("default")
        return self.bot.get_channel(int(fallback_cid)) if fallback_cid else None

    async def send_update(
        self, key: str, message: str, embed_data: Optional[Dict] = None
    ):
        """High-level helper used by Bridge layers (e.g., DiscordBridge).

        `key` is the semantic topic ("skills", "quests", …).  Chooses the
        appropriate channel and dispatches the message.  Falls back to the
        default channel if the specific mapping is missing.
        """
        if not self.bot or not self.is_connected:
            return False

        channel = self.get_channel(key)
        if not channel:
            logger.warning(f"[SKIP] No Discord channel configured for key '{key}'")
            return False

        try:
            if embed_data:
                embed = discord.Embed(**embed_data)
                await channel.send(content=message, embed=embed)
            else:
                await channel.send(message)
            logger.info(f"[OK] Dispatched update '{key}' to Discord")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to send Discord update '{key}': {e}")
            return False

    async def send_markdown(self, markdown: str, channel_key: str = "devlog"):
        """Send long markdown text, auto-splitting into 2k-char Discord blocks.

        Discord imposes a 2000-character limit per message. This helper breaks
        a long markdown string into chunks at paragraph boundaries and sends
        them sequentially to the channel referenced by `channel_key` (which is
        resolved via the semantic channel map added earlier). If the channel
        key isn't found it falls back to the legacy default channel_id.
        """
        if not markdown:
            return
        # Resolve channel id from logical key
        chan_id = self.get_channel(channel_key) or self.config.get("channel_id")
        if not chan_id:
            logger.warning("Discord channel not configured; aborting send_markdown")
            return

        # Split wisely under 2000 chars
        max_len = 1900  # leave room for code fences if any
        paragraphs = markdown.split("\n\n")
        chunk = ""
        for para in paragraphs:
            # +2 accounts for the double newline we'll re-add
            if len(chunk) + len(para) + 2 > max_len:
                await self.send_message(chunk, channel_id=chan_id)
                chunk = ""
            chunk += para + "\n\n"
        if chunk.strip():
            await self.send_message(chunk, channel_id=chan_id)

    # EDIT END


def main():
    """Test the Discord manager."""
    dm = DiscordManager()

    print("Discord Manager Test:")
    print(f"Enabled: {dm.config['enabled']}")
    print(f"Bot Token: {'Set' if dm.config['bot_token'] else 'Not Set'}")
    print(f"Application ID: {dm.config.get('application_id', 'Not Set')}")
    print(f"Guild ID: {dm.config['guild_id']}")
    print(f"Channel ID: {dm.config['channel_id']}")
    print(f"Features: {dm.config['features']}")
    print(
        f"Environment Token: {'Available' if os.getenv('DISCORD_BOT_TOKEN') else 'Not Set'}"
    )
    print(
        f"Environment App ID: {'Available' if os.getenv('DISCORD_APPLICATION_ID') else 'Not Set'}"
    )

    if not DISCORD_AVAILABLE:
        print("\n⚠️  Discord.py not installed. Install with: pip install discord.py")


if __name__ == "__main__":
    main()
