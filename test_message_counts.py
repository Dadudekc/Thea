#!/usr/bin/env python3
"""
Test script to check message counts in conversations.
"""

from core.memory_api import get_memory_api

def test_message_counts():
    """Test message counts in conversations."""
    api = get_memory_api()
    
    # Get first 10 conversations
    conversations = api.get_conversations_chronological(limit=10)
    
    print("Checking message counts for first 10 conversations:")
    print("-" * 80)
    
    for i, conv in enumerate(conversations, 1):
        title = conv.get('title', 'Untitled')[:50]
        message_count = conv.get('message_count', 'N/A')
        word_count = conv.get('word_count', 'N/A')
        
        print(f"{i:2d}. Title: {title}...")
        print(f"    Messages: {message_count}, Words: {word_count}")
        print()
    
    # Check some conversations with different message counts
    print("Checking conversations with different message counts:")
    print("-" * 80)
    
    # Get conversations with message_count > 0
    cursor = api._memory.storage.conn.cursor()
    cursor.execute("""
        SELECT id, title, message_count, word_count 
        FROM conversations 
        WHERE message_count > 0 
        ORDER BY message_count DESC 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1][:40]}...")
        print(f"Messages: {row[2]}, Words: {row[3]}")
        print()
    
    # Check conversations with message_count = 0
    cursor.execute("""
        SELECT id, title, message_count, word_count 
        FROM conversations 
        WHERE message_count = 0 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    print("Conversations with 0 messages:")
    print("-" * 80)
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1][:40]}...")
        print(f"Messages: {row[2]}, Words: {row[3]}")
        print()
    
    # Check total counts
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE message_count > 0")
    with_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE message_count = 0")
    without_messages = cursor.fetchone()[0]
    
    print(f"Total conversations with messages: {with_messages}")
    print(f"Total conversations without messages: {without_messages}")
    print(f"Total conversations: {with_messages + without_messages}")

if __name__ == "__main__":
    test_message_counts() 