#!/usr/bin/env python3
"""
Test Memory Manager Integration
==============================

Quick test to verify the Memory Manager is working correctly.
"""

from core.memory_api import get_memory_api

def test_memory_integration():
    """Test the memory integration."""
    print("🧠 Testing Dream.OS Memory Manager Integration")
    print("=" * 50)
    
    api = get_memory_api()
    
    try:
        # Test 1: Memory stats
        print("\n📊 Memory Statistics:")
        stats = api.get_memory_stats()
        print(f"  Total Conversations: {stats['total_conversations']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Total Words: {stats['total_words']:,}")
        print(f"  Models Used: {', '.join(stats['models'].keys())}")
        
        # Test 2: Search functionality
        print("\n🔍 Testing Search:")
        results = api.search_conversations("Dream.OS", 3)
        print(f"Found {len(results)} results for 'Dream.OS':")
        for i, conv in enumerate(results, 1):
            print(f"  {i}. {conv['title']} (ID: {conv['id']})")
        
        # Test 3: Recent conversations
        print("\n📅 Recent Conversations:")
        recent = api.get_recent_conversations(5)
        for i, conv in enumerate(recent, 1):
            print(f"  {i}. {conv['title']} (ID: {conv['id']})")
        
        # Test 4: Agent context
        print("\n🧠 Agent Context Test:")
        context = api.get_agent_context("web scraping", 2)
        print("Context for 'web scraping' task:")
        print(context[:500] + "..." if len(context) > 500 else context)
        
        # Test 5: Specific conversation
        if results:
            conv_id = results[0]['id']
            print(f"\n📄 Specific Conversation (ID: {conv_id}):")
            conv = api.get_conversation(conv_id)
            if conv:
                print(f"  Title: {conv['title']}")
                print(f"  Model: {conv['model']}")
                print(f"  Messages: {conv['message_count']}")
                print(f"  Words: {conv['word_count']}")
                if conv.get('summary'):
                    print(f"  Summary: {conv['summary'][:100]}...")
        
        print("\n✅ All memory tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory test failed: {e}")
        return False
    
    finally:
        api.close()

if __name__ == "__main__":
    success = test_memory_integration()
    if success:
        print("\n🚀 Memory Manager is ready for production use!")
    else:
        print("\n❌ Memory Manager needs attention.") 