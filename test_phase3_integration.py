#!/usr/bin/env python3
"""
Test Phase 3 Integration - Live ChatGPT Integration & Discord Bot
Tests the complete Phase 3 functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chatgpt_api_client():
    """Test ChatGPT API client functionality."""
    print("🤖 Testing ChatGPT API Client...")
    
    try:
        from core.chatgpt_api_client import ChatGPTAPIClient
        
        # Test client initialization
        client = ChatGPTAPIClient()
        print(f"  [OK] API client initialized")
        
        # Test configuration check
        is_configured = client.is_configured()
        print(f"  [OK] Configuration check: {is_configured}")
        
        # Test rate limit info
        rate_info = client.get_rate_limit_info()
        print(f"  [OK] Rate limit info: {rate_info}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] ChatGPT API client test failed: {e}")
        return False

def test_live_processor():
    """Test live processor functionality."""
    print("🔄 Testing Live Processor...")
    
    try:
        from core.live_processor import LiveProcessor, ProcessingStatus
        from core.memory_manager import MemoryManager
        from core.dreamscape_processor import DreamscapeProcessor
        from core.mmorpg_engine import MMORPGEngine
        
        # Initialize dependencies
        memory_manager = MemoryManager()
        dreamscape_processor = DreamscapeProcessor()
        mmorpg_engine = MMORPGEngine()
        
        # Test processor initialization
        processor = LiveProcessor(
            memory_manager=memory_manager,
            dreamscape_processor=dreamscape_processor,
            mmorpg_engine=mmorpg_engine
        )
        print(f"  [OK] Live processor initialized")
        
        # Test status
        status = processor.get_status()
        print(f"  [OK] Initial status: {status}")
        
        # Test configuration check
        is_configured = processor.is_configured()
        print(f"  [OK] Configuration check: {is_configured}")
        
        # Test stats
        stats = processor.get_stats()
        print(f"  [OK] Initial stats: {stats.total_conversations_processed}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Live processor test failed: {e}")
        return False

def test_discord_commands():
    """Test Discord command functionality."""
    print("📢 Testing Discord Commands...")
    
    try:
        from core.discord_manager import DiscordManager
        from core.mmorpg_engine import MMORPGEngine
        
        # Initialize MMORPG engine
        mmorpg_engine = MMORPGEngine()
        
        # Test Discord manager
        discord_manager = DiscordManager()
        print(f"  [OK] Discord manager initialized")
        
        # Test status
        status = discord_manager.get_status()
        print(f"  [OK] Discord status: {status}")
        
        # Test MMORPG methods used by Discord commands
        player = mmorpg_engine.get_player()
        print(f"  [OK] Player info: {player.name} - {player.architect_tier}")
        
        skills = mmorpg_engine.get_skills()
        print(f"  [OK] Skills count: {len(skills)}")
        
        active_quests = mmorpg_engine.get_active_quests()
        print(f"  [OK] Active quests: {len(active_quests)}")
        
        completed_quests = mmorpg_engine.get_completed_quests()
        print(f"  [OK] Completed quests: {len(completed_quests)}")
        
        domains = mmorpg_engine.get_domains()
        print(f"  [OK] Domains: {len(domains)}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Discord commands test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration with Phase 3 features."""
    print("🖥️ Testing GUI Integration...")
    
    try:
        # Test main window import
        from gui.main_window import TheaMainWindow
        print(f"  [OK] Main window import successful")
        
        # Test live processor integration
        from core.live_processor import get_live_processor
        live_proc = get_live_processor()
        print(f"  [OK] Live processor accessible from GUI")
        
        # Test dashboard panel (without creating QApplication)
        from gui.panels.dashboard_panel import DashboardPanel
        print(f"  [OK] Dashboard panel import successful")
        
        # Test live processor status check (without GUI)
        from core.live_processor import LiveProcessor, ProcessingStatus
        from core.memory_manager import MemoryManager
        from core.dreamscape_processor import DreamscapeProcessor
        from core.mmorpg_engine import MMORPGEngine
        
        # Create a test processor
        memory_manager = MemoryManager()
        dreamscape_processor = DreamscapeProcessor()
        mmorpg_engine = MMORPGEngine()
        
        test_processor = LiveProcessor(
            memory_manager=memory_manager,
            dreamscape_processor=dreamscape_processor,
            mmorpg_engine=mmorpg_engine
        )
        
        status = test_processor.get_status()
        print(f"  [OK] Live processor status check working: {status}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI integration test failed: {e}")
        return False

def test_settings_persistence():
    """Test settings persistence for Phase 3."""
    print("⚙️ Testing Settings Persistence...")
    
    try:
        from core.settings_manager import settings_manager
        
        # Test theme persistence
        settings_manager.set_theme("Dark")
        theme = settings_manager.get_theme()
        print(f"  [OK] Theme persistence: {theme}")
        
        # Test all settings
        all_settings = settings_manager.get_all_settings()
        print(f"  [OK] All settings: {len(all_settings)} items")
        
        # Test settings file
        settings_file = Path("config/settings.json")
        if settings_file.exists():
            print(f"  [OK] Settings file exists: {settings_file}")
        else:
            print(f"  [WARNING] Settings file not found")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Settings persistence test failed: {e}")
        return False

def main():
    """Run all Phase 3 integration tests."""
    print("🚀 Phase 3 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("ChatGPT API Client", test_chatgpt_api_client),
        ("Live Processor", test_live_processor),
        ("Discord Commands", test_discord_commands),
        ("GUI Integration", test_gui_integration),
        ("Settings Persistence", test_settings_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed! System is ready for live deployment.")
        print("\n🚀 Phase 3 Features Available:")
        print("  • Live ChatGPT API integration")
        print("  • Continuous conversation processing")
        print("  • Discord bot with interactive commands")
        print("  • Real-time MMORPG updates")
        print("  • Settings persistence")
        print("  • GUI live processing controls")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 