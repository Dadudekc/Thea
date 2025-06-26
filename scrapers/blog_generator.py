#!/usr/bin/env python3
"""
Blog Generator for DevLog Generator
Handles blog post generation and markdown formatting.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import frontmatter
from jinja2 import Environment, FileSystemLoader

from scrapers.content_processor import ContentBlock

logger = logging.getLogger(__name__)

class BlogGenerator:
    """Handles blog post generation and formatting."""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the blog generator.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_blog_post(self, post_data: Dict, output_file: str) -> bool:
        """
        Generate a blog post in markdown format.
        
        Args:
            post_data: Structured blog post data
            output_file: Output markdown file path
            
        Returns:
            bool: True if successful
        """
        try:
            template = self.env.get_template("blog_post.md.j2")
            content = template.render(post=post_data)
            
            # Add frontmatter
            post_with_frontmatter = frontmatter.Post(
                content,
                title=post_data['title'],
                date=post_data['date'].strftime("%Y-%m-%d"),
                tags=post_data['tags'],
                description=post_data['description']
            )
            
            # Save to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            frontmatter.dump(post_with_frontmatter, output_file)
            
            logger.info(f"Generated blog post: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate blog post: {str(e)}")
            return False
    
    def generate_title(self, blocks: List[ContentBlock]) -> str:
        """Generate a title from content blocks."""
        # Find the first question or main topic
        for block in blocks:
            if block.type == "question":
                return block.content.strip("?")
        return "Development Log: " + blocks[0].timestamp.strftime("%Y-%m-%d")
    
    def generate_description(self, blocks: List[ContentBlock]) -> str:
        """Generate a description from content blocks."""
        # Combine key points from explanations
        explanations = [b.content for b in blocks if b.type == "explanation"][:2]
        return " ".join(explanations)[:200] + "..."
    
    def extract_tags(self, blocks: List[ContentBlock]) -> List[str]:
        """Extract relevant tags from content."""
        tags = set()
        
        # Common programming languages to detect
        languages = {
            "python", "javascript", "typescript", "java", "cpp", "c++", "ruby", 
            "go", "rust", "php", "swift", "kotlin", "scala", "html", "css"
        }
        
        for block in blocks:
            # Extract from code blocks
            if block.type == "code":
                lang = block.metadata.get("language", "").lower()
                if lang in languages:
                    tags.add(lang)
            
            # Extract from content
            if block.type in ["explanation", "question"]:
                # Split content into words and clean them
                words = block.content.lower().split()
                for word in words:
                    # Remove special characters from word
                    clean_word = ''.join(c for c in word if c.isalnum())
                    
                    # Add programming languages
                    if clean_word in languages:
                        tags.add(clean_word)
                    
                    # Add hashtags (but filter out function parameters)
                    if word.startswith(("#", "@")) and "(" not in word and ")" not in word:
                        tag = word.strip("#@")
                        if tag and not any(c in tag for c in "()=,"):
                            tags.add(tag)
        
        # Add some common categories based on content
        if any("api" in block.content.lower() for block in blocks):
            tags.add("api")
        if any("test" in block.content.lower() for block in blocks):
            tags.add("testing")
        if any("error" in block.content.lower() for block in blocks):
            tags.add("debugging")
        
        return sorted(list(tags)) 