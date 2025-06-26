#!/usr/bin/env python3
"""
Debug Scroll Analysis
Analyze ChatGPT's page structure to understand how infinite scroll works.
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

def analyze_page_structure(driver):
    """Analyze the page structure to understand scrolling."""
    print("🔍 Analyzing page structure...")
    
    try:
        # Get page source for analysis
        page_source = driver.page_source
        
        # Look for scroll-related elements
        scroll_containers = driver.find_elements(By.XPATH, "//*[contains(@class, 'scroll') or contains(@class, 'overflow')]")
        print(f"📊 Found {len(scroll_containers)} scroll containers")
        
        for i, container in enumerate(scroll_containers[:5]):  # Show first 5
            try:
                class_name = container.get_attribute('class')
                tag_name = container.tag_name
                print(f"  {i+1}. {tag_name} with classes: {class_name}")
            except:
                continue
        
        # Look for conversation containers
        conv_containers = driver.find_elements(By.XPATH, "//*[contains(@class, 'conversation') or contains(@class, 'chat')]")
        print(f"📊 Found {len(conv_containers)} conversation containers")
        
        # Look for intersection observer or lazy loading indicators
        lazy_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'lazy') or contains(@class, 'loading') or contains(@class, 'observer')]")
        print(f"📊 Found {len(lazy_elements)} lazy loading elements")
        
        # Check for specific ChatGPT scroll containers
        chatgpt_scroll = driver.find_elements(By.XPATH, "//div[contains(@class, 'bg-token-sidebar-surface-primary')]")
        print(f"📊 Found {len(chatgpt_scroll)} ChatGPT sidebar containers")
        
        if chatgpt_scroll:
            sidebar = chatgpt_scroll[0]
            print("🔍 Analyzing ChatGPT sidebar...")
            
            # Check scroll properties
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
            client_height = driver.execute_script("return arguments[0].clientHeight", sidebar)
            scroll_top = driver.execute_script("return arguments[0].scrollTop", sidebar)
            
            print(f"  📏 Scroll height: {scroll_height}")
            print(f"  📏 Client height: {client_height}")
            print(f"  📏 Current scroll top: {scroll_top}")
            print(f"  📏 Can scroll: {scroll_height > client_height}")
            
            # Check for child elements that might be scrollable
            children = sidebar.find_elements(By.XPATH, ".//*")
            scrollable_children = []
            
            for child in children[:10]:  # Check first 10 children
                try:
                    child_scroll_height = driver.execute_script("return arguments[0].scrollHeight", child)
                    child_client_height = driver.execute_script("return arguments[0].clientHeight", child)
                    if child_scroll_height > child_client_height:
                        scrollable_children.append({
                            'tag': child.tag_name,
                            'class': child.get_attribute('class'),
                            'scroll_height': child_scroll_height,
                            'client_height': child_client_height
                        })
                except:
                    continue
            
            print(f"  📊 Found {len(scrollable_children)} scrollable child elements")
            for child in scrollable_children[:3]:
                print(f"    - {child['tag']} ({child['class']}): {child['scroll_height']} > {child['client_height']}")
        
        # Look for JavaScript variables or data attributes
        print("🔍 Looking for JavaScript data...")
        
        # Check if there are any data attributes indicating scroll state
        data_attrs = driver.find_elements(By.XPATH, "//*[@data-scroll or @data-loaded or @data-page]")
        print(f"📊 Found {len(data_attrs)} elements with scroll-related data attributes")
        
        # Try to find the actual conversation list container
        conversation_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
        print(f"📊 Found {len(conversation_links)} conversation links")
        
        if conversation_links:
            # Find the parent container of the first conversation link
            first_link = conversation_links[0]
            try:
                parent = first_link.find_element(By.XPATH, "./..")
                grandparent = parent.find_element(By.XPATH, "./..")
                
                print("🔍 Analyzing conversation link hierarchy...")
                print(f"  📄 First link: {first_link.tag_name} - {first_link.get_attribute('class')}")
                print(f"  📄 Parent: {parent.tag_name} - {parent.get_attribute('class')}")
                print(f"  📄 Grandparent: {grandparent.tag_name} - {grandparent.get_attribute('class')}")
                
                # Check if grandparent is scrollable
                gp_scroll_height = driver.execute_script("return arguments[0].scrollHeight", grandparent)
                gp_client_height = driver.execute_script("return arguments[0].clientHeight", grandparent)
                print(f"  📏 Grandparent scroll: {gp_scroll_height} > {gp_client_height}")
                
            except Exception as e:
                print(f"  ⚠️ Error analyzing hierarchy: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing page structure: {e}")
        return False

def test_scroll_techniques(driver):
    """Test different scroll techniques."""
    print("🧪 Testing scroll techniques...")
    
    try:
        # Find the sidebar
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'bg-token-sidebar-surface-primary')]")
        
        # Technique 1: Standard scroll
        print("🧪 Technique 1: Standard scroll to bottom")
        initial_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
        time.sleep(3)
        new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        print(f"  📊 Before: {initial_count}, After: {new_count}")
        
        # Technique 2: Scroll with smooth behavior
        print("🧪 Technique 2: Smooth scroll")
        driver.execute_script("""
            arguments[0].scrollTo({
                top: arguments[0].scrollHeight,
                behavior: 'smooth'
            });
        """, sidebar)
        time.sleep(3)
        new_count2 = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        print(f"  📊 After smooth scroll: {new_count2}")
        
        # Technique 3: Trigger scroll event
        print("🧪 Technique 3: Trigger scroll event")
        driver.execute_script("""
            var event = new Event('scroll', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, sidebar)
        time.sleep(3)
        new_count3 = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
        print(f"  📊 After scroll event: {new_count3}")
        
        # Technique 4: Try scrolling the parent
        print("🧪 Technique 4: Scroll parent container")
        try:
            parent = driver.execute_script("return arguments[0].parentElement", sidebar)
            if parent:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", parent)
                time.sleep(3)
                new_count4 = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                print(f"  📊 After parent scroll: {new_count4}")
        except:
            print("  ⚠️ Could not scroll parent")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing scroll techniques: {e}")
        return False

def main():
    print("🔍 Debug Scroll Analysis")
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
        
        # Load cookies and check login
        if cookie_manager.cookie_file_exists():
            print("🔄 Loading cookies...")
            cookie_manager.load_cookies(driver)
            time.sleep(3)
        
        if not login_handler.is_logged_in(driver):
            print("⚠️ Not logged in - please log in manually")
            print("=" * 40)
            input("Press Enter when logged in...")
        
        # Analyze page structure
        analyze_page_structure(driver)
        
        # Test scroll techniques
        test_scroll_techniques(driver)
        
        # Take screenshot
        driver.save_screenshot('debug_analysis.png')
        print("📸 Screenshot saved as 'debug_analysis.png'")
        
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