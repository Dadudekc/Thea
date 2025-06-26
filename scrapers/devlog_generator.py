"""
DevLog Content Generator - Transform ChatGPT conversations into engaging developer content.
Processes chat history into structured blog posts, technical articles, and social media content.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from scrapers.content_processor import ContentProcessor, ContentBlock
from scrapers.blog_generator import BlogGenerator
from scrapers.social_content_generator import SocialContentGenerator

logger = logging.getLogger(__name__)

@dataclass
class DevLogPost:
    """Represents a structured blog post from a conversation."""
    title: str
    description: str
    date: datetime
    tags: List[str]
    content_blocks: List[ContentBlock]
    code_snippets: List[Dict[str, str]]
    challenges: List[str]
    solutions: List[str]
    key_learnings: List[str]

class DevLogGenerator:
    """Transforms ChatGPT conversations into various content formats."""
    
    def __init__(self, strategies: dict = {}):
        """
        Initialize the generator.
        
        Args:
            strategies: Dictionary of strategies for different platforms
        """
        self.strategies = strategies
        self.content_processor = ContentProcessor()
        self.blog_generator = BlogGenerator()
        self.social_generator = SocialContentGenerator()
        logger.info("Initialized DevLog Generator")

    def process_conversation(self, chat_data: Dict[str, Any]) -> DevLogPost:
        """
        Process a single conversation into a structured blog post.
        
        Args:
            chat_data: Raw chat data from scraper
            
        Returns:
            DevLogPost: Structured blog post
        """
        # Extract messages and metadata
        messages = chat_data.get("messages", [])
        
        # Initialize content blocks
        content_blocks = []
        code_snippets = []
        challenges = []
        solutions = []
        key_learnings = []
        
        # Process each message
        for msg in messages:
            block = self.content_processor.process_message(msg)
            if block:
                content_blocks.append(block)
                
                # Categorize content
                if block.type == "code":
                    code_snippets.append({
                        "code": block.content,
                        "language": block.metadata.get("language", ""),
                        "description": block.metadata.get("description", "")
                    })
                elif block.type == "error":
                    challenges.append(block.content)
                elif block.type == "solution":
                    solutions.append(block.content)
                
                # Extract key learnings from explanations
                if block.type == "explanation" and block.metadata.get("is_learning", False):
                    key_learnings.append(block.content)
        
        # Generate title and description
        title = self.blog_generator.generate_title(content_blocks)
        description = self.blog_generator.generate_description(content_blocks)
        
        # Create DevLogPost
        return DevLogPost(
            title=title,
            description=description,
            date=datetime.now(),
            tags=self.blog_generator.extract_tags(content_blocks),
            content_blocks=content_blocks,
            code_snippets=code_snippets,
            challenges=challenges,
            solutions=solutions,
            key_learnings=key_learnings
        )

    def generate_blog_post(self, post: DevLogPost, output_file: str) -> bool:
        """Generate a blog post in markdown format."""
        post_data = {
            'title': post.title,
            'description': post.description,
            'date': post.date,
            'tags': post.tags,
            'content_blocks': post.content_blocks,
            'code_snippets': post.code_snippets,
            'challenges': post.challenges,
            'solutions': post.solutions,
            'key_learnings': post.key_learnings
        }
        return self.blog_generator.generate_blog_post(post_data, output_file)

    def generate_social_content(self, post: DevLogPost, platform: str) -> List[Dict[str, str]]:
        """Generate social media content from the blog post."""
        post_data = {
            'title': post.title,
            'description': post.description,
            'date': post.date,
            'tags': post.tags,
            'key_learnings': post.key_learnings
        }
        return self.social_generator.generate_social_content(post_data, platform)

    def auto_publish(
        self,
        chat_data: Dict[str, Any],
        dispatcher: 'DevLogDispatcher',
        blog_output_dir: str = "content/posts",
        social_output_dir: str = "content/social"
    ) -> bool:
        """
        Automatically process conversation and publish content across platforms.
        
        Args:
            chat_data: Raw chat data from scraper
            dispatcher: DevLogDispatcher instance for publishing
            blog_output_dir: Output directory for blog posts
            social_output_dir: Output directory for social content
            
        Returns:
            bool: True if all publishing steps succeeded
        """
        try:
            # Process conversation into structured post
            post = self.process_conversation(chat_data)
            
            # Generate blog post
            blog_file = Path(blog_output_dir) / f"{post.date.strftime('%Y-%m-%d')}-{post.title.lower().replace(' ', '-')}.md"
            if not self.generate_blog_post(post, str(blog_file)):
                logger.error("Failed to generate blog post")
                return False
            
            # Generate social content for each platform
            for platform, strategy in self.strategies.items():
                social_content = self.generate_social_content(post, platform)
                if social_content:
                    # Save social content to trigger dispatcher
                    social_file = Path(social_output_dir) / f"{post.date.strftime('%Y-%m-%d')}-{platform}-posts.json"
                    social_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(social_file, 'w') as f:
                        json.dump(social_content, f, indent=2)
                    
                    logger.info(f"Generated {platform} content: {social_file}")
            
            logger.info(f"Successfully auto-published content from conversation")
            return True
            
        except Exception as e:
            logger.error(f"Failed to auto-publish content: {str(e)}")
            return False

def main():
    """Main entry point for the DevLog Generator."""
    try:
        # Initialize components
        generator = DevLogGenerator()
        
        # Example usage
        logger.info("DevLog Generator ready for use")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 