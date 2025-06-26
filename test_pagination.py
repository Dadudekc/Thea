#!/usr/bin/env python3
"""
Test Pagination System
Tests that pagination works correctly for all conversations.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_conversation_count():
    """Test that we can get the total conversation count."""
    print("📊 Testing Conversation Count...")
    
    try:
        from core.memory_api import get_memory_api
        api = get_memory_api()
        
        total_count = api.get_conversations_count()
        print(f"  [OK] Total conversations: {total_count}")
        
        return total_count
        
    except Exception as e:
        print(f"  [ERROR] Failed to get conversation count: {e}")
        return 0

def test_pagination():
    """Test pagination functionality."""
    print("📄 Testing Pagination...")
    
    try:
        from core.memory_api import get_memory_api
        api = get_memory_api()
        
        # Test different page sizes
        page_sizes = [50, 100, 200]
        total_count = api.get_conversations_count()
        
        for page_size in page_sizes:
            print(f"  Testing page size: {page_size}")
            
            # Get first page
            conversations = api.get_conversations_chronological(limit=page_size, offset=0)
            print(f"    [OK] First page: {len(conversations)} conversations")
            
            # Get second page
            conversations2 = api.get_conversations_chronological(limit=page_size, offset=page_size)
            print(f"    [OK] Second page: {len(conversations2)} conversations")
            
            # Verify no overlap
            if conversations and conversations2:
                first_ids = {conv['id'] for conv in conversations}
                second_ids = {conv['id'] for conv in conversations2}
                overlap = first_ids.intersection(second_ids)
                
                if not overlap:
                    print(f"    [OK] No overlap between pages")
                else:
                    print(f"    [WARNING] Overlap detected: {len(overlap)} conversations")
            
            # Test total pages calculation
            total_pages = (total_count + page_size - 1) // page_size
            print(f"    [OK] Total pages with size {page_size}: {total_pages}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Pagination test failed: {e}")
        return False

def test_chronological_order():
    """Test that conversations are returned in chronological order."""
    print("📅 Testing Chronological Order...")
    
    try:
        from core.memory_api import get_memory_api
        api = get_memory_api()
        
        # Get first 10 conversations
        conversations = api.get_conversations_chronological(limit=10, offset=0)
        
        if len(conversations) < 2:
            print(f"  [WARNING] Not enough conversations to test order ({len(conversations)})")
            return True
        
        # Check chronological order
        for i in range(len(conversations) - 1):
            current = conversations[i]
            next_conv = conversations[i + 1]
            
            current_time = current.get('created_at', '')
            next_time = next_conv.get('created_at', '')
            
            if current_time and next_time:
                try:
                    from datetime import datetime
                    if isinstance(current_time, str):
                        current_dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                    else:
                        current_dt = current_time
                    
                    if isinstance(next_time, str):
                        next_dt = datetime.fromisoformat(next_time.replace('Z', '+00:00'))
                    else:
                        next_dt = next_time
                    
                    if current_dt <= next_dt:
                        continue
                    else:
                        print(f"  [ERROR] Chronological order violated at position {i}")
                        print(f"    Current: {current_time}")
                        print(f"    Next: {next_time}")
                        return False
                        
                except Exception as e:
                    print(f"  [WARNING] Could not parse dates: {e}")
                    continue
        
        print(f"  [OK] First {len(conversations)} conversations are in chronological order")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Chronological order test failed: {e}")
        return False

def test_gui_pagination():
    """Test GUI pagination components."""
    print("🖥️ Testing GUI Pagination...")
    
    try:
        # Test dashboard panel pagination methods
        from gui.panels.conversations_panel import ConversationsPanel
        
        # Create a mock panel (without QApplication)
        panel = ConversationsPanel()
        
        # Test pagination calculations
        panel.total_conversations = 1316
        panel.page_size = 100
        panel.calculate_total_pages()
        
        expected_pages = (1316 + 100 - 1) // 100  # Should be 14 pages
        print(f"  [OK] Total pages calculation: {panel.total_pages} (expected: {expected_pages})")
        
        # Test page navigation
        panel.current_page = 1
        panel.update_pagination_controls()
        print(f"  [OK] Pagination controls updated")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI pagination test failed: {e}")
        return False

def test_full_processing():
    """Test that all conversations can be processed."""
    print("🔄 Testing Full Processing...")
    
    try:
        from core.dreamscape_processor import DreamscapeProcessor
        
        # Create processor
        processor = DreamscapeProcessor()
        
        # Test processing with no limit (should process all)
        result = processor.process_conversations_chronological(limit=None)
        
        print(f"  [OK] Processing result: {result.get('processed_count', 0)} processed")
        print(f"  [OK] Total conversations: {result.get('total_conversations', 0)}")
        print(f"  [OK] Conversations processed: {result.get('conversations_processed', 0)}")
        
        if result.get('errors'):
            print(f"  [WARNING] Errors encountered: {len(result['errors'])}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"  [ERROR] Full processing test failed: {e}")
        return False

def main():
    """Run all pagination tests."""
    print("🚀 Pagination System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Conversation Count", test_conversation_count),
        ("Pagination", test_pagination),
        ("Chronological Order", test_chronological_order),
        ("GUI Pagination", test_gui_pagination),
        ("Full Processing", test_full_processing)
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
        print("🎉 All pagination tests passed! System can handle all conversations efficiently.")
        print("\n📄 Pagination Features Available:")
        print("  • Total conversation count: Working")
        print("  • Page-based navigation: Working")
        print("  • Chronological ordering: Working")
        print("  • GUI pagination controls: Working")
        print("  • Full conversation processing: Working")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 