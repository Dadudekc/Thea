#!/usr/bin/env python3
"""
Update Conversation Statistics Script
====================================

Standalone script to update conversation statistics by extracting messages
from conversation content and storing them in the messages table.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager
from core.conversation_stats_updater import ConversationStatsUpdater

def main():
    """Main function to update conversation statistics."""
    print("📊 Conversation Statistics Updater")
    print("=" * 50)
    
    try:
        # Initialize memory manager
        print("🔧 Initializing memory manager...")
        memory_manager = MemoryManager("dreamos_memory.db")
        
        # Create stats updater
        stats_updater = ConversationStatsUpdater(memory_manager)
        
        # Get current stats
        print("\n📈 Current Statistics:")
        summary = stats_updater.get_conversation_stats_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Ask user for confirmation
        total_conversations = summary.get('total_conversations', 0)
        if total_conversations == 0:
            print("\n❌ No conversations found in database.")
            return
        
        print(f"\n🔄 Found {total_conversations} conversations to update.")
        response = input("Do you want to update all conversation statistics? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Update cancelled.")
            return
        
        # Update statistics
        print("\n🔄 Updating conversation statistics...")
        result = stats_updater.update_all_conversation_stats(limit=None)
        
        if result.get("success"):
            updated_count = result.get("updated_count", 0)
            total_conversations = result.get("total_conversations", 0)
            
            print(f"\n✅ Successfully updated {updated_count}/{total_conversations} conversations!")
            
            # Show updated stats
            print("\n📈 Updated Statistics:")
            updated_summary = stats_updater.get_conversation_stats_summary()
            for key, value in updated_summary.items():
                print(f"  {key}: {value}")
            
            # Show errors if any
            if result.get("errors"):
                print(f"\n⚠️ Errors encountered: {len(result['errors'])}")
                for error in result["errors"][:10]:  # Show first 10 errors
                    print(f"  • {error}")
                if len(result["errors"]) > 10:
                    print(f"  • ... and {len(result['errors']) - 10} more errors")
            
            # Show improvement
            if summary.get("accuracy") != updated_summary.get("accuracy"):
                print(f"\n🎉 Accuracy improved from '{summary.get('accuracy')}' to '{updated_summary.get('accuracy')}'")
            
            print(f"\n💡 Message counts and word counts are now accurate!")
            
        else:
            print(f"\n❌ Update failed: {result.get('error')}")
        
        # Close memory manager
        memory_manager.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 