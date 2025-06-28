#!/usr/bin/env python3
"""
Simple test using paste method to avoid Enter key issues.
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

def simple_paste_test():
    """Test using paste method to send prompts."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting simple paste test...")
    
    with ScraperOrchestrator(headless=False, use_undetected=False) as orch:
        print("🔧 Initializing browser...")
        init_result = orch.initialize_browser()
        print(f"Init result: {init_result.success}")
        
        if not init_result.success:
            return
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        orch.driver.get("https://chat.openai.com")
        time.sleep(3)
        
        print(f"Current URL: {orch.driver.current_url}")
        print(f"Page title: {orch.driver.title}")
        
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
        
        # Wait for chat interface
        print("⏳ Waiting for chat interface...")
        wait = WebDriverWait(orch.driver, 30)
        
        try:
            textarea = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            placeholder = textarea.get_attribute('placeholder') or 'No placeholder'
            print(f"✅ Found textarea with placeholder: '{placeholder}'")
            
        except TimeoutException:
            print("❌ Textarea not found")
            return
        
        # Test with a simple prompt using paste method
        print("📤 Testing paste method...")
        simple_prompt = "Hello! This is a test message using the paste method."
        
        try:
            # Clear the textarea
            textarea.clear()
            time.sleep(1)
            
            # Use paste method instead of send_keys
            orch.driver.execute_script("arguments[0].value = arguments[1];", textarea, simple_prompt)
            time.sleep(1)
            
            # Trigger input event to make sure the textarea recognizes the change
            orch.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
            time.sleep(1)
            
            print("✅ Pasted prompt into textarea")
            
            # Find send button
            send_selectors = [
                "button[data-testid='send-button']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                "button[type='submit']"
            ]
            
            send_button = None
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
                with open('paste_test_response.json', 'w') as f:
                    json.dump({
                        'prompt': simple_prompt,
                        'response': response_text,
                        'url': orch.driver.current_url,
                        'timestamp': time.time()
                    }, f, indent=2)
                
                print("💾 Response saved to paste_test_response.json")
                
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
                
                # Clear and paste template
                textarea.clear()
                time.sleep(1)
                orch.driver.execute_script("arguments[0].value = arguments[1];", textarea, template_prompt)
                time.sleep(1)
                orch.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
                time.sleep(1)
                
                print("✅ Pasted template into textarea")
                
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
                    with open('paste_template_response.json', 'w') as f:
                        json.dump({
                            'template_prompt': template_prompt,
                            'response': final_response,
                            'url': orch.driver.current_url,
                            'timestamp': time.time()
                        }, f, indent=2)
                    
                    print("💾 Template response saved to paste_template_response.json")
                else:
                    print("❌ No template response found")
                    
            else:
                print("❌ No response elements found")
                
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
    
    print("🏁 Simple paste test completed")

if __name__ == "__main__":
    simple_paste_test() 