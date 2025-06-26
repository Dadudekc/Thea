#!/usr/bin/env python3
"""
Memory Agent API
===============

Agent-specific memory operations for Dream.OS.
Provides context retrieval and memory management for AI agents.
"""

import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryAgentAPI:
    """
    Agent-specific memory operations.
    
    Provides context retrieval and memory management for AI agents.
    """
    
    def __init__(self, memory_manager):
        """
        Initialize the Memory Agent API.
        
        Args:
            memory_manager: MemoryManager instance
        """
        self.memory = memory_manager
        self.storage = memory_manager.storage
    
    def get_agent_context(self, task: str, limit: int = 3) -> str:
        """
        Get relevant context for an agent task.
        
        Args:
            task: Description of the task
            limit: Maximum number of conversations to include
            
        Returns:
            Formatted context string
        """
        try:
            # Search for relevant conversations
            try:
                # Prefer the dedicated search method if available (new API)
                conversations = self.memory.search_conversations(task, limit=limit)  # type: ignore[arg-type]
            except (AttributeError, TypeError):
                # Fallback for older MemoryManager that only implements
                # `get_context_window(query, limit)`.
                conversations = self.memory.get_context_window(task, limit=limit)
            
            if not conversations:
                return "No relevant context found for this task."
            
            # Format context
            context_parts = []
            for i, conv in enumerate(conversations, 1):
                title = conv.get('title', 'Untitled')
                content = conv.get('content', '')[:500]  # First 500 chars
                context_parts.append(f"{i}. {title}\n{content}...")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Failed to get agent context: {e}")
            return "Error retrieving context."
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics for agents.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            stats = self.memory.get_conversation_stats()
            
            # Add agent-specific stats
            cursor = self.storage.conn.cursor()
            
            # Get recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) as recent_count
                FROM conversations 
                WHERE created_at >= datetime('now', '-1 day')
            """)
            recent_24h = cursor.fetchone()[0]
            
            # Get conversations with high message counts
            cursor.execute("""
                SELECT COUNT(*) as high_message_count
                FROM conversations 
                WHERE message_count > 10
            """)
            high_message_count = cursor.fetchone()[0]
            
            # Get average message count
            cursor.execute("""
                SELECT AVG(message_count) as avg_messages
                FROM conversations 
                WHERE message_count > 0
            """)
            avg_messages = cursor.fetchone()[0] or 0
            
            stats.update({
                'recent_24h': recent_24h,
                'high_message_count': high_message_count,
                'avg_messages': round(avg_messages, 1),
                'memory_health': 'Good' if stats.get('total_conversations', 0) > 0 else 'Empty'
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory stats: {e}")
            return {}
    
    def ingest_conversations(self, conversations_dir: str = "data/conversations") -> int:
        """
        Ingest conversations from directory.
        
        Args:
            conversations_dir: Directory containing conversation files
            
        Returns:
            Number of conversations ingested
        """
        try:
            import os
            import glob
            
            # Find all JSON files in the directory
            pattern = os.path.join(conversations_dir, "*.json")
            json_files = glob.glob(pattern)
            
            if not json_files:
                logger.warning(f"No JSON files found in {conversations_dir}")
                return 0
            
            ingested_count = 0
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        conversation_data = json.load(f)
                    
                    # Extract conversation info
                    conversation_id = conversation_data.get('id', '')
                    title = conversation_data.get('title', 'Untitled')
                    content = conversation_data.get('content', '')
                    
                    if not conversation_id:
                        logger.warning(f"Skipping file {json_file}: no conversation ID")
                        continue
                    
                    # Check if conversation already exists
                    existing = self.memory.get_conversation_by_id(conversation_id)
                    if existing:
                        logger.info(f"Conversation {conversation_id} already exists, skipping")
                        continue
                    
                    # Store conversation
                    self.memory.store_conversation(
                        conversation_id=conversation_id,
                        title=title,
                        content=content,
                        source='file_ingest'
                    )
                    
                    ingested_count += 1
                    logger.info(f"Ingested conversation: {title}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to ingest {json_file}: {e}")
                    continue
            
            logger.info(f"Successfully ingested {ingested_count} conversations")
            return ingested_count
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest conversations: {e}")
            return 0
    
    def is_memory_ready(self) -> bool:
        """
        Check if memory is ready for agent operations.
        
        Returns:
            True if memory is ready, False otherwise
        """
        try:
            # Check if we have conversations
            count = self.memory.get_conversations_count()
            
            # Check if we have recent activity
            cursor = self.storage.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM conversations 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            recent_count = cursor.fetchone()[0]
            
            # Memory is ready if we have conversations and recent activity
            return count > 0 and recent_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to check memory readiness: {e}")
            return False
    
    def get_conversation_summary_for_agent(self, conversation_id: str) -> Optional[str]:
        """
        Get a summary of a conversation formatted for agents.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Formatted summary or None
        """
        try:
            conversation = self.memory.get_conversation_by_id(conversation_id)
            
            if not conversation:
                return None
            
            title = conversation.get('title', 'Untitled')
            content = conversation.get('content', '')
            message_count = conversation.get('message_count', 0)
            created_at = conversation.get('created_at', '')
            
            # Create summary
            summary = f"Title: {title}\n"
            summary += f"Messages: {message_count}\n"
            summary += f"Created: {created_at}\n"
            summary += f"Content Preview: {content[:300]}..."
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation summary: {e}")
            return None
    
    def search_relevant_context(self, query: str, task_type: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for context relevant to a specific task type.
        
        Args:
            query: Search query
            task_type: Type of task (e.g., 'coding', 'writing', 'analysis')
            limit: Maximum number of results
            
        Returns:
            List of relevant conversations
        """
        try:
            # Basic search
            conversations = self.memory.search_conversations(query, limit=limit)
            
            # If task_type is specified, filter by content
            if task_type:
                filtered_conversations = []
                for conv in conversations:
                    content = conv.get('content', '').lower()
                    if task_type.lower() in content:
                        filtered_conversations.append(conv)
                
                conversations = filtered_conversations[:limit]
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to search relevant context: {e}")
            return []
