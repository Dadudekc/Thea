#!/usr/bin/env python3
"""
Simple browser test using regular selenium.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator

def simple_browser_test():
    """Test with regular selenium (not undetected)."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting simple browser test with regular selenium...")
    
    # Force use of regular selenium, not undetected
    with ScraperOrchestrator(headless=False, use_undetected=False) as orch:
        print("🔧 Initializing browser...")
        init_result = orch.initialize_browser()
        print(f"Init result: {init_result.success}, {init_result.error}")
        
        if not init_result.success:
            print("❌ Browser initialization failed")
            return
        
        print("✅ Browser initialized successfully")
        
        # Navigate to ChatGPT first
        print("🌐 Navigating to ChatGPT...")
        orch.driver.get("https://chat.openai.com")
        time.sleep(3)
        
        print(f"Current URL: {orch.driver.current_url}")
        
        # Check if we need to login
        if "login" in orch.driver.current_url.lower():
            print("🔐 Login required...")
            login_result = orch.login_and_save_cookies(
                username=username,
                password=password,
                allow_manual=True,
                manual_timeout=60,
            )
            
            print(f"Login result: {login_result.success}, {login_result.error}")
            if not login_result.success:
                print("❌ Login failed")
                return
            
            print("✅ Login successful")
            
            # Navigate back to ChatGPT
            orch.driver.get("https://chat.openai.com")
            time.sleep(3)
        
        print(f"Final URL: {orch.driver.current_url}")
        
        # Look for the textarea
        print("🔍 Looking for textarea...")
        try:
            textarea = orch.driver.find_element("css selector", "textarea[data-id='root']")
            print(f"✅ Found textarea: {textarea.get_attribute('placeholder')}")
        except Exception as e:
            print(f"❌ Textarea not found with primary selector: {e}")
            
            # Try alternative selectors
            selectors = [
                "textarea",
                "[data-id='root']",
                "[placeholder*='Message']",
                "[placeholder*='chat']",
                "[placeholder*='Send']"
            ]
            
            for selector in selectors:
                try:
                    elements = orch.driver.find_elements("css selector", selector)
                    if elements:
                        element = elements[0]
                        print(f"Found element with selector '{selector}': {element.get_attribute('placeholder')}")
                        textarea = element
                        break
                except:
                    continue
            else:
                print("❌ No textarea found with any selector")
                return
        
        # Try to send a simple prompt
        print("📤 Attempting to send prompt...")
        simple_prompt = "Hello! This is a test message."
        
        try:
            # Clear and type
            textarea.clear()
            textarea.send_keys(simple_prompt)
            print("✅ Typed prompt into textarea")
            
            # Look for send button
            send_selectors = [
                "button[data-testid='send-button']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                "button:has-text('Send')",
                "button[type='submit']"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    elements = orch.driver.find_elements("css selector", selector)
                    if elements:
                        send_button = elements[0]
                        print(f"✅ Found send button with selector: {selector}")
                        break
                except:
                    continue
            
            if not send_button:
                print("❌ Send button not found")
                return
            
            # Click send
            send_button.click()
            print("✅ Clicked send button")
            
            # Wait for response
            print("⏳ Waiting for response...")
            time.sleep(15)
            
            # Check for response
            try:
                response_selectors = [
                    "[data-message-author-role='assistant']",
                    "[data-testid='conversation-turn-2']",
                    ".markdown",
                    "[role='article']"
                ]
                
                response_elements = []
                for selector in response_selectors:
                    try:
                        elements = orch.driver.find_elements("css selector", selector)
                        if elements:
                            response_elements = elements
                            print(f"✅ Found {len(elements)} response elements with selector: {selector}")
                            break
                    except:
                        continue
                
                if response_elements:
                    latest_response = response_elements[-1]
                    response_text = latest_response.text
                    print(f"📄 Response: {response_text[:300]}...")
                    
                    # Save response
                    import json
                    with open('simple_browser_response.json', 'w') as f:
                        json.dump({
                            'prompt': simple_prompt,
                            'response': response_text,
                            'url': orch.driver.current_url
                        }, f, indent=2)
                    
                    print("💾 Response saved to simple_browser_response.json")
                else:
                    print("❌ No response elements found")
                    
            except Exception as e:
                print(f"❌ Error getting response: {e}")
                
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
    
    print("🏁 Test completed")

if __name__ == "__main__":
    simple_browser_test() 