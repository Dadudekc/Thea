#!/usr/bin/env python3
"""
Dream.OS Memory Prompt Processor
================================

Prompt processing operations for the Memory Manager.
"""

import logging
from typing import List, Dict, Any

from .memory_storage import MemoryStorage

logger = logging.getLogger(__name__)

class MemoryPromptProcessor:
    """Handle prompt processing operations."""
    
    def __init__(self, storage: MemoryStorage):
        """
        Initialize the prompt processor.
        
        Args:
            storage: MemoryStorage instance
        """
        self.storage = storage
    
    def extract_and_store_prompts(self, conversation_id: str, convo_data: Dict[str, Any]):
        """
        Extract and store prompts from conversation data.
        
        Args:
            conversation_id: ID of the conversation
            convo_data: Conversation data dictionary
        """
        try:
            messages = convo_data.get('messages', [])
            
            for msg in messages:
                if msg.get('role') == 'user':
                    prompt_text = msg.get('content', '')
                    if prompt_text:
                        # Identify prompts in the text
                        prompts = self.identify_prompts_in_text(prompt_text)
                        
                        for prompt in prompts:
                            prompt_data = {
                                'conversation_id': conversation_id,
                                'prompt_text': prompt['text'],
                                'prompt_type': 'user',
                                'prompt_category': self.categorize_prompt(prompt['text']),
                                'prompt_effectiveness': 0
                            }
                            
                            self.storage.store_prompt(prompt_data)
                            
        except Exception as e:
            logger.error(f"❌ Failed to extract prompts from conversation {conversation_id}: {e}")
    
    def identify_prompts_in_text(self, text: str) -> List[Dict[str, str]]:
        """
        Identify individual prompts in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of prompt dictionaries
        """
        prompts = []
        
        # Simple prompt identification - split by common separators
        separators = ['\n\n', '\n---\n', '\n***\n', '\n###\n']
        
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                for part in parts:
                    part = part.strip()
                    if len(part) > 10:  # Minimum prompt length
                        prompts.append({'text': part})
                break
        else:
            # No separators found, treat entire text as one prompt
            if text.strip():
                prompts.append({'text': text.strip()})
        
        return prompts
    
    def categorize_prompt(self, prompt_text: str) -> str:
        """
        Categorize a prompt based on its content.
        
        Args:
            prompt_text: Text of the prompt
            
        Returns:
            Category string
        """
        text_lower = prompt_text.lower()
        
        if any(word in text_lower for word in ['code', 'program', 'function', 'class']):
            return 'coding'
        elif any(word in text_lower for word in ['explain', 'describe', 'what is']):
            return 'explanation'
        elif any(word in text_lower for word in ['write', 'create', 'generate']):
            return 'generation'
        elif any(word in text_lower for word in ['review', 'analyze', 'evaluate']):
            return 'analysis'
        else:
            return 'general'
    
    def search_prompts(self, query: str = None, category: str = None, prompt_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search prompts with filters.
        
        Args:
            query: Search query
            category: Prompt category filter
            prompt_type: Prompt type filter
            limit: Maximum number of results
            
        Returns:
            List of prompt dictionaries
        """
        # This would implement prompt search functionality
        # For now, return empty list
        return []
    
    def get_prompt_categories(self) -> List[str]:
        """Get list of available prompt categories."""
        return ['coding', 'explanation', 'generation', 'analysis', 'general']
    
    def get_prompt_types(self) -> List[str]:
        """Get list of available prompt types."""
        return ['user', 'system', 'template']
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Get prompt statistics."""
        # This would implement prompt statistics
        return {
            'total_prompts': 0,
            'categories': {},
            'types': {}
        } 