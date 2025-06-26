#!/usr/bin/env python3
"""
Manual login test for ChatGPT scraper
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.browser_manager import BrowserManager
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor

def main():
    print("🚀 Testing Manual Login ChatGPT Scraper...")
    
    try:
        # Initialize browser manager with undetected Chrome
        print("📱 Initializing browser...")
        browser = BrowserManager(headless=False, use_undetected=True)
        driver = browser.create_driver()
        print("✅ Browser created successfully")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Try to load cookies first
        print("🍪 Loading cookies...")
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        cookie_manager.load_cookies(driver)
        print("✅ Cookies loaded")
        
        # Check if we're logged in
        print("🔐 Checking login status...")
        login_handler = LoginHandler()
        
        if login_handler.is_logged_in(driver):
            print("✅ Successfully logged in using cookies!")
        else:
            print("❌ Not logged in - cookies may be expired")
            print("⚠️ Please log in manually in the browser window...")
            input("Press Enter when you are logged in...")
            print("✅ Manual login completed")
        
        # Extract conversations
        print("📋 Extracting conversations...")
        extractor = ConversationExtractor()
        conversations = extractor.get_conversation_list(driver)
        
        print(f"✅ Found {len(conversations)} conversations")
        
        if conversations:
            print("✅ Real conversations found!")
            
            # Save conversations to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/conversations/manual_login_{timestamp}.json'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(conversations)} conversations to {output_file}")
            
            # Show first few conversations
            print("\n📝 First 5 conversations:")
            for i, conv in enumerate(conversations[:5]):
                print(f"  {i+1}. {conv.get('title', 'No title')} (ID: {conv.get('id', 'No ID')})")
            
            # Save cookies for next time
            cookie_manager.save_cookies(driver)
            print("✅ Cookies saved for future use")
            
        else:
            print("❌ No conversations found even after login")
            print("This might indicate:")
            print("  - Selectors need updating")
            print("  - Page structure has changed")
            print("  - No conversations exist")
        
        # Close browser
        browser.close_driver()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("🎉 Manual login test completed!")
    return 0

if __name__ == "__main__":
    exit(main()) 