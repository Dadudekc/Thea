#!/usr/bin/env python3
"""
Test script for Conversation Statistics Updater
"""

from core.memory_manager import MemoryManager
from core.conversation_stats_updater import ConversationStatsUpdater

def test_stats_updater():
    """Test the conversation stats updater."""
    print("🔧 Testing Conversation Statistics Updater...")
    
    try:
        # Initialize memory manager and stats updater
        memory_manager = MemoryManager("dreamos_memory.db")
        stats_updater = ConversationStatsUpdater(memory_manager)
        
        # Get current stats before update
        print("\n📊 Current Statistics (Before Update):")
        summary = stats_updater.get_conversation_stats_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Test updating a few conversations first
        print("\n🔄 Testing with first 5 conversations...")
        result = stats_updater.update_all_conversation_stats(limit=5)
        
        if result.get("success"):
            print(f"✅ Updated {result['updated_count']}/{result['total_conversations']} conversations")
            if result.get("errors"):
                print(f"⚠️ Errors: {len(result['errors'])}")
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"    • {error}")
        else:
            print(f"❌ Update failed: {result.get('error')}")
            return False
        
        # Get updated stats
        print("\n📊 Updated Statistics (After Update):")
        updated_summary = stats_updater.get_conversation_stats_summary()
        for key, value in updated_summary.items():
            print(f"  {key}: {value}")
        
        # Show improvement
        if summary.get("accuracy") != updated_summary.get("accuracy"):
            print(f"\n🎉 Accuracy improved from '{summary.get('accuracy')}' to '{updated_summary.get('accuracy')}'")
        
        memory_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Conversation Statistics Updater Test")
    print("=" * 50)
    
    success = test_stats_updater()
    
    if success:
        print("\n✅ All tests passed!")
        print("\n💡 To update all conversations, run:")
        print("   python -c \"from core.memory_manager import MemoryManager; from core.conversation_stats_updater import ConversationStatsUpdater; m = MemoryManager('dreamos_memory.db'); s = ConversationStatsUpdater(m); result = s.update_all_conversation_stats(); print(f'Updated {result.get(\"updated_count\", 0)} conversations')\"")
    else:
        print("\n❌ Tests failed!")

if __name__ == "__main__":
    main()
 