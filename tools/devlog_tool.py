#!/usr/bin/env python3
"""
Universal DevLog Tool - Create and post development updates to Discord.
"""

import os
import sys
import json
import click
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.discord_manager import DiscordManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentBlock:
    """Represents a block of content in a devlog post."""
    type: str
    content: str
    metadata: Dict = None

@dataclass
class DevLogPost:
    """Represents a structured devlog post."""
    title: str
    description: str
    date: datetime
    content_blocks: List[ContentBlock]
    tags: List[str] = None
    code_snippets: List[Dict[str, str]] = None
    challenges: List[str] = None
    solutions: List[str] = None
    key_learnings: List[str] = None

class DevLogTool:
    """Tool for creating and posting devlog updates."""
    
    def __init__(self):
        """Initialize the devlog tool."""
        self.discord = DiscordManager()
        
        # Ensure output directories exist
        self.output_dir = Path(project_root) / "outputs" / "devlogs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_devlog(
        self,
        title: str,
        description: str,
        content: str,
        tags: List[str] = None,
        code_snippets: List[Dict[str, str]] = None,
        challenges: List[str] = None,
        solutions: List[str] = None,
        key_learnings: List[str] = None
    ) -> DevLogPost:
        """Create a new devlog post."""
        # Create main content block
        content_block = ContentBlock(
            type="text",
            content=content,
            metadata={}
        )
        
        return DevLogPost(
            title=title,
            description=description,
            date=datetime.now(),
            content_blocks=[content_block],
            tags=tags or [],
            code_snippets=code_snippets or [],
            challenges=challenges or [],
            solutions=solutions or [],
            key_learnings=key_learnings or []
        )
    
    def format_for_discord(self, post: DevLogPost) -> str:
        """Format a devlog post for Discord."""
        # Start with a nice header
        discord_msg = [
            "🚀 **DevLog Update**",
            f"**{post.title}**",
            "",
            f"*{post.description}*",
            "",
            "📝 **Update Details**",
            post.content_blocks[0].content,  # Main content
            ""
        ]
        
        # Add code snippets if any
        if post.code_snippets:
            discord_msg.extend([
                "💻 **Code Changes**"
            ])
            for snippet in post.code_snippets:
                discord_msg.extend([
                    f"```{snippet.get('language', '')}",
                    snippet['code'],
                    "```",
                    snippet.get('description', ''),
                    ""
                ])
        
        # Add challenges and solutions if any
        if post.challenges:
            discord_msg.extend([
                "🔍 **Challenges**",
                *[f"- {challenge}" for challenge in post.challenges],
                ""
            ])
            
        if post.solutions:
            discord_msg.extend([
                "✨ **Solutions**",
                *[f"- {solution}" for solution in post.solutions],
                ""
            ])
        
        # Add key learnings if any
        if post.key_learnings:
            discord_msg.extend([
                "💡 **Key Learnings**",
                *[f"- {learning}" for learning in post.key_learnings],
                ""
            ])
        
        # Add tags
        if post.tags:
            discord_msg.append(f"🏷️ {' '.join(['#' + tag for tag in post.tags])}")
        
        # Add timestamp
        discord_msg.extend([
            "",
            f"*Posted: {post.date.strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(discord_msg)
    
    def save_local(self, post: DevLogPost) -> Path:
        """Save the devlog post locally."""
        # Create filename from date and title
        filename = f"{post.date.strftime('%Y-%m-%d')}-{post.title.lower().replace(' ', '-')}.md"
        output_path = self.output_dir / filename
        
        # Format content for markdown
        content = [
            f"# {post.title}",
            "",
            f"_{post.description}_",
            "",
            "## Update Details",
            post.content_blocks[0].content,
            ""
        ]
        
        if post.code_snippets:
            content.extend([
                "## Code Changes",
                ""
            ])
            for snippet in post.code_snippets:
                content.extend([
                    f"```{snippet.get('language', '')}",
                    snippet['code'],
                    "```",
                    snippet.get('description', ''),
                    ""
                ])
        
        if post.challenges:
            content.extend([
                "## Challenges",
                "",
                *[f"- {challenge}" for challenge in post.challenges],
                ""
            ])
            
        if post.solutions:
            content.extend([
                "## Solutions",
                "",
                *[f"- {solution}" for solution in post.solutions],
                ""
            ])
            
        if post.key_learnings:
            content.extend([
                "## Key Learnings",
                "",
                *[f"- {learning}" for learning in post.key_learnings],
                ""
            ])
            
        if post.tags:
            content.extend([
                "## Tags",
                "",
                " ".join(['#' + tag for tag in post.tags]),
                ""
            ])
            
        content.extend([
            "---",
            f"Posted: {post.date.strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(content))
        
        return output_path
    
    async def post_to_discord(self, content: str, channel_id: Optional[str] = None) -> bool:
        """Post the devlog update to Discord."""
        # Prefer using the Discord bot if available and running
        try:
            if self.discord.config.get("enabled"):
                # Connect if needed (non-blocking attempt)
                if not self.discord.is_connected:
                    logger.info("[DevLog] Discord bot not connected. Attempting REST fallback...")
                    raise RuntimeError("Bot not connected")
                await self.discord.send_message(content, channel_id)
                return True
        except Exception as bot_err:
            logger.warning(f"[DevLog] Bot send failed: {bot_err}. Falling back to REST API.")
        
        # REST fallback using bot token
        token = os.getenv("DISCORD_BOT_TOKEN") or self.discord.config.get("bot_token")
        target_channel_id = channel_id or self.discord.config.get("channel_id")
        if not token or not target_channel_id:
            logger.error("[DevLog] Missing token or channel ID for REST fallback.")
            return False
        
        headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "content": content
        }
        try:
            resp = requests.post(f"https://discord.com/api/v10/channels/{target_channel_id}/messages", headers=headers, json=payload, timeout=10)
            if resp.status_code == 200 or resp.status_code == 201:
                logger.info("[DevLog] Sent message via REST API")
                return True
            else:
                logger.error(f"[DevLog] REST API error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"[DevLog] REST API request failed: {e}")
            return False

@click.group()
def cli():
    """Universal DevLog Tool - Create and post development updates."""
    pass

@cli.command()
@click.option('--title', '-t', required=True, help='Title of the devlog update')
@click.option('--description', '-d', required=True, help='Brief description of the update')
@click.option('--content', '-c', required=True, help='Main content of the update')
@click.option('--tags', multiple=True, help='Tags for categorizing the update')
@click.option('--channel', help='Discord channel ID to post to (optional)')
@click.option('--code', multiple=True, help='Code snippets to include')
@click.option('--code-lang', multiple=True, help='Language for each code snippet')
@click.option('--challenge', multiple=True, help='Challenges encountered')
@click.option('--solution', multiple=True, help='Solutions implemented')
@click.option('--learning', multiple=True, help='Key learnings')
def create(
    title: str,
    description: str,
    content: str,
    tags: tuple,
    channel: Optional[str],
    code: tuple,
    code_lang: tuple,
    challenge: tuple,
    solution: tuple,
    learning: tuple
):
    """Create and post a new devlog update."""
    tool = DevLogTool()
    
    # Prepare code snippets
    code_snippets = []
    for i, snippet in enumerate(code):
        lang = code_lang[i] if i < len(code_lang) else ""
        code_snippets.append({
            "code": snippet,
            "language": lang,
            "description": ""
        })
    
    # Create the post
    post = tool.create_devlog(
        title=title,
        description=description,
        content=content,
        tags=list(tags),
        code_snippets=code_snippets,
        challenges=list(challenge),
        solutions=list(solution),
        key_learnings=list(learning)
    )
    
    # Save locally
    local_path = tool.save_local(post)
    click.echo(f"Saved devlog to: {local_path}")
    
    # Format and post to Discord
    discord_content = tool.format_for_discord(post)
    
    # Run the async post in the event loop
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(tool.post_to_discord(discord_content, channel))
    
    if success:
        click.echo("Successfully posted to Discord!")
    else:
        click.echo("Failed to post to Discord", err=True)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--channel', help='Discord channel ID to post to (optional)')
def post(file: str, channel: Optional[str]):
    """Post an existing devlog file to Discord."""
    tool = DevLogTool()
    
    # Read the file
    with open(file, 'r') as f:
        content = f.read()
    
    # Run the async post in the event loop
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(tool.post_to_discord(content, channel))
    
    if success:
        click.echo("Successfully posted to Discord!")
    else:
        click.echo("Failed to post to Discord", err=True)

if __name__ == '__main__':
    cli() 