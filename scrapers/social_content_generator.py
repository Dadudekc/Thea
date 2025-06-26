#!/usr/bin/env python3
"""
Social Content Generator for DevLog Generator
Handles social media content generation for different platforms.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import logging
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class SocialContentGenerator:
    """Handles social media content generation."""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the social content generator.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_social_content(self, post_data: Dict, platform: str) -> List[Dict[str, str]]:
        """
        Generate social media content from the blog post.
        
        Args:
            post_data: Structured blog post data
            platform: Target platform (twitter, linkedin, etc.)
            
        Returns:
            List[Dict[str, str]]: List of social media posts
        """
        try:
            template = self.env.get_template(f"{platform}_post.j2")
            posts = []
            
            # Generate main post
            main_post = template.render(
                post=post_data,
                title=post_data['title'],
                description=post_data['description'],
                key_learnings=post_data['key_learnings'][:3],  # Top 3 learnings
                tags=post_data['tags'],
                url=f"https://blog.dream.os/posts/{post_data['date'].strftime('%Y-%m-%d')}-{post_data['title'].lower().replace(' ', '-')}"
            )
            posts.append({
                "type": "main",
                "content": main_post
            })
            
            # Generate thread for key learnings if more than 3
            if len(post_data['key_learnings']) > 3:
                thread_template = self.env.get_template(f"{platform}_thread.j2")
                thread = thread_template.render(
                    learnings=post_data['key_learnings'][3:],
                    tags=post_data['tags'],
                    total=len(post_data['key_learnings'][3:])
                )
                posts.append({
                    "type": "thread",
                    "content": thread
                })
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to generate social content: {str(e)}")
            return [] 