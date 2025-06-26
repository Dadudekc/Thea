#!/usr/bin/env python3
"""
Dream.OS Memory Conversation API
===============================

Conversation-related operations for the Memory API.
"""

import logging
from typing import List, Dict, Optional, Any

from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class MemoryConversationAPI:
    """Handle conversation-related memory operations."""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the conversation API.
        
        Args:
            memory_manager: MemoryManager instance
        """
        self.memory = memory_manager
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search conversations by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching conversations
        """
        try:
            return self.memory.get_context_window(query, limit)
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        try:
            return self.memory.get_conversation_by_id(conversation_id)
        except Exception as e:
            logger.error(f"❌ Failed to get conversation {conversation_id}: {e}")
            return None
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations.
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of recent conversations
        """
        try:
            return self.memory.get_recent_conversations(limit)
        except Exception as e:
            logger.error(f"❌ Failed to get recent conversations: {e}")
            return []
    
    def get_conversations_chronological(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get conversations in chronological order (oldest first) with pagination."""
        try:
            query = """
                SELECT id, title, created_at, updated_at, message_count, word_count, source, status
                FROM conversations 
                ORDER BY created_at ASC
            """
            
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset > 0:
                query += f" OFFSET {offset}"
            
            cursor = self.memory.storage.conn.cursor()
            cursor.execute(query)
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'message_count': row[4],
                    'word_count': row[5],
                    'source': row[6],
                    'status': row[7]
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get conversations chronologically: {e}")
            return []
    
    def get_conversations_count(self) -> int:
        """Get total number of conversations."""
        try:
            cursor = self.memory.storage.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Failed to get conversations count: {e}")
            return 0
    
    def get_conversations_by_ids(self, conversation_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple conversations by IDs.
        
        Args:
            conversation_ids: List of conversation IDs
            
        Returns:
            List of conversation data (None for missing conversations)
        """
        results = []
        
        for conv_id in conversation_ids:
            try:
                conv = self.get_conversation(conv_id)
                results.append(conv)
            except Exception as e:
                logger.error(f"❌ Failed to get conversation {conv_id}: {e}")
                results.append(None)
        
        return results
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """
        Get summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary or None
        """
        try:
            conv = self.memory.get_conversation_by_id(conversation_id)
            
            if conv and conv.get('summary'):
                return conv['summary']
            elif conv and conv.get('content'):
                # Return first 200 characters of content as summary
                return conv['content'][:200] + "..."
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get conversation summary: {e}")
            return None
    
    def get_conversation_metadata(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation metadata.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with metadata
        """
        try:
            conv = self.memory.get_conversation_by_id(conversation_id)
            
            if not conv:
                return {}
            
            return {
                'id': conv.get('id'),
                'title': conv.get('title'),
                'model': conv.get('model'),
                'timestamp': conv.get('timestamp'),
                'message_count': conv.get('message_count', 0),
                'word_count': conv.get('word_count', 0),
                'tags': conv.get('tags', ''),
                'url': conv.get('url', '')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation metadata: {e}")
            return {}
    
    def format_conversation_for_prompt(self, conversation: Dict[str, Any], max_length: int = 1000) -> str:
        """
        Format conversation for inclusion in prompts.
        
        Args:
            conversation: Conversation data
            max_length: Maximum length of formatted output
            
        Returns:
            Formatted conversation string
        """
        if not conversation:
            return "No conversation data available."
        
        parts = [
            f"Title: {conversation.get('title', 'Untitled')}",
            f"ID: {conversation.get('id', 'Unknown')}",
            f"Model: {conversation.get('model', 'Unknown')}",
            f"Timestamp: {conversation.get('timestamp', 'Unknown')}"
        ]
        
        if conversation.get('summary'):
            parts.append(f"Summary: {conversation['summary']}")
        
        if conversation.get('content'):
            content = conversation['content']
            if len(content) > max_length:
                content = content[:max_length] + "..."
            parts.append(f"Content: {content}")
        
        return "\n".join(parts)
    
    def batch_search(self, queries: List[str], limit_per_query: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform batch search across multiple queries.
        
        Args:
            queries: List of search queries
            limit_per_query: Results per query
            
        Returns:
            Dictionary mapping queries to results
        """
        results = {}
        
        for query in queries:
            try:
                results[query] = self.search_conversations(query, limit_per_query)
            except Exception as e:
                logger.error(f"❌ Batch search failed for query '{query}': {e}")
                results[query] = []
        
        return results 