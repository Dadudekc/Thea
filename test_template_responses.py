#!/usr/bin/env python3
"""
Test template responses by sending them to ChatGPT and collecting responses.
Uses paste method to avoid Enter key issues.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scraper_orchestrator import ScraperOrchestrator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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
            
            # Use paste method instead of send_keys
            driver.execute_script("arguments[0].value = arguments[1];", textarea, prompt)
            time.sleep(1)
            
            # Trigger input event to make sure the textarea recognizes the change
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
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
    
    def test_templates(self):
        """Test all templates and collect responses."""
        print("🚀 Starting template response collection...")
        
        with ScraperOrchestrator(headless=False, use_undetected=False) as orch:
            print("🔧 Initializing browser...")
            init_result = orch.initialize_browser()
            if not init_result.success:
                print("❌ Browser initialization failed")
                return
            
            print("🔐 Attempting login...")
            login_result = orch.login_and_save_cookies(
                username=self.username,
                password=self.password,
                allow_manual=True,
                manual_timeout=120,
            )
            
            if not login_result.success:
                print("❌ Login failed")
                return
            
            print("✅ Login successful")
            
            # Navigate to ChatGPT
            print("🌐 Navigating to ChatGPT...")
            orch.driver.get("https://chat.openai.com")
            time.sleep(5)
            
            print(f"Current URL: {orch.driver.current_url}")
            
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

def main():
    """Main function."""
    responder = TemplateResponder()
    responder.test_templates()

if __name__ == "__main__":
    main() 