"""
Discord Quest Commands for Dream.OS

Provides Discord commands for tracking quests, viewing character progress,
and managing rewards. Integrates with the infinite progression system.
"""

import discord
from discord.ext import commands
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from .infinite_progression import InfiniteProgressionSystem
from .conversation_flow_manager import ConversationFlowManager

class QuestCommands(commands.Cog):
    def __init__(self, bot, progression_system: InfiniteProgressionSystem, flow_manager: ConversationFlowManager):
        self.bot = bot
        self.progression = progression_system
        self.flow_manager = flow_manager

    @commands.command(name='quests')
    async def view_active_quests(self, ctx):
        """View all your active quests."""
        player_id = str(ctx.author.id)
        active_quests = self.flow_manager.get_active_quests(player_id)

        if not active_quests:
            await ctx.send("You don't have any active quests! Use `!startquest` to begin a new adventure.")
            return

        # Create embeds for each quest
        embeds = []
        for quest in active_quests:
            embed = self.progression.create_discord_quest_embed({
                'id': quest.id,
                'title': quest.title,
                'description': quest.description,
                'progress': len(quest.checkpoints) / len(quest.objectives),
                'rewards': [str(reward) for reward in quest.rewards.__dict__.items()],
                'requirements': [obj['description'] for obj in quest.objectives],
                'difficulty': quest.difficulty,
                'rarity': self._get_quest_rarity(quest.difficulty),
                'started_at': quest.started_at
            })
            embeds.append(discord.Embed.from_dict(embed))

        # Send embeds (Discord limits to 10 embeds per message)
        for i in range(0, len(embeds), 10):
            await ctx.send(embeds=embeds[i:i+10])

    @commands.command(name='character')
    async def view_character(self, ctx):
        """View your character's stats, equipment, and titles."""
        player_id = str(ctx.author.id)
        character = self.progression.characters.get(player_id)

        if not character:
            await ctx.send("You haven't created a character yet! Use `!createcharacter` to begin your journey.")
            return

        # Create character overview embed
        embed = discord.Embed(
            title=f"📊 {character.name}'s Profile",
            description=f"Active Title: {character.active_title or 'None'}",
            color=0x00ff00
        )

        # Add stats
        stats_text = "\n".join(f"**{stat}:** {value}" for stat, value in character.stats.items())
        embed.add_field(name="📈 Stats", value=stats_text or "No stats yet", inline=False)

        # Add equipment
        equipment_text = "\n".join(
            f"**{slot}:** {item.name} ({item.rarity})" 
            for slot, item in character.equipment.items()
        )
        embed.add_field(name="🎮 Equipment", value=equipment_text or "No equipment", inline=False)

        # Add active abilities
        abilities_text = "\n".join(
            f"• {ability}" for ability in character.active_abilities
        )
        embed.add_field(name="⚡ Active Abilities", value=abilities_text or "No active abilities", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='titles')
    async def view_titles(self, ctx):
        """View all your earned titles."""
        player_id = str(ctx.author.id)
        character = self.progression.characters.get(player_id)

        if not character or not character.titles:
            await ctx.send("You haven't earned any titles yet! Complete quests to earn titles.")
            return

        # Create titles embed
        embed = discord.Embed(
            title="🏆 Your Titles",
            description="All titles you've earned on your journey",
            color=0xffd700
        )

        for title in character.titles:
            effects = "\n".join(f"• {effect}" for effect in title.bonus_effects)
            embed.add_field(
                name=f"{title.name} ({title.rarity})",
                value=f"{title.description}\n\n**Effects:**\n{effects}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='equipment')
    async def view_equipment(self, ctx, slot: Optional[str] = None):
        """View your equipped items or details about a specific slot."""
        player_id = str(ctx.author.id)
        character = self.progression.characters.get(player_id)

        if not character:
            await ctx.send("You haven't created a character yet!")
            return

        if slot:
            # View specific slot
            item = character.equipment.get(slot)
            if not item:
                await ctx.send(f"Nothing equipped in {slot}!")
                return

            embed = self._create_equipment_embed(item)
            await ctx.send(embed=embed)
        else:
            # Overview of all equipment
            embed = discord.Embed(
                title="🎮 Equipment Overview",
                description="Your currently equipped items",
                color=0x00ff00
            )

            for slot, item in character.equipment.items():
                if item:
                    stats = ", ".join(f"{k}: {v}" for k, v in item.stats.items())
                    embed.add_field(
                        name=f"{slot.replace('_', ' ').title()}: {item.name}",
                        value=f"Rarity: {item.rarity}\nStats: {stats}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=slot.replace('_', ' ').title(),
                        value="Empty",
                        inline=True
                    )

            await ctx.send(embed=embed)

    @commands.command(name='abilities')
    async def view_abilities(self, ctx):
        """View your learned abilities."""
        player_id = str(ctx.author.id)
        character = self.progression.characters.get(player_id)

        if not character or not character.abilities:
            await ctx.send("You haven't learned any abilities yet!")
            return

        embed = discord.Embed(
            title="⚡ Abilities",
            description="Your learned abilities",
            color=0x00ffff
        )

        for ability in character.abilities:
            effects = "\n".join(f"• {effect['type']}: {effect['value']}" for effect in ability.effects)
            embed.add_field(
                name=f"{ability.name} ({ability.type})",
                value=f"{ability.description}\n\nCooldown: {ability.cooldown}s\n**Effects:**\n{effects}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='questlog')
    async def view_quest_log(self, ctx, quest_id: Optional[str] = None):
        """View your quest log or details about a specific quest."""
        player_id = str(ctx.author.id)
        
        if quest_id:
            # View specific quest
            quest = self.flow_manager.get_quest(quest_id)
            if not quest or quest.player_id != player_id:
                await ctx.send("Quest not found!")
                return

            embed = self.progression.create_discord_quest_embed({
                'id': quest.id,
                'title': quest.title,
                'description': quest.description,
                'progress': len(quest.checkpoints) / len(quest.objectives),
                'rewards': [str(reward) for reward in quest.rewards.__dict__.items()],
                'requirements': [obj['description'] for obj in quest.objectives],
                'difficulty': quest.difficulty,
                'rarity': self._get_quest_rarity(quest.difficulty),
                'started_at': quest.started_at
            })
            
            # Add checkpoints
            checkpoint_text = "\n".join(
                f"[{cp['timestamp'].strftime('%Y-%m-%d %H:%M')}] {cp['update']}"
                for cp in quest.checkpoints[-5:]  # Show last 5 checkpoints
            )
            embed['fields'].append({
                'name': '📝 Recent Progress',
                'value': checkpoint_text or "No progress recorded yet",
                'inline': False
            })

            await ctx.send(embed=discord.Embed.from_dict(embed))
        else:
            # Overview of all quests
            completed_quests = self.flow_manager.get_completed_quests(player_id)
            active_quests = self.flow_manager.get_active_quests(player_id)

            embed = discord.Embed(
                title="📚 Quest Log",
                description=f"Active Quests: {len(active_quests)}\nCompleted Quests: {len(completed_quests)}",
                color=0x00ff00
            )

            # Show active quests
            active_text = "\n".join(
                f"• {quest.title} ({quest.difficulty}) - {len(quest.checkpoints)}/{len(quest.objectives)} objectives"
                for quest in active_quests[:5]  # Show first 5
            )
            embed.add_field(
                name="🎯 Active Quests",
                value=active_text or "No active quests",
                inline=False
            )

            # Show recent completions
            completed_text = "\n".join(
                f"• {quest.title} - Completed {quest.completed_at.strftime('%Y-%m-%d')}"
                for quest in completed_quests[-5:]  # Show last 5
            )
            embed.add_field(
                name="✅ Recent Completions",
                value=completed_text or "No completed quests",
                inline=False
            )

            await ctx.send(embed=embed)

    def _create_equipment_embed(self, item: 'Equipment') -> discord.Embed:
        """Create an embed for equipment details."""
        color = self.progression.RARITY_COLORS.get(item.rarity, 0x969696)
        
        embed = discord.Embed(
            title=f"{item.name}",
            description=item.description,
            color=color
        )

        # Add stats
        stats_text = "\n".join(f"**{stat}:** {value}" for stat, value in item.stats.items())
        embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        # Add abilities if any
        if item.abilities:
            abilities_text = "\n".join(f"• {ability}" for ability in item.abilities)
            embed.add_field(name="⚡ Abilities", value=abilities_text, inline=True)

        # Add flavor text
        if item.flavor_text:
            embed.set_footer(text=item.flavor_text)

        return embed

    def _get_quest_rarity(self, difficulty: str) -> str:
        """Convert quest difficulty to rarity for display."""
        return {
            "Novice": "common",
            "Apprentice": "common",
            "Adept": "rare",
            "Expert": "epic",
            "Master": "legendary",
            "Legendary": "mythic"
        }.get(difficulty, "common")