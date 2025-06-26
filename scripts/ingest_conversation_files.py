#!/usr/bin/env python3
"""
Custom Conversation File Ingestion Script
========================================

Handles the specific format of conversation JSON files in data/conversations/
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_conversation_files():
    """Ingest conversation files from data/conversations/ directory."""
    conversations_dir = Path("data/conversations")
    
    if not conversations_dir.exists():
        print("❌ Conversations directory not found")
        return False
    
    # Find all JSON files (excluding extraction summaries)
    json_files = [f for f in conversations_dir.glob("*.json") 
                  if not f.name.startswith("extraction_summary")]
    
    print(f"📁 Found {len(json_files)} conversation files to ingest")
    
    if not json_files:
        print("❌ No conversation files found")
        return False
    
    # Initialize memory manager
    memory_manager = MemoryManager("dreamos_memory.db")
    
    ingested_count = 0
    errors = []
    
    for file_path in json_files:
        try:
            print(f"📥 Processing: {file_path.name}")
            
            # Load JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract conversation data
            conversation_id = data.get('id', file_path.stem)
            title = data.get('title', 'Untitled')
            url = data.get('url', '')
            extracted_at = data.get('extracted_at', datetime.now().isoformat())
            
            # Get content from full_conversation or messages
            content = data.get('full_conversation', '')
            if not content and 'messages' in data:
                # If no full_conversation, combine messages
                messages = data.get('messages', [])
                if isinstance(messages, list):
                    content = '\n\n'.join(messages)
            
            # Create conversation data structure
            conversation_data = {
                'id': conversation_id,
                'title': title,
                'url': url,
                'timestamp': extracted_at,
                'captured_at': extracted_at,
                'model': 'gpt-4o',  # Default model
                'content': content,
                'message_count': len(data.get('messages', [])),
                'word_count': len(content.split()) if content else 0,
                'source': 'chatgpt'
            }
            
            # Store conversation
            if memory_manager.storage.store_conversation(conversation_data):
                ingested_count += 1
                print(f"✅ Ingested: {title} (ID: {conversation_id})")
            else:
                errors.append(f"Failed to store: {title}")
                
        except Exception as e:
            error_msg = f"Failed to ingest {file_path.name}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    # Close memory manager
    memory_manager.close()
    
    # Print summary
    print(f"\n📊 Ingestion Summary:")
    print(f"  Total files processed: {len(json_files)}")
    print(f"  Successfully ingested: {ingested_count}")
    print(f"  Errors: {len(errors)}")
    
    if errors:
        print(f"\n⚠️ Errors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(errors) > 5:
            print(f"  • ... and {len(errors) - 5} more errors")
    
    return ingested_count > 0

def main():
    """Main function."""
    print("📥 Custom Conversation File Ingestion")
    print("=" * 50)
    
    success = ingest_conversation_files()
    
    if success:
        print("\n✅ Ingestion completed successfully!")
        print("💡 You can now run the conversation statistics updater.")
    else:
        print("\n❌ Ingestion failed!")

if __name__ == "__main__":
    main()
