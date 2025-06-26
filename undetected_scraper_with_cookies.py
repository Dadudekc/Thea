#!/usr/bin/env python3
"""
Undetected Chrome Scraper with Cookie Management
Uses undetected-chromedriver to bypass anti-bot detection and save cookies for future use.
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
    print("🚀 Undetected Chrome Scraper with Cookie Management")
    print("=" * 55)
    
    try:
        # Create undetected Chrome driver
        print("📱 Creating undetected Chrome driver...")
        driver = uc.Chrome(version_main=137)  # Match your Chrome version
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
        
        # Load existing cookies first
        if cookie_manager.cookie_file_exists():
            print("🔄 Loading saved cookies...")
            cookie_manager.load_cookies(driver)
            time.sleep(2)
        
        # Check login status
        print("🔍 Checking login status...")
        if login_handler.is_logged_in(driver):
            print("✅ Already logged in using saved cookies!")
        else:
            print("❌ Not logged in")
            print("\n⚠️  MANUAL LOGIN REQUIRED")
            print("=" * 40)
            print("Please log in manually in the browser window.")
            print("The undetected Chrome should bypass anti-bot detection.")
            print("Once logged in and you can see your conversations, come back here.")
            print("=" * 40)
            
            # Wait for manual login
            manual_timeout = 180  # 3 minutes
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
        
        # Save cookies after successful login
        print("🍪 Saving cookies for future use...")
        cookie_manager.save_cookies(driver)
        print("✅ Cookies saved successfully")
        
        # Extract conversations
        print("📋 Extracting conversations...")
        extractor = ConversationExtractor()
        conversations = extractor.get_conversation_list(driver)
        
        if conversations:
            print(f"✅ Successfully found {len(conversations)} conversations!")
            
            # Save conversations to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/conversations/undetected_scraper_{timestamp}.json'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved conversations to {output_file}")
            
            # Show first few conversations
            print("\n📝 First 10 conversations:")
            for i, conv in enumerate(conversations[:10]):
                title = conv.get('title', 'No title')
                conv_id = conv.get('id', 'No ID')
                print(f"  {i+1:2d}. {title} (ID: {conv_id})")
            
            if len(conversations) > 10:
                print(f"  ... and {len(conversations) - 10} more conversations")
            
        else:
            print("❌ No conversations found")
            print("This might indicate:")
            print("  - Selectors need updating")
            print("  - Page structure has changed")
            print("  - No conversations exist")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
        print("\n🎉 Undetected Chrome scraper completed!")
        print("💡 The undetected Chrome successfully bypassed anti-bot detection!")
        print("💾 Cookies have been saved for future automated use!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 