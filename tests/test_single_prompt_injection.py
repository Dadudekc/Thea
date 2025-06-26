#!/usr/bin/env python3
"""
Simple test script to debug prompt injection with a single conversation and model.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.chatgpt_scraper import ChatGPTScraper

# Load environment variables
load_dotenv()

def test_single_prompt_injection():
    """Test prompt injection with a single conversation and model."""
    
    print("=" * 60)
    print("🧪 Testing Single Prompt Injection")
    print("=" * 60)
    
    # Load one conversation
    try:
        with open("conversations.json", 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        if not conversations:
            print("❌ No conversations found")
            return False
        
        # Use the first conversation
        conversation = conversations[0]
        conversation_id = conversation['id']
        conversation_title = conversation['title']
        
        print(f"📝 Testing with conversation: {conversation_title}")
        print(f"🆔 Conversation ID: {conversation_id}")
        
    except Exception as e:
        print(f"❌ Error loading conversations: {e}")
        return False
    
    # Initialize scraper
    username = os.getenv('CHATGPT_USERNAME')
    password = os.getenv('CHATGPT_PASSWORD')
    
    if not username or not password:
        print("❌ Missing ChatGPT credentials")
        return False
    
    scraper = ChatGPTScraper(
        headless=False,
        timeout=30,
        use_undetected=True,
        username=username,
        password=password
    )
    
    try:
        # Start driver
        if not scraper.start_driver():
            print("❌ Failed to start browser driver")
            return False
        
        print("✅ Browser driver started")
        
        # Navigate to ChatGPT
        if not scraper.navigate_to_chatgpt():
            print("❌ Failed to navigate to ChatGPT")
            return False
        
        print("✅ Successfully navigated to ChatGPT")
        
        # Check login status
        print("🔍 Checking login status...")
        if scraper.is_logged_in():
            print("✅ Already logged in!")
        else:
            print("ℹ️ Not logged in, attempting login...")
            if not scraper.ensure_login_modern(allow_manual=True, manual_timeout=60):
                print("❌ Failed to log in")
                return False
            print("✅ Login successful!")
        
        # Test different URL formats
        test_urls = [
            f"https://chat.openai.com/c/{conversation_id}",
            f"https://chat.openai.com/c/{conversation_id}?model=gpt-4o",
            f"https://chat.openai.com/c/{conversation_id}?model=gpt-4-1"
        ]
        
        for i, url in enumerate(test_urls):
            print(f"\n🧪 Test {i+1}: {url}")
            
            try:
                # Navigate to conversation
                scraper.driver.get(url)
                time.sleep(5)  # Wait for page to load
                
                # Check if we're on the right page
                current_url = scraper.driver.current_url
                print(f"📍 Current URL: {current_url}")
                
                # Check if chat interface is available
                try:
                    from selenium.webdriver.common.by import By
                    textarea = scraper.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
                    if textarea.is_displayed() and textarea.is_enabled():
                        print("✅ Chat interface is ready!")
                        
                        # Try to send a simple test prompt
                        test_prompt = "Hello! This is a test prompt to verify the interface is working."
                        textarea.clear()
                        textarea.send_keys(test_prompt)
                        print("✅ Test prompt entered")
                        
                        # Don't actually send it for this test
                        print("⏸️ Test prompt ready (not sent)")
                        break
                        
                    else:
                        print("❌ Chat interface not ready")
                        
                except Exception as e:
                    print(f"❌ Error checking chat interface: {e}")
                
            except Exception as e:
                print(f"❌ Error navigating to {url}: {e}")
        
        print("\n🎉 Single prompt injection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        if scraper:
            print("ℹ️ Closing browser...")
            scraper.close_driver()

if __name__ == "__main__":
    test_single_prompt_injection() 