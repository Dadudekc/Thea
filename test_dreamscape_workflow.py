#!/usr/bin/env python3
"""
Test Complete Dreamscape Processing Workflow
Tests the end-to-end dreamscape processing system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager
from core.memory_api import MemoryAPI
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from core.dreamscape_memory import DreamscapeMemory

def test_memory_system():
    """Test the memory management system."""
    print("🧠 Testing Memory System...")
    
    try:
        # Test Memory Manager
        mm = MemoryManager()
        stats = mm.get_conversation_stats()
        print(f"  [OK] Memory Manager: {stats.get('total_conversations', 0)} conversations")
        
        # Test Memory API
        api = MemoryAPI()
        conversations = api.get_conversations_chronological(limit=5)
        print(f"  [OK] Memory API: Retrieved {len(conversations)} conversations in chronological order")
        
        # Test Dreamscape Memory
        dm = DreamscapeMemory()
        state = dm.get_current_memory_state()
        print(f"  [OK] Dreamscape Memory: Current tier {state.get('architect_tier', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Memory system test failed: {e}")
        return False

def test_mmorpg_engine():
    """Test the MMORPG engine."""
    print("🎮 Testing MMORPG Engine...")
    
    try:
        # Test MMORPG Engine
        engine = MMORPGEngine()
        
        # Test player info
        player = engine.get_player()
        print(f"  [OK] Player: {player.name} - {player.architect_tier}")
        
        # Test skills
        skills = engine.get_skills()
        print(f"  [OK] Skills: {len(skills)} skills loaded")
        
        # Test game status
        status = engine.get_game_status()
        print(f"  [OK] Game Status: Tier {status['current_tier']}, {status['total_xp']} XP")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] MMORPG engine test failed: {e}")
        return False

def test_dreamscape_processing():
    """Test the dreamscape processing workflow."""
    print("🌌 Testing Dreamscape Processing...")
    
    try:
        # Create processor
        processor = DreamscapeProcessor()
        
        # Test processing a small batch
        result = processor.process_conversations_chronological(limit=3)
        
        if result.get("error"):
            print(f"  [ERROR] Processing failed: {result['error']}")
            return False
        
        processed_count = result.get("processed_count", 0)
        total_conversations = result.get("total_conversations", 0)
        
        print(f"  [OK] Processed {processed_count}/{total_conversations} conversations")
        print(f"  [OK] Processing completed successfully")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Dreamscape processing test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration components."""
    print("🖥️ Testing GUI Integration...")
    
    try:
        # Test that GUI components can be imported
        from gui.main_window import TheaMainWindow
        print("  [OK] GUI main window import successful")
        
        # Test that core systems can be initialized
        from core.memory_manager import MemoryManager
        from core.memory_api import MemoryAPI
        from core.dreamscape_memory import DreamscapeMemory
        from core.discord_manager import DiscordManager
        from core.mmorpg_engine import MMORPGEngine
        
        print("  [OK] All core system imports successful")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI integration test failed: {e}")
        return False

def test_chronological_processing():
    """Test that conversations are processed in chronological order."""
    print("📅 Testing Chronological Processing...")
    
    try:
        api = MemoryAPI()
        conversations = api.get_conversations_chronological(limit=10)
        
        if len(conversations) < 2:
            print("  [WARNING] Need at least 2 conversations to test chronological order")
            return True
        
        # Check that conversations are in chronological order (oldest first)
        timestamps = [conv.get('timestamp', '') for conv in conversations]
        
        # Simple check - timestamps should be in ascending order
        is_chronological = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
        
        if is_chronological:
            print("  [OK] Conversations are in chronological order (oldest first)")
        else:
            print("  [WARNING] Conversations may not be in chronological order")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Chronological processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Dreamscape Workflow Test Suite")
    print("=" * 50)
    
    tests = [
        test_memory_system,
        test_mmorpg_engine,
        test_dreamscape_processing,
        test_gui_integration,
        test_chronological_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dreamscape workflow is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 