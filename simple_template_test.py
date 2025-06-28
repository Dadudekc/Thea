#!/usr/bin/env python3
"""
Simple test to debug template sending to ChatGPT.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator
from jinja2 import Environment, FileSystemLoader

def simple_test():
    """Simple test with just one template."""
    
    # Get credentials
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🚀 Starting simple template test...")
    
    with ScraperOrchestrator(headless=False, use_undetected=True) as orch:
        # Initialize browser
        print("🔧 Initializing browser...")
        if not orch.initialize_browser().success:
            print("❌ Browser initialization failed")
            return
        
        # Login
        print("🔐 Attempting login...")
        login_result = orch.login_and_save_cookies(
            username=username,
            password=password,
            allow_manual=True,
            manual_timeout=120,
        )
        
        if not login_result.success:
            if login_result.metadata and login_result.metadata.get("requires_manual_login"):
                print("⏳ Manual login required - please login in the browser window")
                # Wait for manual login
                for waited in range(0, 120, 5):
                    if orch.driver and "chat.openai.com" in orch.driver.current_url:
                        try:
                            conv_items = orch.driver.find_elements("css selector", ".conversation-list-item")
                            if conv_items:
                                print(f"✅ Login complete after {waited}s")
                                orch.cookie_manager.save_cookies(orch.driver)
                                break
                        except:
                            pass
                    time.sleep(5)
                else:
                    print("❌ Manual login timeout")
                    return
            else:
                print(f"❌ Login failed: {login_result.error}")
                return
        
        print("✅ Successfully logged in to ChatGPT")
        
        # Navigate to ChatGPT
        print("🌐 Navigating to ChatGPT...")
        orch.driver.get("https://chat.openai.com")
        time.sleep(5)
        
        # Test a simple prompt first
        print("📤 Testing simple prompt...")
        simple_prompt = "Hello! Can you help me with a quick test?"
        
        success = orch.conversation_extractor.send_prompt(
            orch.driver, simple_prompt, wait_for_response=True
        )
        
        if success:
            print("✅ Simple prompt sent successfully")
            
            # Wait for response
            time.sleep(5)
            
            # Get response
            content = orch.conversation_extractor.get_conversation_content(orch.driver)
            print(f"📄 Response received: {len(str(content))} characters")
            
            # Now test a template
            print("📋 Testing template...")
            
            # Render a simple template
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('templates/dreamscape/equipment_gain.j2')
            template_prompt = template.render({
                'player_name': 'Victor',
                'item_name': 'Test Item',
                'rarity': 'Common',
                'item_type': 'Tool'
            })
            
            print(f"📤 Sending template prompt: {len(template_prompt)} characters")
            
            success = orch.conversation_extractor.send_prompt(
                orch.driver, template_prompt, wait_for_response=True
            )
            
            if success:
                print("✅ Template prompt sent successfully")
                time.sleep(5)
                
                # Get final response
                final_content = orch.conversation_extractor.get_conversation_content(orch.driver)
                print(f"📄 Final response: {len(str(final_content))} characters")
                
                # Save the response
                import json
                with open('simple_test_response.json', 'w') as f:
                    json.dump({
                        'simple_prompt': simple_prompt,
                        'template_prompt': template_prompt,
                        'responses': {
                            'simple': content,
                            'template': final_content
                        }
                    }, f, indent=2)
                
                print("💾 Response saved to simple_test_response.json")
            else:
                print("❌ Template prompt failed")
        else:
            print("❌ Simple prompt failed")
    
    print("🏁 Test completed")

if __name__ == "__main__":
    simple_test() 