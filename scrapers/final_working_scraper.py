#!/usr/bin/env python3
"""
Final Working Scraper
Uses the correct nav element with scrollport class for scrolling.
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
    sys.exit(1)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler

class FinalWorkingScraper:
    """Final working scraper that targets the correct scroll container."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def ensure_login(self, driver, cookie_manager, login_handler):
        """Ensure we're logged in, trying cookies first, then manual login."""
        print("🔐 Ensuring login...")
        
        # Try loading cookies first
        if cookie_manager.cookie_file_exists():
            print("🔄 Trying saved cookies...")
            cookie_manager.load_cookies(driver)
            time.sleep(3)
            
            if login_handler.is_logged_in(driver):
                print("✅ Login successful with saved cookies!")
                return True
            else:
                print("❌ Saved cookies didn't work")
        
        # Fall back to manual login
        print("⚠️ Manual login required")
        print("=" * 40)
        print("Please log in manually in the browser window.")
        print("Once logged in and you can see your conversations, come back here.")
        print("=" * 40)
        
        # Wait for manual login
        manual_timeout = 180
        start_time = time.time()
        
        while time.time() - start_time < manual_timeout:
            if login_handler.is_logged_in(driver):
                print("✅ Manual login successful!")
                # Save fresh cookies
                print("🍪 Saving fresh cookies...")
                cookie_manager.save_cookies(driver)
                print("✅ Fresh cookies saved!")
                return True
            time.sleep(2)
            remaining = int(manual_timeout - (time.time() - start_time))
            print(f"⏰ Waiting for login... {remaining}s remaining")
        
        print("❌ Login timeout")
        return False
    
    def find_scrollport_container(self, driver):
        """Find the correct scrollport container."""
        print("🔍 Finding the scrollport container...")
        
        try:
            # Target the specific nav element with scrollport class
            scrollport_selectors = [
                "//nav[contains(@class, 'scrollport')]",
                "//nav[contains(@class, 'group/scrollport')]",
                "//nav[contains(@class, 'relative') and contains(@class, 'flex') and contains(@class, 'overflow')]"
            ]
            
            for selector in scrollport_selectors:
                try:
                    container = driver.find_element(By.XPATH, selector)
                    print(f"✅ Found scrollport container using: {selector}")
                    
                    # Verify it's scrollable
                    scroll_height = driver.execute_script("return arguments[0].scrollHeight", container)
                    client_height = driver.execute_script("return arguments[0].clientHeight", container)
                    
                    print(f"📏 Scroll height: {scroll_height}, Client height: {client_height}")
                    
                    if scroll_height > client_height:
                        print("✅ Container is scrollable!")
                        return container
                    else:
                        print("❌ Container is not scrollable")
                        
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            print("❌ Could not find scrollport container")
            return None
            
        except Exception as e:
            print(f"❌ Error finding scrollport container: {e}")
            return None
    
    def get_conversation_list(self, driver) -> list:
        """Get all conversations by scrolling the correct scrollport container."""
        if not driver:
            print("❌ No driver provided")
            return []
        
        try:
            print("📋 Extracting conversation list with scrollport scrolling...")
            
            # Wait for page to load
            wait = WebDriverWait(driver, self.timeout)
            
            # Wait for initial conversations to load
            print("⏳ Waiting for initial conversations to load...")
            time.sleep(5)
            
            # Find the correct scrollport container
            scroll_container = self.find_scrollport_container(driver)
            if not scroll_container:
                print("❌ Could not find scrollport container")
                return []
            
            # Scroll the correct container to load all conversations
            print("🔄 Starting scrollport scrolling...")
            self._scrollport_scroll(driver, scroll_container)
            
            # Extract all conversations
            print("📝 Extracting conversation data...")
            conversations = self._extract_conversations(driver)
            
            print(f"✅ Successfully extracted {len(conversations)} conversations!")
            return conversations
            
        except Exception as e:
            print(f"❌ Error extracting conversations: {e}")
            return []
    
    def _scrollport_scroll(self, driver, scroll_container):
        """Scroll the scrollport container to load all conversations."""
        try:
            # Get initial count
            initial_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
            print(f"📊 Initial conversation count: {initial_count}")
            
            # Scroll the scrollport container multiple times
            max_scrolls = 300  # Higher limit for large lists
            no_change_count = 0
            max_no_change = 20  # More patience
            
            for i in range(max_scrolls):
                # Scroll to bottom of scrollport container
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                time.sleep(1)
                
                # Trigger scroll event
                driver.execute_script("""
                    var event = new Event('scroll', { bubbles: true });
                    arguments[0].dispatchEvent(event);
                """, scroll_container)
                time.sleep(1)
                
                # Check new count
                new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                
                # Progress indicator
                if (i + 1) % 20 == 0:
                    print(f"📈 Scroll {i+1}/{max_scrolls}: {new_count} conversations")
                
                # Check if we're still loading new conversations
                if new_count <= initial_count:
                    no_change_count += 1
                    
                    # Try more aggressive techniques after a few attempts
                    if no_change_count >= 5:
                        print("🚀 Trying burst scrolling on scrollport...")
                        
                        # Multiple rapid scrolls
                        for j in range(15):
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                            time.sleep(0.2)
                        
                        # Check again
                        new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                        print(f"📊 After burst scrolling: {new_count} conversations")
                        
                        if new_count <= initial_count:
                            no_change_count += 1
                        else:
                            no_change_count = 0
                else:
                    no_change_count = 0
                
                # Stop if no changes for several attempts
                if no_change_count >= max_no_change:
                    print(f"⏹️ Stopping scroll after {max_no_change} attempts with no new conversations")
                    break
                
                initial_count = new_count
            
            final_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
            print(f"🎯 Final conversation count after scrollport scrolling: {final_count}")
            
        except Exception as e:
            print(f"⚠️ Error during scrollport scrolling: {e}")
    
    def _extract_conversations(self, driver) -> list:
        """Extract conversation data from the page."""
        try:
            # Get all conversation links
            conversation_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
            
            conversations = []
            seen_ids = set()
            
            for link in conversation_links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Extract conversation ID
                    conversation_id = None
                    if '/c/' in href:
                        conversation_id = href.split('/c/')[-1].split('?')[0]
                    
                    if not conversation_id or conversation_id in seen_ids:
                        continue
                    
                    seen_ids.add(conversation_id)
                    
                    # Get title
                    title = link.text.strip()
                    if not title:
                        try:
                            parent = link.find_element(By.XPATH, "./..")
                            title = parent.text.strip()
                        except:
                            title = f"Conversation {conversation_id[:8]}"
                    
                    # Skip demo conversations
                    if 'demo' in title.lower() or 'demo' in conversation_id.lower():
                        continue
                    
                    conversations.append({
                        'id': conversation_id,
                        'title': title,
                        'url': href
                    })
                    
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    print(f"⚠️ Error extracting conversation: {e}")
                    continue
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error extracting conversations: {e}")
            return []

def main():
    print("🚀 Final Working Scraper")
    print("=" * 30)
    
    try:
        # Create undetected Chrome driver
        print("📱 Creating undetected Chrome driver...")
        driver = uc.Chrome(version_main=137)
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
        scraper = FinalWorkingScraper()
        
        # Ensure login (tries cookies first, falls back to manual)
        if not scraper.ensure_login(driver, cookie_manager, login_handler):
            print("❌ Failed to login")
            driver.quit()
            return 1
        
        # Extract conversations with scrollport scrolling
        print("📋 Extracting conversations with scrollport scrolling...")
        conversations = scraper.get_conversation_list(driver)
        
        if conversations:
            print(f"🎉 Successfully found {len(conversations)} conversations!")
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/conversations/final_working_{timestamp}.json'
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to {output_file}")
            
            # Show first 20 conversations
            print("\n📝 First 20 conversations:")
            for i, conv in enumerate(conversations[:20]):
                title = conv.get('title', 'No title')
                conv_id = conv.get('id', 'No ID')
                print(f"  {i+1:2d}. {title} (ID: {conv_id})")
            
            if len(conversations) > 20:
                print(f"  ... and {len(conversations) - 20} more conversations")
            
        else:
            print("❌ No conversations found")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
        print("\n🎉 Final working scraper completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 