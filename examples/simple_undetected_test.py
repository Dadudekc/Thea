#!/usr/bin/env python3
"""
Simple undetected Chrome test for version 3.5.3
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

def main():
    print("🚀 Simple Undetected Chrome Test")
    print("=" * 35)
    
    try:
        # Create driver with minimal parameters
        print("📱 Creating undetected Chrome driver...")
        
        # For version 3.5.5, specify the Chrome version to match installed browser
        driver = uc.Chrome(version_main=137)  # Match your Chrome version 137
        
        print("✅ Undetected Chrome driver created successfully")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Wait for page to load
        time.sleep(5)
        
        # Show page title
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        print("\n⚠️  MANUAL LOGIN REQUIRED")
        print("=" * 30)
        print("Please log in manually in the browser window.")
        print("The undetected Chrome should bypass anti-bot detection.")
        print("Once logged in, come back here and press Enter.")
        print("=" * 30)
        
        input("Press Enter when you are logged in...")
        
        print("✅ Manual login completed!")
        
        # Take screenshot
        driver.save_screenshot('undetected_login_success.png')
        print("📸 Screenshot saved as 'undetected_login_success.png'")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
        print("\n🎉 Undetected Chrome test completed!")
        print("💡 If you were able to log in, undetected Chrome is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 