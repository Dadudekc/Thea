#!/usr/bin/env python3
"""
Comprehensive Scroll Finder
Find ALL scrollable containers and test each one to find the correct one.
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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler

def find_all_scrollable_containers(driver):
    """Find ALL scrollable containers on the page."""
    print("🔍 Finding ALL scrollable containers...")
    
    try:
        # Get all elements
        all_elements = driver.find_elements(By.XPATH, "//*")
        scrollable_containers = []
        
        print(f"📊 Analyzing {len(all_elements)} elements...")
        
        for i, element in enumerate(all_elements):
            try:
                # Check if element is scrollable
                scroll_height = driver.execute_script("return arguments[0].scrollHeight", element)
                client_height = driver.execute_script("return arguments[0].clientHeight", element)
                
                if scroll_height > client_height and client_height > 0:
                    tag_name = element.tag_name
                    class_name = element.get_attribute('class') or ""
                    
                    scrollable_containers.append({
                        'element': element,
                        'tag': tag_name,
                        'class': class_name,
                        'scroll_height': scroll_height,
                        'client_height': client_height,
                        'scrollable_amount': scroll_height - client_height
                    })
                    
                    if len(scrollable_containers) <= 10:  # Show first 10
                        print(f"  📏 {tag_name} ({class_name[:50]}): {scroll_height} > {client_height} (scrollable: {scroll_height - client_height})")
                
                # Progress indicator
                if (i + 1) % 1000 == 0:
                    print(f"  📊 Analyzed {i+1}/{len(all_elements)} elements, found {len(scrollable_containers)} scrollable")
                    
            except Exception as e:
                continue
        
        print(f"✅ Found {len(scrollable_containers)} scrollable containers total")
        
        # Sort by scrollable amount (most scrollable first)
        scrollable_containers.sort(key=lambda x: x['scrollable_amount'], reverse=True)
        
        return scrollable_containers
        
    except Exception as e:
        print(f"❌ Error finding scrollable containers: {e}")
        return []

def test_container_scrolling(driver, container_info, container_index):
    """Test scrolling a specific container."""
    try:
        element = container_info['element']
        tag = container_info['tag']
        class_name = container_info['class']
        scrollable_amount = container_info['scrollable_amount']
        
        print(f"🧪 Testing container {container_index + 1}: {tag} (scrollable: {scrollable_amount})")
        
        # Get initial conversation count
        initial_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        
        # Try scrolling this container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        time.sleep(2)
        
        # Check new count
        new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        
        if new_count > initial_count:
            print(f"  ✅ SUCCESS! Container {container_index + 1} loaded more conversations: {initial_count} → {new_count}")
            return True, new_count
        else:
            print(f"  ❌ Container {container_index + 1} did not load more conversations: {initial_count} → {new_count}")
            return False, new_count
            
    except Exception as e:
        print(f"  ⚠️ Error testing container {container_index + 1}: {e}")
        return False, 0

def main():
    print("🔍 Comprehensive Scroll Finder")
    print("=" * 35)
    
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
        
        # Load cookies and check login
        if cookie_manager.cookie_file_exists():
            print("🔄 Loading cookies...")
            cookie_manager.load_cookies(driver)
            time.sleep(3)
        
        if not login_handler.is_logged_in(driver):
            print("⚠️ Not logged in - please log in manually")
            print("=" * 40)
            input("Press Enter when logged in...")
        
        # Wait for conversations to load
        print("⏳ Waiting for conversations to load...")
        time.sleep(5)
        
        # Find all scrollable containers
        scrollable_containers = find_all_scrollable_containers(driver)
        
        if not scrollable_containers:
            print("❌ No scrollable containers found")
            driver.quit()
            return 1
        
        # Test the top 20 most scrollable containers
        print(f"\n🧪 Testing top {min(20, len(scrollable_containers))} most scrollable containers...")
        
        working_containers = []
        
        for i in range(min(20, len(scrollable_containers))):
            container_info = scrollable_containers[i]
            success, new_count = test_container_scrolling(driver, container_info, i)
            
            if success:
                working_containers.append({
                    'index': i,
                    'info': container_info,
                    'conversation_count': new_count
                })
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  📏 Total scrollable containers found: {len(scrollable_containers)}")
        print(f"  ✅ Working containers: {len(working_containers)}")
        
        if working_containers:
            print(f"\n🎉 Found {len(working_containers)} working scroll containers!")
            for container in working_containers:
                info = container['info']
                print(f"  📏 Container {container['index'] + 1}: {info['tag']} - {container['conversation_count']} conversations")
        else:
            print("\n❌ No working scroll containers found")
            print("This might mean:")
            print("  - Manual scrolling is required")
            print("  - ChatGPT uses a different loading mechanism")
            print("  - Need to investigate further")
        
        # Take screenshot
        driver.save_screenshot('comprehensive_analysis.png')
        print("📸 Screenshot saved as 'comprehensive_analysis.png'")
        
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