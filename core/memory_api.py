#!/usr/bin/env python3
"""
Dream.OS Memory API
==================

High-level API for memory access and context management.
Provides easy integration for agents and other components.
"""

import logging
from typing import List, Dict, Optional, Any

from .memory_manager import MemoryManager
from .memory_conversation_api import MemoryConversationAPI
from .memory_prompt_api import MemoryPromptAPI
from .memory_agent_api import MemoryAgentAPI

logger = logging.getLogger(__name__)

class MemoryAPI:
    """
    High-level Memory API for Dream.OS.
    
    Provides simplified access to memory operations for agents and components.
    """
    
    def __init__(self, db_path: str = "dreamos_memory.db"):
        """
        Initialize the Memory API.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._memory = None
        self._conversation_api = None
        self._prompt_api = None
        self._agent_api = None
    
    def _get_memory(self) -> MemoryManager:
        """Get or create MemoryManager instance."""
        if self._memory is None:
            self._memory = MemoryManager(self.db_path)
        return self._memory
    
    def _get_conversation_api(self) -> MemoryConversationAPI:
        """Get or create conversation API instance."""
        if self._conversation_api is None:
            self._conversation_api = MemoryConversationAPI(self._get_memory())
        return self._conversation_api
    
    def _get_prompt_api(self) -> MemoryPromptAPI:
        """Get or create prompt API instance."""
        if self._prompt_api is None:
            self._prompt_api = MemoryPromptAPI(self._get_memory())
        return self._prompt_api
    
    def _get_agent_api(self) -> MemoryAgentAPI:
        """Get or create agent API instance."""
        if self._agent_api is None:
            self._agent_api = MemoryAgentAPI(self._get_memory())
        return self._agent_api
    
    def close(self):
        """Close the memory connection."""
        if self._memory:
            self._memory.close()
            self._memory = None
            self._conversation_api = None
            self._prompt_api = None
            self._agent_api = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Conversation operations
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._get_conversation_api().search_conversations(query, limit)

    def advanced_search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Expose advanced conversation search."""
        return self._get_conversation_api().advanced_search(query, limit)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._get_conversation_api().get_conversation(conversation_id)
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._get_conversation_api().get_recent_conversations(limit)
    
    def get_conversations_by_ids(self, conversation_ids: List[str]) -> List[Dict[str, Any]]:
        return self._get_conversation_api().get_conversations_by_ids(conversation_ids)
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        return self._get_conversation_api().get_conversation_summary(conversation_id)
    
    def get_conversation_metadata(self, conversation_id: str) -> Dict[str, Any]:
        return self._get_conversation_api().get_conversation_metadata(conversation_id)
    
    def format_conversation_for_prompt(self, conversation: Dict[str, Any], max_length: int = 1000) -> str:
        return self._get_conversation_api().format_conversation_for_prompt(conversation, max_length)
    
    def batch_search(self, queries: List[str], limit_per_query: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        return self._get_conversation_api().batch_search(queries, limit_per_query)
    
    def get_conversations_chronological(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get conversations in chronological order with pagination."""
        return self._get_conversation_api().get_conversations_chronological(limit, offset)
    
    def get_conversations_count(self) -> int:
        """Get total number of conversations."""
        return self._get_conversation_api().get_conversations_count()
    
    # Prompt operations
    def search_prompts(self, query: str = None, category: str = None, prompt_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        return self._get_prompt_api().search_prompts(query, category, prompt_type, limit)
    
    def get_prompts_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self._get_prompt_api().get_prompts_by_conversation(conversation_id)
    
    def get_prompt_categories(self) -> List[str]:
        return self._get_prompt_api().get_prompt_categories()
    
    def get_prompt_types(self) -> List[str]:
        return self._get_prompt_api().get_prompt_types()
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        return self._get_prompt_api().get_prompt_stats()
    
    def get_best_prompts(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        return self._get_prompt_api().get_best_prompts(category, limit)
    
    # Agent operations
    def get_agent_context(self, task: str, limit: int = 3) -> str:
        return self._get_agent_api().get_agent_context(task, limit)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        return self._get_agent_api().get_memory_stats()
    
    def ingest_conversations(self, conversations_dir: str = "data/conversations") -> int:
        return self._get_agent_api().ingest_conversations(conversations_dir)
    
    def is_memory_ready(self) -> bool:
        return self._get_agent_api().is_memory_ready()


# Global memory API instance
_memory_api = None

def get_memory_api(db_path: str = "dreamos_memory.db") -> MemoryAPI:
    """Get global Memory API instance."""
    global _memory_api
    if _memory_api is None:
        _memory_api = MemoryAPI(db_path)
    return _memory_api

def close_memory_api():
    """Close the global memory API."""
    global _memory_api
    if _memory_api:
        _memory_api.close()
        _memory_api = None

# Convenience functions
def search_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Quick search function."""
    api = get_memory_api()
    return api.search_conversations(query, limit)

def advanced_search_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Quick advanced search helper."""
    api = get_memory_api()
    return api.advanced_search_conversations(query, limit)

def get_context_for_task(task: str, limit: int = 3) -> str:
    """Quick context function."""
    api = get_memory_api()
    return api.get_agent_context(task, limit)

def get_memory_stats() -> Dict[str, Any]:
    """Quick stats function."""
    api = get_memory_api()
    return api.get_memory_stats()

def search_prompts(query: str = None, category: str = None, prompt_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Quick prompt search function."""
    api = get_memory_api()
    return api.search_prompts(query, category, prompt_type, limit)

def get_prompt_stats() -> Dict[str, Any]:
    """Quick prompt stats function."""
    api = get_memory_api()
    return api.get_prompt_stats()

def get_best_prompts(category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Quick best prompts function."""
    api = get_memory_api()
    return api.get_best_prompts(category, limit)

if __name__ == "__main__":
    # CLI interface for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Dream.OS Memory API")
    parser.add_argument("--search", type=str, help="Search for conversations")
    parser.add_argument("--context", type=str, help="Get context for task")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    parser.add_argument("--recent", type=int, default=5, help="Show recent conversations")
    
    args = parser.parse_args()
    
    with MemoryAPI() as api:
        if args.search:
            print(f"🔍 Searching for: {args.search}")
            results = api.search_conversations(args.search)
            for i, conv in enumerate(results, 1):
                print(f"  {i}. {conv['title']} (ID: {conv['id']})")
        
        if args.context:
            print(f"🧠 Context for task: {args.context}")
            context = api.get_agent_context(args.context)
            print(context)
        
        if args.stats:
            print("📊 Memory Statistics:")
            stats = api.get_memory_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        if args.recent:
            print(f"📅 Recent conversations (last {args.recent}):")
            recent = api.get_recent_conversations(args.recent)
            for i, conv in enumerate(recent, 1):
                print(f"  {i}. {conv['title']} (ID: {conv['id']})") 