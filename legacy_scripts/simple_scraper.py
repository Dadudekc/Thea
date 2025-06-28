#!/usr/bin/env python3
"""
Simple ChatGPT Scraper
=====================

Extract all conversations from ChatGPT using the current page structure.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.browser_manager import BrowserManager
from scrapers.login_handler import LoginHandler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_all_conversations():
    """Scrape all conversations from ChatGPT."""
    print("🚀 Starting ChatGPT Conversation Scraper")
    print("=" * 60)
    
    browser_manager = BrowserManager(headless=False, use_undetected=True)
    driver = None
    
    try:
        # Create driver
        driver = browser_manager.create_driver()
        if not driver:
            print("❌ Failed to create driver")
            return False, []
        
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
        
        # Scroll to load all conversations
        print("5. Scrolling to load all conversations...")
        scroll_count = 0
        conversations_before = 0
        conversations_after = 0
        max_scrolls = 200  # Increased limit for more conversations
        
        while scroll_count < max_scrolls:
            # Count conversations before scrolling
            elements_before = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
            conversations_before = len(elements_before)
            
            # Scroll down in smaller increments
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
            
            # Wait a bit more for content to load
            time.sleep(2)
            
            # Count conversations after scrolling
            elements_after = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
            conversations_after = len(elements_after)
            
            scroll_count += 1
            
            if scroll_count % 10 == 0:
                print(f"   Scrolled {scroll_count} times, found {conversations_after} conversations...")
            
            # If no new conversations loaded after 3 consecutive scrolls, try scrolling more aggressively
            if scroll_count > 3 and conversations_after == conversations_before:
                # Try scrolling to the very bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Try scrolling up and down to trigger loading
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Check again
                elements_after = driver.find_elements(By.XPATH, "//a[contains(@href, '/c/')]")
                conversations_after = len(elements_after)
                
                if conversations_after == conversations_before:
                    print(f"   No new conversations after aggressive scrolling, stopping...")
                    break
        
        print(f"✅ Finished scrolling after {scroll_count} attempts")
        print(f"   Final conversation count: {conversations_after}")
        
        # Extract all conversations
        print("6. Extracting conversations...")
        conversations = []
        
        # Use the working selector
        selector = "//a[contains(@href, '/c/')]"
        elements = driver.find_elements(By.XPATH, selector)
        
        print(f"   Found {len(elements)} conversation elements")
        
        for i, element in enumerate(elements, 1):
            try:
                href = element.get_attribute('href')
                title = element.text.strip()
                
                if href and title and '/c/' in href:
                    conversation = {
                        'id': href.split('/c/')[-1],
                        'title': title,
                        'url': href,
                        'index': i
                    }
                    conversations.append(conversation)
                    
                    if i <= 5 or i % 100 == 0:
                        print(f"   {i:4d}. {title[:50]}...")
                        
            except Exception as e:
                print(f"   Error extracting conversation {i}: {e}")
                continue
        
        print(f"✅ Extracted {len(conversations)} conversations")
        
        # Save conversations
        print("7. Saving conversations...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/conversations/all_conversations_{timestamp}.json"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(conversations)} conversations to {output_file}")
        
        # Also save a summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_conversations': len(conversations),
            'file': output_file,
            'scraping_method': 'simple_scraper'
        }
        
        summary_file = f"data/conversations/scraping_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved summary to {summary_file}")
        
        return True, conversations
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False, []
    finally:
        if driver:
            browser_manager.close_driver()

def main():
    """Main function."""
    success, conversations = scrape_all_conversations()
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print(f"📊 Total conversations found: {len(conversations)}")
        
        if len(conversations) > 1000:
            print("🎉 Excellent! Found over 1000 conversations!")
        elif len(conversations) > 100:
            print("👍 Good! Found over 100 conversations!")
        else:
            print("⚠️  Found fewer conversations than expected.")
            
        print("\n💡 Next steps:")
        print("   1. Run the ingestion script to load these into the database")
        print("   2. Run the stats updater to update message counts")
        print("   3. Use the Dreamscape processor to analyze conversations")
    else:
        print("\n❌ Scraping failed")
        print("💡 Check the browser window and try again.")

if __name__ == "__main__":
    main()
