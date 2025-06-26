#!/usr/bin/env python3
"""
Debug script to inspect ChatGPT page structure and find correct selectors
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.browser_manager import BrowserManager
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from selenium.webdriver.common.by import By

def debug_page_structure():
    print("🔍 Debugging ChatGPT page structure...")
    
    try:
        # Initialize browser
        browser = BrowserManager(headless=False, use_undetected=True)
        driver = browser.create_driver()
        print("✅ Browser created")
        
        # Navigate to ChatGPT
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Load cookies
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        cookie_manager.load_cookies(driver)
        print("✅ Cookies loaded")
        
        # Check login status
        login_handler = LoginHandler()
        if not login_handler.is_logged_in(driver):
            print("❌ Not logged in - please log in manually")
            input("Press Enter when logged in...")
        
        print("✅ Logged in successfully")
        
        # Wait for page to load
        time.sleep(5)
        
        # Debug sidebar elements
        print("\n🔍 Looking for sidebar elements...")
        sidebar_selectors = [
            "//nav[contains(@class, 'sidebar')]",
            "//div[contains(@class, 'sidebar')]",
            "//aside[contains(@class, 'sidebar')]",
            "//div[contains(@class, 'conversations')]",
            "//nav[contains(@class, 'conversations')]",
            "//div[contains(@class, 'flex-col')]",
            "//nav",
            "//aside"
        ]
        
        for selector in sidebar_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            print(f"  Element {i+1}: class='{elem.get_attribute('class')}', text='{elem.text[:50]}...'")
                        except:
                            print(f"  Element {i+1}: [error getting attributes]")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        # Debug conversation links
        print("\n🔍 Looking for conversation links...")
        link_selectors = [
            "//a[contains(@href, '/c/')]",
            "//a[contains(@href, 'chat.openai.com/c/')]",
            "//a[contains(@href, 'c/')]",
            "//div[contains(@class, 'conversation')]//a",
            "//nav//a",
            "//div[contains(@class, 'flex-col')]//a",
            "//a"
        ]
        
        for selector in link_selectors:
            try:
                links = driver.find_elements(By.XPATH, selector)
                if links:
                    print(f"✅ Found {len(links)} links with selector: {selector}")
                    for i, link in enumerate(links[:5]):  # Show first 5
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            print(f"  Link {i+1}: href='{href}', text='{text[:30]}...'")
                        except:
                            print(f"  Link {i+1}: [error getting attributes]")
                else:
                    print(f"❌ No links found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        # Debug page source structure
        print("\n🔍 Page structure analysis...")
        page_source = driver.page_source
        
        # Look for conversation-related patterns
        if 'conversation' in page_source.lower():
            print("✅ Found 'conversation' in page source")
        else:
            print("❌ No 'conversation' found in page source")
            
        if '/c/' in page_source:
            print("✅ Found '/c/' URLs in page source")
        else:
            print("❌ No '/c/' URLs found in page source")
        
        # Save page source for manual inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("✅ Saved page source to debug_page_source.html")
        
        # Take screenshot
        driver.save_screenshot('debug_screenshot.png')
        print("✅ Saved screenshot to debug_screenshot.png")
        
        browser.close_driver()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(debug_page_structure()) 