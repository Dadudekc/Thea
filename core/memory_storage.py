"""
Memory Storage Module
Handles SQLite database operations for the memory system.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .database_schema_manager import DatabaseSchemaManager
from .conversation_storage import ConversationStorage
from .search_storage import SearchStorage

logger = logging.getLogger(__name__)

class MemoryStorage:
    """Handles SQLite database operations for memory management."""
    
    def __init__(self, db_path: str = "dreamos_memory.db"):
        """
        Initialize the memory storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.schema_manager = DatabaseSchemaManager()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with schema."""
        try:
            self.conn = self.schema_manager.init_database(self.db_path)
            self.conversation_storage = ConversationStorage(self.conn)
            self.search_storage = SearchStorage(self.conn)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory database: {e}")
            raise
    
    def store_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """Store a conversation in the database."""
        return self.conversation_storage.store_conversation(conversation_data)
    
    def get_conversation_by_id(self, conversation_id: str) -> Dict[str, Any]:
        """Retrieve a conversation by ID."""
        return self.conversation_storage.get_conversation_by_id(conversation_id)
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations."""
        return self.conversation_storage.get_recent_conversations(limit)
    
    def get_conversations_chronological(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversations in chronological order (oldest first).
        This is important for storyline progression where the earliest
        conversations should be processed first.
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of conversations in chronological order
        """
        return self.conversation_storage.get_conversations_chronological(limit)
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by content."""
        return self.search_storage.search_conversations(query, limit)

    def advanced_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Run advanced boolean search across conversations."""
        return self.search_storage.advanced_search(query, limit)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        return self.conversation_storage.get_conversation_stats()
    
    def store_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """
        Store a prompt in the database.
        
        Args:
            prompt_data: Dictionary containing prompt data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO prompts
                (conversation_id, prompt_text, prompt_type, prompt_category, prompt_effectiveness)
                VALUES (?, ?, ?, ?, ?)
            """, (
                prompt_data.get('conversation_id'),
                prompt_data.get('prompt_text'),
                prompt_data.get('prompt_type', 'user'),
                prompt_data.get('prompt_category', 'general'),
                prompt_data.get('prompt_effectiveness', 0)
            ))
            
            self.conn.commit()
            logger.info(f"✅ Stored prompt for conversation: {prompt_data.get('conversation_id')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store prompt: {e}")
            return False
    
    def get_prompts_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get prompts for a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of prompt dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM prompts WHERE conversation_id = ?
                ORDER BY extracted_at DESC
            """, (conversation_id,))
            
            prompts = []
            for row in cursor.fetchall():
                prompts.append(dict(row))
            
            return prompts
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve prompts for {conversation_id}: {e}")
            return []
    
    def store_memory_index(self, index_data: Dict[str, Any]) -> bool:
        """Store content in the memory index for search."""
        return self.search_storage.store_memory_index(index_data)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_conversations_count(self) -> int:
        return self.conversation_storage.get_conversations_count() 