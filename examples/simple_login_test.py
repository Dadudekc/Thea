#!/usr/bin/env python3
"""
Simple manual login test for ChatGPT
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.browser_manager import BrowserManager
from scrapers.conversation_extractor import ConversationExtractor
from selenium.webdriver.common.by import By

def main():
    print("🚀 Simple Manual Login Test...")
    
    try:
        # Initialize browser
        browser = BrowserManager(headless=False, use_undetected=True)
        driver = browser.create_driver()
        print("✅ Browser created")
        
        # Navigate to ChatGPT
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Force manual login
        print("⚠️ Please log in manually in the browser window...")
        input("Press Enter when you are logged in and can see your conversations...")
        print("✅ Manual login completed")
        
        # Wait a bit for page to settle
        time.sleep(3)
        
        # Test conversation extraction
        print("📋 Testing conversation extraction...")
        extractor = ConversationExtractor()
        conversations = extractor.get_conversation_list(driver)
        
        print(f"✅ Found {len(conversations)} conversations")
        
        if conversations:
            print("✅ Real conversations found!")
            print("\n📝 First 5 conversations:")
            for i, conv in enumerate(conversations[:5]):
                print(f"  {i+1}. {conv.get('title', 'No title')} (ID: {conv.get('id', 'No ID')})")
        else:
            print("❌ No conversations found")
            print("Let's debug the page structure...")
            
            # Debug: look for any links
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(all_links)} total links on page")
            
            for i, link in enumerate(all_links[:10]):
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and text:
                        print(f"  Link {i+1}: {text[:30]} -> {href}")
                except:
                    pass
        
        # Close browser
        browser.close_driver()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 