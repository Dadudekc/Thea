#!/usr/bin/env python3
"""
Test Scraper Script
==================

Simple test to see what's happening with the ChatGPT scraper.
"""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.browser_manager import BrowserManager
from scrapers.login_handler import LoginHandler
from selenium.webdriver.common.by import By

def test_chatgpt_page():
    """Test what we can find on the ChatGPT page."""
    print("🔍 Testing ChatGPT Page")
    print("=" * 50)
    
    browser_manager = BrowserManager(headless=False, use_undetected=True)
    driver = None
    
    try:
        # Create driver
        driver = browser_manager.create_driver()
        if not driver:
            print("❌ Failed to create driver")
            return False
        
        print("✅ Driver created")
        
        # Navigate to ChatGPT
        print("2. Navigating to ChatGPT...")
        driver.get("https://chat.openai.com/")
        time.sleep(5)
        print("✅ Navigated to ChatGPT")
        
        # Force manual login check
        print("3. Please log in manually...")
        print("   A browser window should have opened. Please log in to ChatGPT.")
        print("   Look for the login page and enter your credentials.")
        input("   Press Enter when you're logged in and can see the main chat interface...")
        
        # Give extra time for page to load after login
        print("4. Waiting for page to load after login...")
        time.sleep(5)
        
        # Look for conversation elements
        print("5. Looking for conversation elements...")
        
        # Try different selectors
        selectors = [
            "//a[contains(@href, '/c/')]",
            "//div[contains(@class, 'conversation')]",
            "//nav//a[contains(@href, '/c/')]",
            "//div[contains(@class, 'sidebar')]//a",
            "//a[contains(@href, '/c/') and contains(@class, 'conversation')]",
            "//div[contains(@class, 'conversation-item')]",
            "//div[contains(@class, 'conversation')]//a[contains(@href, '/c/')]"
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"  Selector {i}: {selector}")
                print(f"    Found {len(elements)} elements")
                
                if elements:
                    # Show first few elements
                    for j, elem in enumerate(elements[:3]):
                        try:
                            href = elem.get_attribute('href')
                            text = elem.text.strip()
                            print(f"    Element {j+1}: href='{href}', text='{text}'")
                        except:
                            print(f"    Element {j+1}: [error reading element]")
                    
                    if len(elements) > 3:
                        print(f"    ... and {len(elements) - 3} more elements")
                    
                    if '/c/' in str(elements[0].get_attribute('href')):
                        print(f"    ✅ This selector looks promising!")
                        break
                        
            except Exception as e:
                print(f"    Error: {e}")
        
        # Check page source for conversation-related content
        print("\n6. Checking page source...")
        page_source = driver.page_source
        if '/c/' in page_source:
            print("✅ Found '/c/' in page source - conversations are present")
            
            # Count conversation URLs
            import re
            conversation_urls = re.findall(r'https://chat\.openai\.com/c/[a-zA-Z0-9-]+', page_source)
            unique_urls = list(set(conversation_urls))
            print(f"✅ Found {len(unique_urls)} unique conversation URLs in page source")
            
            if len(unique_urls) > 10:
                print("✅ This looks like we have many conversations!")
                return True
        else:
            print("❌ No '/c/' found in page source")
        
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        if driver:
            browser_manager.close_driver()

def main():
    """Main function."""
    success = test_chatgpt_page()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("💡 The page seems to have conversations. The scraper should work.")
    else:
        print("\n❌ Test failed")
        print("💡 There might be an issue with the page or selectors.")

if __name__ == "__main__":
    main()
