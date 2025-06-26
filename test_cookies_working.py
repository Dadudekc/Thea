#!/usr/bin/env python3
"""
Test if saved cookies are working for automatic login
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import undetected_chromedriver as uc
    print("✅ undetected-chromedriver available")
except ImportError:
    print("❌ undetected-chromedriver not available")
    sys.exit(1)

from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler

def main():
    print("🍪 Testing Saved Cookies")
    print("=" * 30)
    
    try:
        # Create driver
        print("📱 Creating undetected Chrome driver...")
        driver = uc.Chrome(version_main=137)
        print("✅ Driver created")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Wait for page to load
        time.sleep(3)
        
        # Initialize managers
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        login_handler = LoginHandler()
        
        # Check if cookies exist
        if cookie_manager.cookie_file_exists():
            print("✅ Cookie file exists")
            print("🔄 Loading saved cookies...")
            cookie_manager.load_cookies(driver)
            print("✅ Cookies loaded")
            
            # Wait for cookies to take effect
            time.sleep(3)
            
            # Check login status
            print("🔍 Checking if cookies worked...")
            if login_handler.is_logged_in(driver):
                print("🎉 SUCCESS! Cookies are working - automatically logged in!")
                
                # Take screenshot to show we're logged in
                driver.save_screenshot('cookies_working.png')
                print("📸 Screenshot saved as 'cookies_working.png'")
                
                # Show page title and URL
                print(f"📄 Page title: {driver.title}")
                print(f"🌐 Current URL: {driver.current_url}")
                
            else:
                print("❌ Cookies didn't work - still not logged in")
                print("This might mean:")
                print("  - Cookies are expired")
                print("  - ChatGPT changed their authentication")
                print("  - Need to log in manually again")
                
                # Take screenshot to see what's on the page
                driver.save_screenshot('cookies_not_working.png')
                print("📸 Screenshot saved as 'cookies_not_working.png'")
                
        else:
            print("❌ No cookie file found")
            print("You need to run the manual login script first")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 