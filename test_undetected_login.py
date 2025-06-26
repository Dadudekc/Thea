#!/usr/bin/env python3
"""
Test undetected Chrome login
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import undetected_chromedriver as uc
    print("✅ undetected-chromedriver available")
except ImportError:
    print("❌ undetected-chromedriver not available")
    print("Please install it with: pip install undetected-chromedriver")
    sys.exit(1)

from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor

def main():
    print("🚀 Undetected Chrome Login Test")
    print("=" * 40)
    
    try:
        # Create undetected Chrome driver with minimal options
        print("📱 Creating undetected Chrome driver...")
        
        # Use simple options to avoid compatibility issues
        driver = uc.Chrome(
            headless=False,  # Always show browser for manual login
            use_subprocess=True,
            version_main=None  # Auto-detect Chrome version
        )
        
        print("✅ Undetected Chrome driver created successfully")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Wait for page to load
        time.sleep(3)
        
        # Initialize managers
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        login_handler = LoginHandler()
        
        # Check login status
        print("🔍 Checking login status...")
        if login_handler.is_logged_in(driver):
            print("✅ Already logged in!")
        else:
            print("❌ Not logged in")
            print("\n⚠️  MANUAL LOGIN REQUIRED")
            print("=" * 30)
            print("Please log in manually in the browser window.")
            print("The undetected Chrome should bypass anti-bot detection.")
            print("Once logged in, come back here.")
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
            output_file = f'data/conversations/undetected_login_{timestamp}.json'
            
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
        
        print("\n🎉 Undetected Chrome login test completed!")
        print("💡 The undetected Chrome should have bypassed anti-bot detection!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 