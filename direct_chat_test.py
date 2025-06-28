#!/usr/bin/env python3
"""
Direct test of ChatGPT chat interface.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator

def direct_chat_test():
    """Test direct navigation to chat interface."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting direct chat test...")
    
    with ScraperOrchestrator(headless=False, use_undetected=False) as orch:
        print("🔧 Initializing browser...")
        init_result = orch.initialize_browser()
        print(f"Init result: {init_result.success}")
        
        if not init_result.success:
            return
        
        # Navigate directly to the chat interface
        print("🌐 Navigating to chat interface...")
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
        
        # Wait for the chat interface to load
        print("⏳ Waiting for chat interface to load...")
        time.sleep(5)
        
        # Look for the textarea with the correct selector
        print("🔍 Looking for chat textarea...")
        try:
            # Try the most common selector first
            textarea = orch.driver.find_element("css selector", "textarea")
            placeholder = textarea.get_attribute('placeholder') or 'No placeholder'
            print(f"✅ Found textarea with placeholder: '{placeholder}'")
            
            # Check if it's the right textarea (should contain "Ask" or similar)
            if "ask" in placeholder.lower() or "message" in placeholder.lower():
                print("✅ This appears to be the chat textarea")
            else:
                print("⚠️ This might not be the chat textarea")
                
        except Exception as e:
            print(f"❌ Textarea not found: {e}")
            return
        
        # Try to send a simple prompt
        print("📤 Attempting to send prompt...")
        simple_prompt = "Hello! This is a test message."
        
        try:
            # Clear and type
            textarea.clear()
            textarea.send_keys(simple_prompt)
            print("✅ Typed prompt into textarea")
            
            # Look for send button - try multiple selectors
            send_button = None
            send_selectors = [
                "button[data-testid='send-button']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                "button[type='submit']",
                "button:has-text('Send')",
                "button:has-text('send')"
            ]
            
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
                # Try to find any button near the textarea
                print("🔍 Looking for any button near textarea...")
                try:
                    # Get all buttons and find one that might be the send button
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
                "[data-testid*='conversation']",
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
                with open('direct_chat_response.json', 'w') as f:
                    json.dump({
                        'prompt': simple_prompt,
                        'response': response_text,
                        'url': orch.driver.current_url,
                        'timestamp': time.time()
                    }, f, indent=2)
                
                print("💾 Response saved to direct_chat_response.json")
                
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
                    with open('template_chat_response.json', 'w') as f:
                        json.dump({
                            'template_prompt': template_prompt,
                            'response': final_response,
                            'url': orch.driver.current_url,
                            'timestamp': time.time()
                        }, f, indent=2)
                    
                    print("💾 Template response saved to template_chat_response.json")
                else:
                    print("❌ No template response found")
                    
            else:
                print("❌ No response elements found")
                
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
    
    print("🏁 Direct chat test completed")

if __name__ == "__main__":
    direct_chat_test() 