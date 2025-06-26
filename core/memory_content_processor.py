#!/usr/bin/env python3
"""
Dream.OS Memory Content Processor
================================

Content processing operations for the Memory Manager.
"""

import logging
import hashlib
from typing import List, Dict, Any
from datetime import datetime

from .memory_storage import MemoryStorage

logger = logging.getLogger(__name__)

class MemoryContentProcessor:
    """Handle content processing operations."""
    
    def __init__(self, storage: MemoryStorage):
        """
        Initialize the content processor.
        
        Args:
            storage: MemoryStorage instance
        """
        self.storage = storage
    
    def extract_content(self, convo_data: Dict[str, Any]) -> str:
        """
        Extract content from conversation data.
        
        Args:
            convo_data: Conversation data dictionary
            
        Returns:
            Extracted content string
        """
        content_parts = []
        
        # Add title
        if convo_data.get('title'):
            content_parts.append(f"Title: {convo_data['title']}")
        
        # Add summary
        if convo_data.get('summary'):
            content_parts.append(f"Summary: {convo_data['summary']}")
        
        # Add messages
        messages = convo_data.get('messages', [])
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            if content:
                content_parts.append(f"{role.title()}: {content}")
        
        return "\n\n".join(content_parts)
    
    def index_conversation_content(self, conversation_id: str, conversation: Dict[str, Any]):
        """
        Index conversation content for search.
        
        Args:
            conversation_id: ID of the conversation
            conversation: Conversation data dictionary
        """
        try:
            # Index title
            if conversation.get('title'):
                self.storage.store_memory_index({
                    'conversation_id': conversation_id,
                    'content_hash': hashlib.md5(conversation['title'].encode()).hexdigest(),
                    'content_type': 'title',
                    'content_text': conversation['title']
                })
            
            # Index summary
            if conversation.get('summary'):
                self.storage.store_memory_index({
                    'conversation_id': conversation_id,
                    'content_hash': hashlib.md5(conversation['summary'].encode()).hexdigest(),
                    'content_type': 'summary',
                    'content_text': conversation['summary']
                })
            
            # Index content in chunks
            content = conversation.get('content', '')
            if content:
                chunks = self.chunk_content(content)
                for i, chunk in enumerate(chunks):
                    self.storage.store_memory_index({
                        'conversation_id': conversation_id,
                        'content_hash': hashlib.md5(chunk.encode()).hexdigest(),
                        'content_type': 'content',
                        'content_text': chunk
                    })
            
            # Index tags
            tags = conversation.get('tags', '')
            if tags:
                self.storage.store_memory_index({
                    'conversation_id': conversation_id,
                    'content_hash': hashlib.md5(tags.encode()).hexdigest(),
                    'content_type': 'tags',
                    'content_text': tags
                })
                
        except Exception as e:
            logger.error(f"❌ Failed to index conversation {conversation_id}: {e}")
    
    def chunk_content(self, content: str, chunk_size: int = 1000) -> List[str]:
        """
        Split content into chunks for indexing.
        
        Args:
            content: Content string to chunk
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of content chunks
        """
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def prepare_conversation_data(self, convo_data: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
        """
        Prepare conversation data for storage.
        
        Args:
            convo_data: Raw conversation data
            conversation_id: ID of the conversation
            
        Returns:
            Prepared conversation data
        """
        return {
            'id': conversation_id,
            'title': convo_data.get('title', 'Untitled'),
            'timestamp': convo_data.get('timestamp', datetime.now().isoformat()),
            'captured_at': convo_data.get('captured_at', datetime.now().isoformat()),
            'model': convo_data.get('model', 'gpt-4o'),
            'tags': convo_data.get('tags', ''),
            'summary': convo_data.get('summary'),
            'content': self.extract_content(convo_data),
            'url': convo_data.get('url', ''),
            'message_count': len(convo_data.get('messages', [])),
            'word_count': len(self.extract_content(convo_data).split())
        } 