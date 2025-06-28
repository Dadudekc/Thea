#!/usr/bin/env python3
"""
Minimal debug script to test prompt sending.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator

def debug_prompt_send():
    """Debug prompt sending step by step."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting debug prompt send...")
    
    with ScraperOrchestrator(headless=False, use_undetected=True) as orch:
        print("🔧 Initializing browser...")
        init_result = orch.initialize_browser()
        print(f"Init result: {init_result.success}, {init_result.error}")
        
        if not init_result.success:
            return
        
        print("🔐 Attempting login...")
        login_result = orch.login_and_save_cookies(
            username=username,
            password=password,
            allow_manual=True,
            manual_timeout=60,
        )
        
        print(f"Login result: {login_result.success}, {login_result.error}")
        if not login_result.success:
            return
        
        print("✅ Logged in successfully")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        orch.driver.get("https://chat.openai.com")
        time.sleep(3)
        
        print(f"Current URL: {orch.driver.current_url}")
        
        # Check if we're on the right page
        if "chat.openai.com" not in orch.driver.current_url:
            print("❌ Not on ChatGPT page")
            return
        
        # Look for the textarea
        print("🔍 Looking for textarea...")
        try:
            textarea = orch.driver.find_element("css selector", "textarea[data-id='root']")
            print(f"✅ Found textarea: {textarea.get_attribute('placeholder')}")
        except Exception as e:
            print(f"❌ Textarea not found: {e}")
            # Try alternative selectors
            selectors = [
                "textarea",
                "[data-id='root']",
                "[placeholder*='Message']",
                "[placeholder*='chat']"
            ]
            for selector in selectors:
                try:
                    element = orch.driver.find_element("css selector", selector)
                    print(f"Found element with selector '{selector}': {element.get_attribute('placeholder')}")
                except:
                    continue
            return
        
        # Try to send a simple prompt
        print("📤 Attempting to send prompt...")
        simple_prompt = "Hello! This is a test."
        
        try:
            # Clear and type
            textarea.clear()
            textarea.send_keys(simple_prompt)
            print("✅ Typed prompt into textarea")
            
            # Look for send button
            send_button = orch.driver.find_element("css selector", "button[data-testid='send-button']")
            print("✅ Found send button")
            
            # Click send
            send_button.click()
            print("✅ Clicked send button")
            
            # Wait for response
            print("⏳ Waiting for response...")
            time.sleep(10)
            
            # Check for response
            try:
                response_elements = orch.driver.find_elements("css selector", "[data-message-author-role='assistant']")
                print(f"✅ Found {len(response_elements)} response elements")
                
                if response_elements:
                    latest_response = response_elements[-1]
                    response_text = latest_response.text
                    print(f"📄 Response: {response_text[:200]}...")
                else:
                    print("❌ No response elements found")
                    
            except Exception as e:
                print(f"❌ Error getting response: {e}")
                
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
    
    print("🏁 Debug completed")

if __name__ == "__main__":
    debug_prompt_send() 