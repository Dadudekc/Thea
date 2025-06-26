#!/usr/bin/env python3
"""
Ingest conversations from chatgpt_chats.json into the Memory Manager.
This script processes the JSON file created by the ChatGPT scraper.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager
from core.memory_api import get_memory_stats

def main():
    print("🧠 Dream.OS Memory Manager - JSON Conversation Ingestion")
    print("=" * 60)
    
    # Check if the JSON file exists
    json_file = project_root / "chatgpt_chats.json"
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        return
    
    # Load the JSON data
    print(f"📁 Loading conversations from: {json_file}")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        print(f"✅ Loaded {len(conversations)} conversations from JSON")
    except Exception as e:
        print(f"❌ Failed to load JSON file: {e}")
        return
    
    # Initialize Memory Manager
    print("\n🧠 Initializing Memory Manager...")
    try:
        with MemoryManager("dreamos_memory.db") as memory:
            print("✅ Memory database initialized")
            
            # Get current stats
            current_stats = memory.get_conversation_stats()
            print(f"📊 Current conversations in database: {current_stats.get('total_conversations', 0)}")
            
            # Process each conversation
            print(f"\n📥 Starting conversation ingestion...")
            ingested_count = 0
            skipped_count = 0
            
            for i, conv in enumerate(conversations, 1):
                try:
                    # Check if conversation already exists
                    existing = memory.get_conversation_by_id(conv['id'])
                    if existing:
                        print(f"⏭️ Skipping existing: {conv.get('title', 'No title')} (ID: {conv['id']})")
                        skipped_count += 1
                        continue
                    
                    # Create conversation data structure
                    conversation_data = {
                        'id': conv['id'],
                        'title': conv.get('title', 'Untitled'),
                        'timestamp': conv.get('timestamp', ''),
                        'captured_at': conv.get('captured_at', ''),
                        'url': conv.get('url', ''),
                        'model': 'gpt-4o',  # Default model
                        'messages': [],  # Will be populated when we extract full content
                        'responses': [],
                        'full_conversation': ''
                    }
                    
                    # Store the conversation
                    memory.store_conversation(conversation_data)
                    ingested_count += 1
                    
                    if i % 50 == 0:
                        print(f"📊 Progress: {i}/{len(conversations)} conversations processed")
                    
                except Exception as e:
                    print(f"⚠️ Failed to ingest conversation {conv.get('title', 'Unknown')}: {e}")
                    continue
            
            # Get final stats
            final_stats = memory.get_conversation_stats()
            
            print(f"\n🎉 Ingestion completed!")
            print(f"📊 Results:")
            print(f"  Total conversations processed: {len(conversations)}")
            print(f"  New conversations ingested: {ingested_count}")
            print(f"  Existing conversations skipped: {skipped_count}")
            print(f"  Total conversations in database: {final_stats.get('total_conversations', 0)}")
            print(f"  Total messages: {final_stats.get('total_messages', 0)}")
            print(f"  Total words: {final_stats.get('total_words', 0):,}")
            
            if ingested_count > 0:
                print(f"\n✅ Successfully ingested {ingested_count} new conversations!")
                print(f"🧠 Memory Manager now contains {final_stats.get('total_conversations', 0)} conversations")
            else:
                print(f"\nℹ️ No new conversations to ingest - all {len(conversations)} conversations already exist")
    
    except Exception as e:
        print(f"❌ Failed to initialize Memory Manager: {e}")
        return

if __name__ == "__main__":
    main() 