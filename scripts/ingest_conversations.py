#!/usr/bin/env python3
"""
Dream.OS Conversation Ingestion Script
=====================================

Ingest existing conversations from data/conversations/ into the memory database.
This script handles the initial data migration for the Memory Manager.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function."""
    print("🧠 Dream.OS Memory Manager - Conversation Ingestion")
    print("=" * 50)
    
    # Check if conversations directory exists
    conversations_dir = Path("data/conversations")
    if not conversations_dir.exists():
        print(f"❌ Conversations directory not found: {conversations_dir}")
        print("Please ensure you have conversations in data/conversations/")
        return False
    
    # Count existing conversation files
    conversation_files = list(conversations_dir.glob("*.json"))
    print(f"📁 Found {len(conversation_files)} conversation files")
    
    if not conversation_files:
        print("⚠️ No conversation files found to ingest")
        return False
    
    # Initialize memory manager
    try:
        with MemoryManager("dreamos_memory.db") as memory:
            print("✅ Memory database initialized")
            
            # Show existing stats
            existing_stats = memory.get_conversation_stats()
            if existing_stats['total_conversations'] > 0:
                print(f"📊 Existing conversations in database: {existing_stats['total_conversations']}")
            
            # Ingest conversations
            print("\n📥 Starting conversation ingestion...")
            ingested_count = memory.ingest_conversations(str(conversations_dir))
            
            if ingested_count > 0:
                print(f"\n🎉 Successfully ingested {ingested_count} conversations!")
                
                # Show updated stats
                updated_stats = memory.get_conversation_stats()
                print(f"\n📊 Memory Database Statistics:")
                print(f"  Total Conversations: {updated_stats['total_conversations']}")
                print(f"  Total Messages: {updated_stats['total_messages']}")
                print(f"  Total Words: {updated_stats['total_words']:,}")
                print(f"  Models Used: {', '.join(updated_stats['models'].keys())}")
                
                if updated_stats['date_range']['earliest']:
                    print(f"  Date Range: {updated_stats['date_range']['earliest']} to {updated_stats['date_range']['latest']}")
                
                print(f"\n✅ Memory Manager is ready for use!")
                print(f"   Database: dreamos_memory.db")
                print(f"   Use: from core.memory_manager import MemoryManager")
                
                return True
            else:
                print("❌ No conversations were ingested")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to ingest conversations: {e}")
        print(f"❌ Error: {e}")
        return False


def show_memory_usage():
    """Show how to use the Memory Manager."""
    print("\n🧠 Memory Manager Usage Examples:")
    print("=" * 40)
    
    print("""
# Initialize Memory Manager
from core.memory_manager import MemoryManager

with MemoryManager("dreamos_memory.db") as memory:
    # Search for relevant conversations
    context = memory.get_context_window("python web scraping", limit=3)
    
    # Get specific conversation
    conv = memory.get_conversation_by_id("conversation_id")
    
    # Get recent conversations
    recent = memory.get_recent_conversations(limit=10)
    
    # Get statistics
    stats = memory.get_conversation_stats()
    """)


if __name__ == "__main__":
    success = main()
    
    if success:
        show_memory_usage()
        print("\n🚀 Memory Manager integration complete!")
    else:
        print("\n❌ Ingestion failed. Please check the error messages above.")
        sys.exit(1) 