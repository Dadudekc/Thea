#!/usr/bin/env python3
"""
Simple test for cookie-based login using regular Selenium
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor

def main():
    print("🚀 Testing Cookie-Based Login (Direct Selenium)...")
    
    try:
        # Create regular Chrome driver directly
        print("📱 Initializing browser...")
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        print("✅ Browser created successfully")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Initialize cookie manager and login handler
        print("🍪 Initializing cookie manager...")
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        login_handler = LoginHandler()
        
        # Use the new method that handles cookies properly
        print("🔐 Attempting login with cookie management...")
        if login_handler.ensure_login_with_cookies(driver, cookie_manager, manual_timeout=60):
            print("✅ Login successful!")
            
            # Extract conversations
            print("📋 Extracting conversations...")
            extractor = ConversationExtractor()
            conversations = extractor.get_conversation_list(driver)
            
            print(f"✅ Found {len(conversations)} conversations")
            
            if conversations:
                print("✅ Real conversations found!")
                
                # Save conversations to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'data/conversations/cookie_login_{timestamp}.json'
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(conversations, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Saved {len(conversations)} conversations to {output_file}")
                
                # Show first few conversations
                print("\n📝 First 5 conversations:")
                for i, conv in enumerate(conversations[:5]):
                    print(f"  {i+1}. {conv.get('title', 'No title')} (ID: {conv.get('id', 'No ID')})")
                
            else:
                print("❌ No conversations found even after login")
                print("This might indicate:")
                print("  - Selectors need updating")
                print("  - Page structure has changed")
                print("  - No conversations exist")
        else:
            print("❌ Login failed - could not authenticate")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("🎉 Cookie-based login test completed!")
    return 0

if __name__ == "__main__":
    exit(main()) 