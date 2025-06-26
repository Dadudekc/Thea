#!/usr/bin/env python3
"""
Manual Login and Cookie Saving Script
Prompts user to log in manually and saves cookies for future automated use.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor

def main():
    print("🚀 Manual Login + Cookie Saving Script")
    print("=" * 50)
    
    try:
        # Create browser
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
        
        # Initialize managers
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        login_handler = LoginHandler()
        
        # Check if we're already logged in
        print("🔍 Checking login status...")
        if login_handler.is_logged_in(driver):
            print("✅ Already logged in!")
        else:
            print("❌ Not logged in")
            print("\n⚠️  MANUAL LOGIN REQUIRED")
            print("=" * 30)
            print("Please log in manually in the browser window that just opened.")
            print("Once you're logged in and can see your conversations, come back here.")
            print("=" * 30)
            
            # Wait for manual login
            manual_timeout = 120  # 2 minutes
            start_time = time.time()
            
            while time.time() - start_time < manual_timeout:
                if login_handler.is_logged_in(driver):
                    print("✅ Login detected! You're now logged in.")
                    break
                time.sleep(2)
                remaining = int(manual_timeout - (time.time() - start_time))
                print(f"⏰ Waiting for login... {remaining}s remaining")
            else:
                print("❌ Login timeout - please try again")
                driver.quit()
                return 1
        
        # Save cookies
        print("🍪 Saving cookies for future use...")
        cookie_manager.save_cookies(driver)
        print("✅ Cookies saved successfully")
        
        # Test conversation extraction
        print("📋 Testing conversation extraction...")
        extractor = ConversationExtractor()
        conversations = extractor.get_conversation_list(driver)
        
        if conversations:
            print(f"✅ Successfully found {len(conversations)} conversations!")
            
            # Save conversations to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/conversations/manual_login_{timestamp}.json'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved conversations to {output_file}")
            
            # Show first few conversations
            print("\n📝 First 5 conversations:")
            for i, conv in enumerate(conversations[:5]):
                title = conv.get('title', 'No title')
                conv_id = conv.get('id', 'No ID')
                print(f"  {i+1}. {title} (ID: {conv_id})")
            
        else:
            print("❌ No conversations found")
            print("This might indicate:")
            print("  - Selectors need updating")
            print("  - Page structure has changed")
            print("  - No conversations exist")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
        print("\n🎉 Manual login completed successfully!")
        print("💡 Next time you run the scraper, it should use the saved cookies automatically!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 