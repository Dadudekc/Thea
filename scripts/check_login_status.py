#!/usr/bin/env python3
"""
Check actual login status
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler

def main():
    print("🔍 Checking Login Status...")
    
    try:
        # Create browser
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        print("✅ Browser created")
        
        # Navigate to ChatGPT
        driver.get('https://chat.openai.com/')
        print("✅ Navigated to ChatGPT")
        
        # Load cookies
        cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
        if cookie_manager.cookie_file_exists():
            print("🔄 Loading cookies...")
            cookie_manager.load_cookies(driver)
        
        # Wait a moment for page to load
        import time
        time.sleep(3)
        
        # Check what's actually on the page
        print("\n🔍 Page Analysis:")
        
        # Check for login form
        try:
            login_form = driver.find_element(By.XPATH, "//form[contains(@action, 'login')]")
            print("❌ Login form found - NOT logged in")
        except:
            print("✅ No login form found")
        
        # Check for "Log in" button
        try:
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            print("❌ Log in button found - NOT logged in")
        except:
            print("✅ No Log in button found")
        
        # Check for "Sign up" button
        try:
            signup_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign up')]")
            print("❌ Sign up button found - NOT logged in")
        except:
            print("✅ No Sign up button found")
        
        # Check for conversation sidebar
        try:
            sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'sidebar')]")
            print("✅ Sidebar found - might be logged in")
        except:
            print("❌ No sidebar found")
        
        # Check for conversation links
        try:
            conv_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
            print(f"✅ Found {len(conv_links)} conversation links - logged in")
        except:
            print("❌ No conversation links found")
        
        # Check for "New chat" button
        try:
            new_chat = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'New chat')]")
            print("✅ New chat button found - logged in")
        except:
            print("❌ No New chat button found")
        
        # Use the login handler's detection
        print("\n🔍 Login Handler Detection:")
        login_handler = LoginHandler()
        is_logged_in = login_handler.is_logged_in(driver)
        print(f"Login handler says: {'✅ Logged in' if is_logged_in else '❌ Not logged in'}")
        
        # Show page title
        print(f"\n📄 Page title: {driver.title}")
        
        # Show current URL
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Take screenshot for manual inspection
        driver.save_screenshot('login_status_check.png')
        print("📸 Screenshot saved as 'login_status_check.png'")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 