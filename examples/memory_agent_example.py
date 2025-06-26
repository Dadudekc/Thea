#!/usr/bin/env python3
"""
Memory Agent Integration Example
===============================

Demonstrates how agents can use the Memory Manager to access conversation history
and provide context-aware responses.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_api import get_memory_api


class MemoryAwareAgent:
    """
    Example agent that uses memory to provide context-aware responses.
    """
    
    def __init__(self, name: str = "MemoryAgent"):
        self.name = name
        self.memory_api = get_memory_api()
    
    def get_task_context(self, task: str) -> str:
        """
        Get relevant context for a task from memory.
        
        Args:
            task: Task description
            
        Returns:
            Formatted context string
        """
        return self.memory_api.get_agent_context(task, limit=3)
    
    def search_related_conversations(self, query: str, limit: int = 5) -> list:
        """
        Search for conversations related to a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant conversations
        """
        return self.memory_api.search_conversations(query, limit)
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """
        Get summary of a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        summary = self.memory_api.get_conversation_summary(conversation_id)
        return summary or "No summary available."
    
    def analyze_conversation_patterns(self, topic: str) -> dict:
        """
        Analyze conversation patterns for a topic.
        
        Args:
            topic: Topic to analyze
            
        Returns:
            Analysis results
        """
        conversations = self.search_related_conversations(topic, limit=10)
        
        if not conversations:
            return {"error": f"No conversations found for topic: {topic}"}
        
        # Analyze patterns
        total_messages = sum(conv.get('message_count', 0) for conv in conversations)
        total_words = sum(conv.get('word_count', 0) for conv in conversations)
        models_used = set(conv.get('model', 'unknown') for conv in conversations)
        
        # Find most active conversations
        most_active = sorted(conversations, key=lambda x: x.get('message_count', 0), reverse=True)[:3]
        
        return {
            "topic": topic,
            "conversation_count": len(conversations),
            "total_messages": total_messages,
            "total_words": total_words,
            "models_used": list(models_used),
            "most_active_conversations": [
                {
                    "title": conv['title'],
                    "id": conv['id'],
                    "message_count": conv.get('message_count', 0),
                    "word_count": conv.get('word_count', 0)
                }
                for conv in most_active
            ]
        }
    
    def generate_context_prompt(self, task: str, include_recent: bool = True) -> str:
        """
        Generate a context-aware prompt for a task.
        
        Args:
            task: Task description
            include_recent: Whether to include recent conversations
            
        Returns:
            Formatted prompt with context
        """
        prompt_parts = [
            f"Task: {task}",
            "",
            "Relevant conversation history:",
            self.get_task_context(task)
        ]
        
        if include_recent:
            recent = self.memory_api.get_recent_conversations(3)
            if recent:
                prompt_parts.extend([
                    "",
                    "Recent conversations:",
                    *[f"- {conv['title']} (ID: {conv['id']})" for conv in recent]
                ])
        
        prompt_parts.extend([
            "",
            "Memory statistics:",
            f"- Total conversations: {self.memory_api.get_memory_stats()['total_conversations']}",
            f"- Total messages: {self.memory_api.get_memory_stats()['total_messages']}",
            f"- Total words: {self.memory_api.get_memory_stats()['total_words']:,}"
        ])
        
        return "\n".join(prompt_parts)
    
    def close(self):
        """Close the memory connection."""
        self.memory_api.close()


def demonstrate_memory_agent():
    """Demonstrate the MemoryAwareAgent capabilities."""
    print("🧠 Memory-Aware Agent Demonstration")
    print("=" * 50)
    
    agent = MemoryAwareAgent("Thea")
    
    try:
        # Demo 1: Task context
        print("\n1️⃣ Task Context Example:")
        task = "web scraping and data analysis"
        context = agent.get_task_context(task)
        print(f"Context for task: '{task}'")
        print(context[:300] + "..." if len(context) > 300 else context)
        
        # Demo 2: Conversation search
        print("\n2️⃣ Conversation Search Example:")
        search_results = agent.search_related_conversations("Dream.OS", 3)
        print(f"Found {len(search_results)} conversations about 'Dream.OS':")
        for i, conv in enumerate(search_results, 1):
            print(f"  {i}. {conv['title']} (ID: {conv['id']})")
        
        # Demo 3: Pattern analysis
        print("\n3️⃣ Pattern Analysis Example:")
        analysis = agent.analyze_conversation_patterns("Dream.OS")
        print(f"Analysis for 'Dream.OS':")
        print(f"  Conversations: {analysis['conversation_count']}")
        print(f"  Total Messages: {analysis['total_messages']}")
        print(f"  Total Words: {analysis['total_words']:,}")
        print(f"  Models Used: {', '.join(analysis['models_used'])}")
        
        # Demo 4: Context prompt generation
        print("\n4️⃣ Context Prompt Generation:")
        prompt = agent.generate_context_prompt("analyze conversation patterns", include_recent=True)
        print("Generated prompt:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
        # Demo 5: Conversation summary
        if search_results:
            conv_id = search_results[0]['id']
            print(f"\n5️⃣ Conversation Summary Example:")
            summary = agent.get_conversation_summary(conv_id)
            print(f"Summary for conversation {conv_id}:")
            print(summary)
        
        print("\n✅ Memory Agent demonstration completed!")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
    
    finally:
        agent.close()


def show_agent_integration_patterns():
    """Show common integration patterns for agents."""
    print("\n🔧 Agent Integration Patterns")
    print("=" * 40)
    
    print("""
# Pattern 1: Context Loading
agent = MemoryAwareAgent("MyAgent")
context = agent.get_task_context("my task")
# Use context in your agent's prompt

# Pattern 2: Conversation Lookup
conversations = agent.search_related_conversations("python", 5)
for conv in conversations:
    # Process each relevant conversation
    pass

# Pattern 3: Pattern Analysis
analysis = agent.analyze_conversation_patterns("machine learning")
# Use analysis results for insights

# Pattern 4: Prompt Enhancement
prompt = agent.generate_context_prompt("analyze data", include_recent=True)
# Use enhanced prompt with memory context

# Pattern 5: Conversation Summary
summary = agent.get_conversation_summary("conversation_id")
# Use summary for quick reference
    """)


if __name__ == "__main__":
    demonstrate_memory_agent()
    show_agent_integration_patterns()
    
    print("\n🚀 Memory Agent integration ready for production use!") 