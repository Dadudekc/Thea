#!/usr/bin/env python3
"""
Dream.OS Memory Prompt API
==========================

Prompt-related operations for the Memory API.
"""

import logging
from typing import List, Dict, Optional, Any

from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class MemoryPromptAPI:
    """Handle prompt-related memory operations."""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the prompt API.
        
        Args:
            memory_manager: MemoryManager instance
        """
        self.memory = memory_manager
    
    def search_prompts(self, query: str = None, category: str = None, prompt_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for prompts with optional filtering.
        
        Args:
            query: Text to search for in prompt content
            category: Filter by prompt category
            prompt_type: Filter by prompt type
            limit: Maximum number of results
            
        Returns:
            List of matching prompts with conversation context
        """
        try:
            return self.memory.search_prompts(query, category, prompt_type, limit)
        except Exception as e:
            logger.error(f"❌ Failed to search prompts: {e}")
            return []
    
    def get_prompts_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all prompts for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of prompts for the conversation
        """
        try:
            return self.memory.get_prompts_by_conversation(conversation_id)
        except Exception as e:
            logger.error(f"❌ Failed to get prompts for conversation {conversation_id}: {e}")
            return []
    
    def get_prompt_categories(self) -> List[str]:
        """
        Get all available prompt categories.
        
        Returns:
            List of prompt categories
        """
        try:
            return self.memory.get_prompt_categories()
        except Exception as e:
            logger.error(f"❌ Failed to get prompt categories: {e}")
            return []
    
    def get_prompt_types(self) -> List[str]:
        """
        Get all available prompt types.
        
        Returns:
            List of prompt types
        """
        try:
            return self.memory.get_prompt_types()
        except Exception as e:
            logger.error(f"❌ Failed to get prompt types: {e}")
            return []
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """
        Get statistics about prompts in the database.
        
        Returns:
            Dictionary with prompt statistics
        """
        try:
            return self.memory.get_prompt_stats()
        except Exception as e:
            logger.error(f"❌ Failed to get prompt stats: {e}")
            return {}
    
    def get_best_prompts(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most effective prompts.
        
        Args:
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of most effective prompts
        """
        try:
            return self.memory.search_prompts(category=category, limit=limit)
        except Exception as e:
            logger.error(f"❌ Failed to get best prompts: {e}")
            return [] 