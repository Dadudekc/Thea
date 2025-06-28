#!/usr/bin/env python3
"""
Test template responses by sending them to ChatGPT and collecting responses.
Uses paste method to avoid Enter key issues.
"""

import os
import sys
import time
import json
import signal
import atexit
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Global variable to hold the orchestrator for cleanup
_global_orchestrator = None

def cleanup_handler(signum=None, frame=None):
    """Cleanup handler to properly close browser."""
    global _global_orchestrator
    if _global_orchestrator:
        try:
            _global_orchestrator.close()
            print("✅ Browser closed during cleanup")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")

# Register cleanup handlers
atexit.register(cleanup_handler)
if hasattr(signal, 'SIGINT'):
    signal.signal(signal.SIGINT, cleanup_handler)
if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, cleanup_handler)

class TemplateResponder:
    """Handles sending templates to ChatGPT and collecting responses."""
    
    def __init__(self):
        self.username = os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com")
        self.password = os.getenv("CHATGPT_PASSWORD", "Falcons#1247")
        self.responses_dir = Path("outputs/template_responses")
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        
    def categorize_template(self, template_name: str) -> str:
        """Categorize template based on its name."""
        if "dreamscape" in template_name.lower():
            return "dreamscape"
        elif "conversation_analyzer" in template_name.lower():
            return "conversation_analyzer"
        elif "project_summary" in template_name.lower():
            return "project_summary"
        elif "code_review" in template_name.lower():
            return "code_review"
        elif "devlog" in template_name.lower():
            return "devlog"
        elif "mmorpg" in template_name.lower():
            return "mmorpg"
        else:
            return "other"
    
    def save_response(self, category: str, template_name: str, prompt: str, response: str, url: str):
        """Save response to categorized file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{timestamp}.json"
        filepath = self.responses_dir / filename
        
        data = {
            "template_name": template_name,
            "category": category,
            "prompt": prompt,
            "response": response,
            "url": url,
            "timestamp": timestamp
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved response to {filepath}")
    
    def send_prompt_with_paste(self, driver, textarea, prompt: str) -> bool:
        """Send prompt using paste method to avoid Enter key issues."""
        try:
            # Clear the textarea
            textarea.clear()
            time.sleep(1)
            
            # Handle different input types
            tag_name = textarea.tag_name.lower()
            
            if tag_name == 'textarea' or tag_name == 'input':
                # Use paste method for traditional inputs
                driver.execute_script("arguments[0].value = arguments[1];", textarea, prompt)
                time.sleep(1)
                
                # Trigger input event to make sure the textarea recognizes the change
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
                time.sleep(1)
            elif tag_name == 'div' or tag_name == 'p':
                # Handle contenteditable elements
                driver.execute_script("arguments[0].innerHTML = arguments[1];", textarea, prompt)
                time.sleep(1)
                
                # Trigger input event
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
                time.sleep(1)
            else:
                # Fallback: try to send keys directly
                textarea.send_keys(prompt)
                time.sleep(1)
            
            print("✅ Pasted prompt into textarea")
            return True
            
        except Exception as e:
            print(f"❌ Error pasting prompt: {e}")
            return False
    
    def find_send_button(self, driver, wait):
        """Find the send button using multiple strategies."""
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
                return send_button
            except TimeoutException:
                continue
        
        # Try to find any button that might be the send button
        try:
            all_buttons = driver.find_elements("css selector", "button")
            for button in all_buttons:
                text = button.text.lower()
                aria_label = (button.get_attribute('aria-label') or '').lower()
                if 'send' in text or 'send' in aria_label:
                    print(f"✅ Found send button by text/aria-label: '{button.text}' / '{button.get_attribute('aria-label')}'")
                    return button
        except Exception as e:
            print(f"❌ Error finding send button: {e}")
        
        return None
    
    def get_response(self, driver, wait):
        """Get the latest response from ChatGPT."""
        response_selectors = [
            "[data-message-author-role='assistant']",
            "[data-testid='conversation-turn-2']",
            ".markdown",
            "[role='article']",
            "div[data-message-author-role='assistant']"
        ]
        
        for selector in response_selectors:
            try:
                elements = driver.find_elements("css selector", selector)
                if elements:
                    latest_response = elements[-1]
                    response_text = latest_response.text
                    print(f"✅ Found response with selector: {selector}")
                    return response_text
            except:
                continue
        
        return None
    
    def check_login_status(self, driver) -> bool:
        """Check if user is logged in using profile image detection."""
        try:
            # Primary indicator: Profile image (most reliable)
            profile_image_selectors = [
                "img[alt='Profile image']",
                "img[src*='gravatar.com']",
                "img[src*='auth0.com']",
                "[data-testid='user-avatar']",
                ".user-avatar img",
                "img[class*='avatar']"
            ]
            
            for selector in profile_image_selectors:
                try:
                    elements = driver.find_elements("css selector", selector)
                    if elements and len(elements) > 0:
                        # Check if any of the elements are visible
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            print(f"✅ Logged in detected via profile image: {selector}")
                            return True
                except Exception:
                    continue
            
            # Secondary indicators (fallback)
            logged_in_indicators = [
                "//a[contains(@href, '/c/')]",  # Conversation links
                "//button[contains(@aria-label, 'New chat')]",  # New chat button
                "//button[contains(text(), 'New chat')]",  # New chat button (text)
            ]
            
            for indicator in logged_in_indicators:
                try:
                    elements = driver.find_elements("xpath", indicator)
                    if elements and len(elements) > 0:
                        # Check if any of the elements are visible
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            print(f"✅ Logged in detected via: {indicator}")
                            return True
                except Exception:
                    continue
            
            print("❌ Not logged in - no profile image or conversation elements found")
            return False
            
        except Exception as e:
            print(f"❌ Error checking login status: {e}")
            return False

    def test_templates(self):
        """Test all templates and collect responses."""
        global _global_orchestrator
        
        print("🚀 Starting template response collection...")
        
        orch = ScraperOrchestrator(headless=False, use_undetected=False)
        _global_orchestrator = orch  # Set global for cleanup
        
        try:
            print("🔧 Initializing browser...")
            init_result = orch.initialize_browser()
            if not init_result.success:
                print("❌ Browser initialization failed")
                return
            
            # Navigate to ChatGPT
            print("🌐 Navigating to ChatGPT...")
            orch.driver.get("https://chat.openai.com")
            time.sleep(5)
            
            print(f"Current URL: {orch.driver.current_url}")
            
            # Check login status using profile image
            print("🔍 Checking login status...")
            if not self.check_login_status(orch.driver):
                print("❌ Not logged in - please log in manually")
                print("⏳ Waiting for manual login...")
                input("Press Enter when you are logged in...")
                
                # Check again after manual login
                if not self.check_login_status(orch.driver):
                    print("❌ Still not logged in after manual login")
                    return
                else:
                    print("✅ Manual login successful!")
            else:
                print("✅ Already logged in!")
            
            # Wait for chat interface
            print("⏳ Waiting for chat interface...")
            wait = WebDriverWait(orch.driver, 30)
            
            try:
                # Try modern ChatGPT textarea selectors first
                textarea_selectors = [
                    "textarea[data-id='root']",
                    "textarea[placeholder*='Message']",
                    "textarea[placeholder*='chat']",
                    "textarea[placeholder*='Send']",
                    "textarea",
                    "[data-id='root']",
                    "[contenteditable='true']",
                    "div[contenteditable='true']",
                    "p[data-placeholder]"
                ]
                
                textarea = None
                for selector in textarea_selectors:
                    try:
                        textarea = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if textarea and textarea.is_displayed() and textarea.is_enabled():
                            placeholder = textarea.get_attribute('placeholder') or 'No placeholder'
                            print(f"✅ Found textarea with selector: {selector}, placeholder: '{placeholder}'")
                            break
                    except TimeoutException:
                        continue
                
                if not textarea:
                    print("❌ Textarea not found with any selector")
                    # Try to find any input-like element
                    try:
                        all_inputs = orch.driver.find_elements("css selector", "input, textarea, [contenteditable='true']")
                        for inp in all_inputs:
                            if inp.is_displayed() and inp.is_enabled():
                                tag_name = inp.tag_name
                                placeholder = inp.get_attribute('placeholder') or 'No placeholder'
                                print(f"Found potential input: {tag_name}, placeholder: '{placeholder}'")
                                if any(keyword in placeholder.lower() for keyword in ['message', 'chat', 'send', 'type']):
                                    textarea = inp
                                    print(f"✅ Using fallback input: {tag_name}")
                                    break
                    except Exception as e:
                        print(f"❌ Error during fallback input search: {e}")
                    
                    if not textarea:
                        return
                
            except TimeoutException:
                print("❌ Textarea not found")
                return
            
            # Load and test templates
            from jinja2 import Environment, FileSystemLoader
            
            # Define template paths
            template_paths = [
                ("templates/dreamscape/equipment_gain.j2", {
                    'player_name': 'Victor',
                    'item_name': 'Mystic Blade',
                    'rarity': 'Rare',
                    'item_type': 'Weapon'
                }),
                ("templates/dreamscape/skill_up.j2", {
                    'player_name': 'Victor',
                    'skill_name': 'Sword Mastery',
                    'old_level': 5,
                    'new_level': 6,
                    'skill_type': 'Combat'
                }),
                ("templates/dreamscape/quest_completed.j2", {
                    'player_name': 'Victor',
                    'quest_name': 'The Lost Artifact',
                    'quest_type': 'Main Quest',
                    'xp_gained': 1500,
                    'rewards': ['Rare Sword', 'Gold Coins', 'Experience Points']
                }),
                ("templates/dreamscape/lore_snippet.j2", {
                    'location_name': 'Ancient Ruins',
                    'lore_type': 'Historical',
                    'discovery_context': 'While exploring the ruins'
                }),
                ("templates/prompts/action_planner.j2", {
                    'task_description': 'Design a new feature for the game',
                    'context': 'MMORPG development project'
                }),
                ("templates/prompts/code_review.j2", {
                    'code_snippet': 'def calculate_damage(weapon, player_level):\n    return weapon.damage * player_level * 1.5',
                    'context': 'Game combat system'
                }),
                ("templates/prompts/conversation_analyzer.j2", {
                    'conversation_text': 'User: How do I level up faster?\nAssistant: You can complete quests and defeat monsters to gain experience points.',
                    'analysis_focus': 'Gaming advice quality'
                }),
                ("templates/prompts/devlog_generator.j2", {
                    'project_name': 'Dreamscape MMORPG',
                    'development_phase': 'Alpha Testing',
                    'key_features': ['Combat System', 'Quest System', 'Character Progression']
                }),
                ("templates/prompts/project_summary.j2", {
                    'project_name': 'Dreamscape MMORPG',
                    'project_scope': 'Full-stack MMORPG with AI integration',
                    'current_status': 'Alpha development phase'
                })
            ]
            
            env = Environment(loader=FileSystemLoader('.'))
            
            for template_path, variables in template_paths:
                try:
                    print(f"\n📋 Testing template: {template_path}")
                    
                    # Render template
                    template = env.get_template(template_path)
                    prompt = template.render(variables)
                    
                    print(f"📤 Sending prompt ({len(prompt)} characters)...")
                    
                    # Send prompt using paste method
                    if not self.send_prompt_with_paste(orch.driver, textarea, prompt):
                        print("❌ Failed to paste prompt")
                        continue
                    
                    # Find and click send button
                    send_button = self.find_send_button(orch.driver, wait)
                    if not send_button:
                        print("❌ Send button not found")
                        continue
                    
                    send_button.click()
                    print("✅ Clicked send button")
                    
                    # Wait for response
                    print("⏳ Waiting for response...")
                    time.sleep(20)  # Increased wait time
                    
                    # Get response
                    response = self.get_response(orch.driver, wait)
                    if response:
                        print(f"📄 Response received ({len(response)} characters)")
                        
                        # Categorize and save
                        template_name = Path(template_path).stem
                        category = self.categorize_template(template_name)
                        self.save_response(category, template_name, prompt, response, orch.driver.current_url)
                    else:
                        print("❌ No response received")
                    
                    # Wait between requests to avoid rate limiting
                    print("⏳ Waiting between requests...")
                    time.sleep(10)
                    
                except Exception as e:
                    print(f"❌ Error testing template {template_path}: {e}")
                    continue
            
            print("\n🏁 Template testing completed!")
            
        finally:
            # Cleanup
            try:
                orch.close()
                _global_orchestrator = None
                print("✅ Browser closed successfully")
            except Exception as e:
                print(f"⚠️  Error during browser cleanup: {e}")

    def test_templates_quick(self):
        """Quick test with just one template."""
        global _global_orchestrator
        
        print("🚀 Starting quick template test...")
        
        orch = ScraperOrchestrator(headless=False, use_undetected=False)
        _global_orchestrator = orch  # Set global for cleanup
        
        try:
            print("🔧 Initializing browser...")
            init_result = orch.initialize_browser()
            if not init_result.success:
                print("❌ Browser initialization failed")
                return
            
            # Navigate to ChatGPT
            print("🌐 Navigating to ChatGPT...")
            orch.driver.get("https://chat.openai.com")
            time.sleep(5)
            
            print(f"Current URL: {orch.driver.current_url}")
            
            # Check login status using profile image
            print("🔍 Checking login status...")
            if not self.check_login_status(orch.driver):
                print("❌ Not logged in - please log in manually")
                print("⏳ Waiting for manual login...")
                input("Press Enter when you are logged in...")
                
                # Check again after manual login
                if not self.check_login_status(orch.driver):
                    print("❌ Still not logged in after manual login")
                    return
                else:
                    print("✅ Manual login successful!")
            else:
                print("✅ Already logged in!")
            
            # Wait for chat interface
            print("⏳ Waiting for chat interface...")
            wait = WebDriverWait(orch.driver, 30)
            
            try:
                # Try modern ChatGPT textarea selectors first
                textarea_selectors = [
                    "textarea[data-id='root']",
                    "textarea[placeholder*='Message']",
                    "textarea[placeholder*='chat']",
                    "textarea[placeholder*='Send']",
                    "textarea",
                    "[data-id='root']",
                    "[contenteditable='true']",
                    "div[contenteditable='true']",
                    "p[data-placeholder]"
                ]
                
                textarea = None
                for selector in textarea_selectors:
                    try:
                        textarea = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if textarea and textarea.is_displayed() and textarea.is_enabled():
                            placeholder = textarea.get_attribute('placeholder') or 'No placeholder'
                            print(f"✅ Found textarea with selector: {selector}, placeholder: '{placeholder}'")
                            break
                    except TimeoutException:
                        continue
                
                if not textarea:
                    print("❌ Textarea not found with any selector")
                    return
                
            except TimeoutException:
                print("❌ Textarea not found")
                return
            
            # Test with just one simple template
            print("\n📋 Testing simple template...")
            
            # Simple test template
            test_template = "Hello! This is a test message from the template system. Please respond with a simple greeting."
            
            print(f"📤 Sending test prompt ({len(test_template)} characters)...")
            
            # Send prompt using paste method
            if not self.send_prompt_with_paste(orch.driver, textarea, test_template):
                print("❌ Failed to paste prompt")
                return
            
            # Find and click send button
            send_button = self.find_send_button(orch.driver, wait)
            if not send_button:
                print("❌ Send button not found")
                return
            
            send_button.click()
            print("✅ Clicked send button")
            
            # Wait for response
            print("⏳ Waiting for response...")
            time.sleep(20)
            
            # Get response
            response = self.get_response(orch.driver, wait)
            if response:
                print(f"📄 Response received ({len(response)} characters)")
                print(f"Response preview: {response[:200]}...")
                
                # Save test response
                self.save_response("test", "quick_test", test_template, response, orch.driver.current_url)
                print("✅ Quick test completed successfully!")
            else:
                print("❌ No response received")
            
        finally:
            # Cleanup
            try:
                orch.close()
                _global_orchestrator = None
                print("✅ Browser closed successfully")
            except Exception as e:
                print(f"⚠️  Error during browser cleanup: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test template responses")
    parser.add_argument("--test", action="store_true", help="Run a quick test with one template only")
    args = parser.parse_args()
    
    responder = TemplateResponder()
    
    if args.test:
        print("🧪 Running quick test mode...")
        responder.test_templates_quick()
    else:
        responder.test_templates()

if __name__ == "__main__":
    main() 