#!/usr/bin/env python3
"""
Search Storage for Memory Storage
Handles search and indexing operations.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SearchStorage:
    """Handles search and indexing operations."""
    
    def __init__(self, connection):
        """
        Initialize the search storage.
        
        Args:
            connection: SQLite connection object
        """
        self.conn = connection
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversations by content.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching conversation dictionaries
        """
        try:
            cursor = self.conn.cursor()
            
            # Search in title, content, and tags
            search_sql = """
                SELECT * FROM conversations 
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            
            search_term = f"%{query}%"
            cursor.execute(search_sql, (search_term, search_term, search_term, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(dict(row))
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to search conversations: {e}")
            return []
    
    def store_memory_index(self, index_data: Dict[str, Any]) -> bool:
        """
        Store content in the memory index for search.
        
        Args:
            index_data: Dictionary containing index data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO memory_index
                (conversation_id, content_hash, content_type, content_text)
                VALUES (?, ?, ?, ?)
            """, (
                index_data.get('conversation_id'),
                index_data.get('content_hash'),
                index_data.get('content_type'),
                index_data.get('content_text')
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory index: {e}")
            return False

    def advanced_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform basic boolean search with optional exclusion terms."""
        try:
            cursor = self.conn.cursor()

            terms = []
            params = []
            for token in query.split():
                if token.startswith('-'):
                    like = f"%{token[1:]}%"
                    terms.append("(title NOT LIKE ? AND content NOT LIKE ? AND tags NOT LIKE ?)")
                    params.extend([like, like, like])
                else:
                    like = f"%{token}%"
                    terms.append("(title LIKE ? OR content LIKE ? OR tags LIKE ?)")
                    params.extend([like, like, like])

            where_clause = " AND ".join(terms) if terms else "1"
            search_sql = f"""
                SELECT * FROM conversations
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(search_sql, params)

            conversations = [dict(row) for row in cursor.fetchall()]
            return conversations

        except Exception as e:
            logger.error(f"❌ Failed to run advanced search: {e}")
            return []
