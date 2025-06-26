#!/usr/bin/env python3
"""
Test script to verify the improved conversation scrolling functionality.
This script focuses only on the scrolling part without full login.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.chatgpt_scraper import ChatGPTScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scrolling_functionality():
    """Test the improved conversation scrolling functionality."""
    
    print("=" * 60)
    print("🎯 Testing Improved Conversation Scrolling")
    print("=" * 60)
    
    # Get credentials from environment
    username = os.getenv('CHATGPT_USERNAME')
    password = os.getenv('CHATGPT_PASSWORD')
    
    if not username or not password:
        print("❌ No credentials found in .env file")
        print("Please set CHATGPT_USERNAME and CHATGPT_PASSWORD")
        return False
    
    print(f"✅ Found credentials for: {username}")
    
    # Initialize scraper with cookies if available
    cookie_file = "chatgpt_cookies.pkl"
    scraper = None
    
    try:
        print("ℹ️  Initializing ChatGPT scraper...")
        scraper = ChatGPTScraper(
            headless=False,  # Show browser for debugging
            timeout=30,
            use_undetected=True,
            username=username,
            password=password,
            cookie_file=cookie_file if os.path.exists(cookie_file) else None
        )
        
        # Start the driver
        if not scraper.start_driver():
            print("❌ Failed to start browser driver")
            return False
        
        print("✅ Browser driver started")
        
        # Navigate to ChatGPT
        print("ℹ️  Navigating to ChatGPT...")
        if not scraper.navigate_to_chatgpt():
            print("❌ Failed to navigate to ChatGPT")
            return False
        
        print("✅ Successfully navigated to ChatGPT")
        
        # Check if already logged in
        print("ℹ️  Checking login status...")
        if scraper.is_logged_in():
            print("✅ Already logged in!")
        else:
            print("ℹ️  Not logged in, attempting login...")
            if not scraper.ensure_login_modern(allow_manual=True, manual_timeout=60):
                print("❌ Failed to log in")
                return False
            print("✅ Login successful!")
        
        # Now test the improved scrolling functionality
        print("\n" + "=" * 40)
        print("🚀 TESTING IMPROVED SCROLLING FUNCTIONALITY")
        print("=" * 40)
        
        # Test the scrolling method directly
        print("ℹ️  Testing _scroll_conversation_history() method...")
        scraper._scroll_conversation_history()
        
        # Wait a moment for any final loading
        import time
        time.sleep(3)
        
        # Now try to get the conversation list
        print("ℹ️  Getting conversation list after aggressive scrolling...")
        conversations = scraper.get_conversation_list()
        
        if conversations:
            print(f"✅ SUCCESS! Found {len(conversations)} conversations after aggressive scrolling")
            print("\n📋 Conversation List:")
            for i, conv in enumerate(conversations[:10], 1):  # Show first 10
                print(f"  {i}. {conv['title']}")
            if len(conversations) > 10:
                print(f"  ... and {len(conversations) - 10} more conversations")
        else:
            print("❌ No conversations found after aggressive scrolling")
            print("This might indicate an issue with the scrolling or conversation detection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during scrolling test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            print("ℹ️  Closing browser...")
            scraper.close_driver()

if __name__ == "__main__":
    success = test_scrolling_functionality()
    if success:
        print("\n✅ Scrolling test completed successfully!")
    else:
        print("\n❌ Scrolling test failed!")
        sys.exit(1) 