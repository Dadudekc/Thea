#!/usr/bin/env python3
"""
Debug Scraper Script
===================

Helps debug and fix the ChatGPT scraper to get all 1,300+ conversations.
"""

import sys
import json
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.chatgpt_scraper import ChatGPTScraper
from scrapers.browser_manager import BrowserManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_list_manager import ConversationListManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_scraper():
    """Debug the scraper step by step."""
    print("🔍 Debugging ChatGPT Scraper")
    print("=" * 50)
    
    try:
        # Step 1: Initialize browser
        print("1. Initializing browser...")
        browser_manager = BrowserManager(headless=False, use_undetected=True)
        driver = browser_manager.create_driver()
        
        if not driver:
            print("❌ Failed to create driver")
            return False
        
        print("✅ Browser initialized")
        
        # Step 2: Navigate to ChatGPT
        print("2. Navigating to ChatGPT...")
        driver.get("https://chat.openai.com/")
        print("✅ Navigated to ChatGPT")
        
        # Step 3: Check if logged in
        print("3. Checking login status...")
        login_handler = LoginHandler()
        is_logged_in = login_handler.is_logged_in(driver)
        
        if is_logged_in:
            print("✅ Already logged in")
        else:
            print("❌ Not logged in - you'll need to log in manually")
            print("   Please log in to ChatGPT in the browser window that opened")
            input("   Press Enter when you're logged in...")
            
            # Check again after manual login
            is_logged_in = login_handler.is_logged_in(driver)
            if not is_logged_in:
                print("❌ Still not logged in")
                return False
            print("✅ Login successful")
        
        # Step 4: Try to get conversations
        print("4. Attempting to get conversations...")
        conversation_manager = ConversationListManager(timeout=30)
        conversations = conversation_manager.get_conversation_list(driver)
        
        if conversations and len(conversations) > 2:  # More than demo data
            print(f"✅ Found {len(conversations)} conversations!")
            
            # Save conversations
            output_file = "data/all_conversations_debug.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved conversations to {output_file}")
            
            # Show first few conversations
            print("\n📋 First 5 conversations:")
            for i, conv in enumerate(conversations[:5], 1):
                print(f"  {i}. {conv.get('title', 'Untitled')} ({conv.get('id', 'N/A')})")
            
            if len(conversations) > 5:
                print(f"  ... and {len(conversations) - 5} more")
            
            return True
        else:
            print("❌ No conversations found or only demo data")
            print("   This might be due to:")
            print("   - ChatGPT's UI has changed")
            print("   - Page hasn't loaded completely")
            print("   - Need to scroll to load more conversations")
            
            # Try to help user
            print("\n💡 Suggestions:")
            print("   1. Make sure you're on the main ChatGPT page")
            print("   2. Try scrolling down to load more conversations")
            print("   3. Check if there are any popups or overlays")
            print("   4. Try refreshing the page")
            
            input("   Press Enter to continue debugging...")
            return False
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        return False
    finally:
        if 'driver' in locals():
            browser_manager.close_driver()

def main():
    """Main function."""
    success = debug_scraper()
    
    if success:
        print("\n✅ Debugging completed successfully!")
        print("💡 You can now run the ingestion script with the new conversation data.")
    else:
        print("\n❌ Debugging failed")
        print("💡 You may need to:")
        print("   - Check your internet connection")
        print("   - Make sure ChatGPT is accessible")
        print("   - Try running the scraper manually")

if __name__ == "__main__":
    main()
 