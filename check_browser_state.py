#!/usr/bin/env python3
"""
Check browser state and available elements.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator

def check_browser_state():
    """Check what's currently in the browser."""
    
    username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
    password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
    
    print("🔍 Checking browser state...")
    
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
        if "login" in orch.driver.current_url.lower():
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
            orch.driver.get("https://chat.openai.com")
            time.sleep(3)
        
        # Now check what elements are available
        print("\n🔍 Checking available elements...")
        
        # Check for textarea
        textarea_selectors = [
            "textarea[data-id='root']",
            "textarea",
            "[data-id='root']",
            "[placeholder*='Message']",
            "[placeholder*='chat']",
            "[placeholder*='Send']"
        ]
        
        print("Looking for textarea elements:")
        for selector in textarea_selectors:
            try:
                elements = orch.driver.find_elements("css selector", selector)
                if elements:
                    element = elements[0]
                    placeholder = element.get_attribute('placeholder') or 'No placeholder'
                    print(f"  ✅ {selector}: {len(elements)} found, placeholder='{placeholder}'")
                else:
                    print(f"  ❌ {selector}: 0 found")
            except Exception as e:
                print(f"  ❌ {selector}: Error - {e}")
        
        # Check for send buttons
        send_selectors = [
            "button[data-testid='send-button']",
            "button[aria-label*='Send']",
            "button[aria-label*='send']",
            "button[type='submit']",
            "button"
        ]
        
        print("\nLooking for send buttons:")
        for selector in send_selectors:
            try:
                elements = orch.driver.find_elements("css selector", selector)
                if elements:
                    element = elements[0]
                    aria_label = element.get_attribute('aria-label') or 'No aria-label'
                    text = element.text or 'No text'
                    print(f"  ✅ {selector}: {len(elements)} found, aria-label='{aria_label}', text='{text}'")
                else:
                    print(f"  ❌ {selector}: 0 found")
            except Exception as e:
                print(f"  ❌ {selector}: Error - {e}")
        
        # Check for response elements
        response_selectors = [
            "[data-message-author-role='assistant']",
            "[data-testid='conversation-turn-2']",
            ".markdown",
            "[role='article']",
            "[data-testid*='conversation']"
        ]
        
        print("\nLooking for response elements:")
        for selector in response_selectors:
            try:
                elements = orch.driver.find_elements("css selector", selector)
                if elements:
                    print(f"  ✅ {selector}: {len(elements)} found")
                else:
                    print(f"  ❌ {selector}: 0 found")
            except Exception as e:
                print(f"  ❌ {selector}: Error - {e}")
        
        # Check page source for clues
        print("\n📄 Page source analysis:")
        page_source = orch.driver.page_source
        print(f"  Page source length: {len(page_source)} characters")
        
        # Look for key phrases in page source
        key_phrases = [
            'textarea',
            'data-id="root"',
            'send-button',
            'Message ChatGPT',
            'conversation'
        ]
        
        for phrase in key_phrases:
            count = page_source.count(phrase)
            print(f"  '{phrase}': {count} occurrences")
        
        # Try to find any interactive elements
        print("\n🔍 Looking for any interactive elements:")
        try:
            all_buttons = orch.driver.find_elements("css selector", "button")
            print(f"  Total buttons found: {len(all_buttons)}")
            
            for i, button in enumerate(all_buttons[:5]):  # Show first 5
                text = button.text or 'No text'
                aria_label = button.get_attribute('aria-label') or 'No aria-label'
                print(f"    Button {i+1}: text='{text}', aria-label='{aria_label}'")
                
        except Exception as e:
            print(f"  Error finding buttons: {e}")
        
        # Check if we're actually on the chat page
        print(f"\n📍 Current state:")
        print(f"  URL: {orch.driver.current_url}")
        print(f"  Title: {orch.driver.title}")
        
        if "chat.openai.com" in orch.driver.current_url and "login" not in orch.driver.current_url.lower():
            print("  ✅ Appears to be on ChatGPT chat page")
        else:
            print("  ❌ Not on ChatGPT chat page")
    
    print("\n🏁 Browser state check completed")

if __name__ == "__main__":
    check_browser_state() 