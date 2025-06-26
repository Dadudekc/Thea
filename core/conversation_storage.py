#!/usr/bin/env python3
"""
Conversation Storage for Memory Storage
Handles conversation CRUD operations.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationStorage:
    """Handles conversation storage operations."""
    
    def __init__(self, connection):
        """
        Initialize the conversation storage.
        
        Args:
            connection: SQLite connection object
        """
        self.conn = connection
    
    def store_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Store a conversation in the database.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations
                (id, title, timestamp, captured_at, model, tags, summary, content, url, message_count, word_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_data.get('id'),
                conversation_data.get('title', 'Untitled'),
                conversation_data.get('timestamp', datetime.now().isoformat()),
                conversation_data.get('captured_at', datetime.now().isoformat()),
                conversation_data.get('model', 'gpt-4o'),
                conversation_data.get('tags', ''),
                conversation_data.get('summary'),
                conversation_data.get('content'),
                conversation_data.get('url', ''),
                conversation_data.get('message_count', 0),
                conversation_data.get('word_count', 0),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.info(f"[OK] Stored conversation: {conversation_data.get('title', 'Untitled')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store conversation: {e}")
            return False
    
    def get_conversation_by_id(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            Conversation data dictionary or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations WHERE id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve conversation {conversation_id}: {e}")
            return None
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations.
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(dict(row))
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve recent conversations: {e}")
            return []
    
    def get_conversations_chronological(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversations in chronological order (oldest first).
        This is important for storyline progression where the earliest
        conversations should be processed first.
        
        Args:
            limit: Maximum number of conversations to retrieve (None for all)
            
        Returns:
            List of conversation dictionaries in chronological order
        """
        try:
            cursor = self.conn.cursor()
            
            # Build query based on whether limit is specified
            if limit is not None:
                query = """
                    SELECT * FROM conversations 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            else:
                query = """
                    SELECT * FROM conversations 
                    ORDER BY timestamp ASC
                """
                cursor.execute(query)
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(dict(row))
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to retrieve chronological conversations: {e}")
            return []
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary containing statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Get total conversations
            cursor.execute("SELECT COUNT(*) as total FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            # Get conversations by model
            cursor.execute("""
                SELECT model, COUNT(*) as count 
                FROM conversations 
                GROUP BY model
            """)
            model_stats = dict(cursor.fetchall())
            
            # Get total messages and words
            cursor.execute("""
                SELECT 
                    SUM(message_count) as total_messages,
                    SUM(word_count) as total_words
                FROM conversations
            """)
            totals = cursor.fetchone()
            total_messages = totals[0] or 0
            total_words = totals[1] or 0
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*) as recent_count
                FROM conversations 
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            recent_activity = cursor.fetchone()[0]

            # EDIT START: include earliest and latest timestamps for date_range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM conversations")
            ts_row = cursor.fetchone()
            earliest, latest = ts_row if ts_row else (None, None)

            # EDIT START: add daily/weekly/monthly activity counts and include in result
            # Daily activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*)
                FROM conversations
                WHERE timestamp >= datetime('now', '-1 day')
            """)
            daily_activity = cursor.fetchone()[0]

            # Weekly activity (last 7 days)
            cursor.execute("""
                SELECT COUNT(*)
                FROM conversations
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            weekly_activity = cursor.fetchone()[0]

            # Monthly activity (last 30 days)
            cursor.execute("""
                SELECT COUNT(*)
                FROM conversations
                WHERE timestamp >= datetime('now', '-30 days')
            """)
            monthly_activity = cursor.fetchone()[0]
            # EDIT END

            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'total_words': total_words,
                'recent_activity': recent_activity,
                'models': model_stats,
                'date_range': {
                    'earliest': earliest,
                    'latest': latest
                },
                # EDIT START: expose new trend metrics
                'daily_conversations': daily_activity,
                'weekly_conversations': weekly_activity,
                'monthly_conversations': monthly_activity
                # EDIT END
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation stats: {e}")
            return {}
    
    def get_conversations_count(self) -> int:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Failed to count conversations: {e}")
            return 0 