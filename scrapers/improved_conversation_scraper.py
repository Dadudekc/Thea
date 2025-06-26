#!/usr/bin/env python3
"""
Improved Conversation Scraper with Aggressive Scrolling
Designed to handle large numbers of conversations (1,300+) with better scrolling logic.
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

class ImprovedConversationScraper:
    """Improved conversation scraper with aggressive scrolling."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def get_conversation_list(self, driver) -> list:
        """Get list of all conversations with aggressive scrolling."""
        if not driver:
            print("❌ No driver provided")
            return []
        
        try:
            print("📋 Extracting conversation list with aggressive scrolling...")
            
            # Wait for page to load
            wait = WebDriverWait(driver, self.timeout)
            
            # Find the conversation sidebar
            sidebar_selectors = [
                "//div[contains(@class, 'bg-token-sidebar-surface-primary')]",
                "//div[contains(@class, 'sidebar')]",
                "//nav[contains(@class, 'sidebar')]",
                "//aside[contains(@class, 'sidebar')]",
                "//div[contains(@class, 'conversations')]",
                "//nav[contains(@class, 'conversations')]",
                "//div[contains(@class, 'flex-col') and contains(@class, 'overflow')]"
            ]
            
            sidebar = None
            for selector in sidebar_selectors:
                try:
                    sidebar = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    print(f"✅ Found sidebar using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not sidebar:
                print("❌ Could not find conversation sidebar")
                return []
            
            # Wait for initial conversations to load
            print("⏳ Waiting for initial conversations to load...")
            time.sleep(5)
            
            # Aggressive scrolling to load all conversations
            print("🔄 Starting aggressive scrolling to load all conversations...")
            self._aggressive_scroll(driver, sidebar)
            
            # Extract all conversations
            print("📝 Extracting conversation data...")
            conversations = self._extract_conversations(driver)
            
            print(f"✅ Successfully extracted {len(conversations)} conversations!")
            return conversations
            
        except Exception as e:
            print(f"❌ Error extracting conversations: {e}")
            return []
    
    def _aggressive_scroll(self, driver, sidebar):
        """Aggressive scrolling to load all conversations."""
        try:
            # Get initial count
            initial_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
            print(f"📊 Initial conversation count: {initial_count}")
            
            # Very aggressive scrolling for large lists
            max_scrolls = 100  # Much higher limit
            no_change_count = 0
            max_no_change = 8  # More patience before stopping
            
            for i in range(max_scrolls):
                # Scroll to bottom
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                time.sleep(2)  # Wait for loading
                
                # Check new count
                new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                
                # Progress indicator
                if (i + 1) % 5 == 0:
                    print(f"📈 Scroll {i+1}/{max_scrolls}: {new_count} conversations")
                
                # Check if we're still loading new conversations
                if new_count <= initial_count:
                    no_change_count += 1
                    
                    # Try more aggressive scrolling after a few attempts
                    if no_change_count >= 3:
                        print("🚀 Trying more aggressive scrolling...")
                        for j in range(5):  # Multiple quick scrolls
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                            time.sleep(0.5)
                        
                        # Check again
                        new_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                        print(f"📊 After aggressive scrolling: {new_count} conversations")
                        
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
            print(f"🎯 Final conversation count after scrolling: {final_count}")
            
            # If we still have a low count, try one more round
            if final_count < 500:  # If less than 500, try more
                print("🔄 Low count detected, trying additional scrolling...")
                for i in range(20):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                    time.sleep(1)
                
                final_count = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]"))
                print(f"📊 After additional scrolling: {final_count} conversations")
            
        except Exception as e:
            print(f"⚠️ Error during scrolling: {e}")
    
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
    print("🚀 Improved Conversation Scraper with Aggressive Scrolling")
    print("=" * 60)
    
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
        
        # Load existing cookies
        if cookie_manager.cookie_file_exists():
            print("🔄 Loading saved cookies...")
            cookie_manager.load_cookies(driver)
            time.sleep(2)
        
        # Check login status
        print("🔍 Checking login status...")
        if login_handler.is_logged_in(driver):
            print("✅ Already logged in!")
        else:
            print("❌ Not logged in")
            print("\n⚠️  MANUAL LOGIN REQUIRED")
            print("=" * 40)
            print("Please log in manually in the browser window.")
            print("Once logged in and you can see your conversations, come back here.")
            print("=" * 40)
            
            # Wait for manual login
            manual_timeout = 180
            start_time = time.time()
            
            while time.time() - start_time < manual_timeout:
                if login_handler.is_logged_in(driver):
                    print("✅ Login detected!")
                    break
                time.sleep(2)
                remaining = int(manual_timeout - (time.time() - start_time))
                print(f"⏰ Waiting for login... {remaining}s remaining")
            else:
                print("❌ Login timeout")
                driver.quit()
                return 1
        
        # Save cookies
        print("🍪 Saving cookies...")
        cookie_manager.save_cookies(driver)
        print("✅ Cookies saved")
        
        # Extract conversations with improved scraper
        print("📋 Extracting conversations with aggressive scrolling...")
        scraper = ImprovedConversationScraper()
        conversations = scraper.get_conversation_list(driver)
        
        if conversations:
            print(f"🎉 Successfully found {len(conversations)} conversations!")
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/conversations/improved_scraper_{timestamp}.json'
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to {output_file}")
            
            # Show first 15 conversations
            print("\n📝 First 15 conversations:")
            for i, conv in enumerate(conversations[:15]):
                title = conv.get('title', 'No title')
                conv_id = conv.get('id', 'No ID')
                print(f"  {i+1:2d}. {title} (ID: {conv_id})")
            
            if len(conversations) > 15:
                print(f"  ... and {len(conversations) - 15} more conversations")
            
        else:
            print("❌ No conversations found")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        
        print("\n🎉 Improved scraper completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 