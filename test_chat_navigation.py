#!/usr/bin/env python3
"""
Test chat navigation with proper handling of landing page redirects.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def test_chat_navigation():
    """Test navigation to chat interface with proper handling."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting chat navigation test...")
    
    with ScraperOrchestrator(headless=False, use_undetected=False) as orch:
        print("🔧 Initializing browser...")
        init_result = orch.initialize_browser()
        print(f"Init result: {init_result.success}")
        
        if not init_result.success:
            return
        
        # Navigate to the chat interface
        print("🌐 Navigating to chat interface...")
        orch.driver.get("https://chat.openai.com")
        time.sleep(3)
        
        print(f"Current URL: {orch.driver.current_url}")
        print(f"Page title: {orch.driver.title}")
        
        # Check if we're on the landing page and need to click through
        if "chatgpt.com" in orch.driver.current_url and "chat.openai.com" not in orch.driver.current_url:
            print("⚠️ On landing page, looking for chat button...")
            
            # Look for a button to go to chat
            chat_button_selectors = [
                "a[href*='chat.openai.com']",
                "button:has-text('Try ChatGPT')",
                "button:has-text('Start chatting')",
                "a:has-text('Chat')",
                "button:has-text('Chat')"
            ]
            
            chat_button = None
            for selector in chat_button_selectors:
                try:
                    elements = orch.driver.find_elements("css selector", selector)
                    if elements:
                        chat_button = elements[0]
                        print(f"✅ Found chat button with selector: {selector}")
                        break
                except:
                    continue
            
            if chat_button:
                print("🖱️ Clicking chat button...")
                chat_button.click()
                time.sleep(5)
                print(f"After click - URL: {orch.driver.current_url}")
            else:
                print("❌ No chat button found, trying direct navigation...")
                orch.driver.get("https://chat.openai.com")
                time.sleep(3)
        
        # Check if we need to login
        if "login" in orch.driver.current_url.lower() or "auth" in orch.driver.current_url.lower():
            print("🔐 Login required...")
            login_result = orch.login_and_save_cookies(
                username=username,
                password=password,
                allow_manual=True,
                manual_timeout=60,
            )
            
            if not login_result.success:
                print("❌ Login failed")
                return
            
            print("✅ Login successful")
            
            # Navigate back to chat interface
            orch.driver.get("https://chat.openai.com")
            time.sleep(5)
        
        print(f"Final URL: {orch.driver.current_url}")
        
        # Check if we're actually on the chat page
        if "chat.openai.com" not in orch.driver.current_url:
            print("❌ Still not on chat page, trying alternative approach...")
            
            # Try to find and click any "Try ChatGPT" or similar button
            try:
                buttons = orch.driver.find_elements("css selector", "button")
                for button in buttons:
                    text = button.text.lower()
                    if "try" in text or "chat" in text or "start" in text:
                        print(f"🖱️ Clicking button: {button.text}")
                        button.click()
                        time.sleep(5)
                        break
            except Exception as e:
                print(f"❌ Error clicking buttons: {e}")
        
        print(f"Current URL after navigation: {orch.driver.current_url}")
        
        # Wait for the chat interface to be ready
        print("⏳ Waiting for chat interface to be ready...")
        wait = WebDriverWait(orch.driver, 30)
        
        try:
            # Wait for textarea to be present and interactable
            textarea = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            placeholder = textarea.get_attribute('placeholder') or 'No placeholder'
            print(f"✅ Found interactable textarea with placeholder: '{placeholder}'")
            
        except TimeoutException:
            print("❌ Textarea not found or not interactable within 30 seconds")
            print("🔍 Checking what elements are available...")
            
            # Debug: check what elements are available
            try:
                all_textareas = orch.driver.find_elements("css selector", "textarea")
                print(f"Found {len(all_textareas)} textarea elements:")
                for i, ta in enumerate(all_textareas):
                    placeholder = ta.get_attribute('placeholder') or 'No placeholder'
                    print(f"  {i+1}: placeholder='{placeholder}'")
            except Exception as e:
                print(f"Error checking textareas: {e}")
            
            return
        
        # Try to send a simple prompt
        print("📤 Attempting to send prompt...")
        simple_prompt = "Hello! This is a test message."
        
        try:
            # Clear and type
            textarea.clear()
            textarea.send_keys(simple_prompt)
            print("✅ Typed prompt into textarea")
            
            # Wait for send button to be available
            print("🔍 Looking for send button...")
            send_button = None
            
            # Try multiple selectors with waiting
            send_selectors = [
                "button[data-testid='send-button']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                "button[type='submit']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found send button with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not send_button:
                # Try to find any button that might be the send button
                print("🔍 Looking for any button that might be send...")
                try:
                    all_buttons = orch.driver.find_elements("css selector", "button")
                    for button in all_buttons:
                        text = button.text.lower()
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        if 'send' in text or 'send' in aria_label:
                            send_button = button
                            print(f"✅ Found send button by text/aria-label: '{button.text}' / '{button.get_attribute('aria-label')}'")
                            break
                except Exception as e:
                    print(f"❌ Error finding send button: {e}")
            
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
            print("🔍 Looking for response...")
            response_selectors = [
                "[data-message-author-role='assistant']",
                "[data-testid='conversation-turn-2']",
                ".markdown",
                "[role='article']",
                "div[data-message-author-role='assistant']"
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
                with open('navigation_chat_response.json', 'w') as f:
                    json.dump({
                        'prompt': simple_prompt,
                        'response': response_text,
                        'url': orch.driver.current_url,
                        'timestamp': time.time()
                    }, f, indent=2)
                
                print("💾 Response saved to navigation_chat_response.json")
                
                # Now test with a template
                print("\n📋 Testing with template...")
                
                # Render a simple template
                from jinja2 import Environment, FileSystemLoader
                env = Environment(loader=FileSystemLoader('.'))
                template = env.get_template('templates/dreamscape/equipment_gain.j2')
                template_prompt = template.render({
                    'player_name': 'Victor',
                    'item_name': 'Test Sword',
                    'rarity': 'Rare',
                    'item_type': 'Weapon'
                })
                
                print(f"📤 Sending template prompt: {len(template_prompt)} characters")
                
                # Clear and type template
                textarea.clear()
                textarea.send_keys(template_prompt)
                print("✅ Typed template into textarea")
                
                # Click send again
                send_button.click()
                print("✅ Clicked send button for template")
                
                # Wait for response
                time.sleep(15)
                
                # Get final response
                final_elements = orch.driver.find_elements("css selector", "[data-message-author-role='assistant']")
                if final_elements:
                    final_response = final_elements[-1].text
                    print(f"📄 Template response: {final_response[:300]}...")
                    
                    # Save template response
                    with open('navigation_template_response.json', 'w') as f:
                        json.dump({
                            'template_prompt': template_prompt,
                            'response': final_response,
                            'url': orch.driver.current_url,
                            'timestamp': time.time()
                        }, f, indent=2)
                    
                    print("💾 Template response saved to navigation_template_response.json")
                else:
                    print("❌ No template response found")
                    
            else:
                print("❌ No response elements found")
                
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
    
    print("🏁 Chat navigation test completed")

if __name__ == "__main__":
    test_chat_navigation() 