#!/usr/bin/env python3
"""
Core Prompt Agent - Basic functionality for prompt injection and response capture.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.chatgpt_scraper import ChatGPTScraper
from core.template_engine import render_template
from utils.chat_navigation import robust_navigate_to_convo, send_prompt_to_chat

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/prompt_agent_core.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PromptAgentCore:
    """
    Core functionality for prompt injection and response capture.
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.scraper = None
        
        # Output structure
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from the prompts directory."""
        prompts_dir = Path("prompts")
        templates = {}
        
        if not prompts_dir.exists():
            logger.warning("Prompts directory not found, creating default templates")
            return self._create_default_templates()
        
        for prompt_file in prompts_dir.glob("*.prompt.md"):
            prompt_id = prompt_file.stem.replace(".prompt", "")
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    templates[prompt_id] = f.read()
                logger.info(f"Loaded prompt template: {prompt_id}")
            except Exception as e:
                logger.error(f"Failed to load prompt template {prompt_id}: {e}")
        
        return templates
    
    def _create_default_templates(self) -> Dict[str, str]:
        """Create default prompt templates if none exist."""
        default_prompts = {
            "memory-summarizer": """You are an expert conversation analyst. Please analyze the following conversation and provide a comprehensive summary that captures the main topic, key insights, action items, and technical details.

**CONVERSATION TO ANALYZE:**
{{ conversation_content }}""",
            
            "codex-validator": """You are an expert code reviewer. Please analyze the following conversation for any code, technical specifications, or implementation details and provide a comprehensive technical assessment.

**CONVERSATION TO ANALYZE:**
{{ conversation_content }}"""
        }
        
        # Save default templates
        prompts_dir = Path("prompts")
        prompts_dir.mkdir(exist_ok=True)
        
        for prompt_id, content in default_prompts.items():
            prompt_file = prompts_dir / f"{prompt_id}.prompt.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created default prompt template: {prompt_id}")
        
        return default_prompts
    
    def load_conversations(self, conversations_file: str = "conversations.json") -> List[Dict]:
        """Load conversations from JSON file."""
        try:
            with open(conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            logger.info(f"Loaded {len(conversations)} conversations")
            return conversations
        except FileNotFoundError:
            logger.error(f"Conversations file not found: {conversations_file}")
            return []
        except Exception as e:
            logger.error(f"Failed to load conversations: {e}")
            return []
    
    def initialize_scraper(self) -> bool:
        """Initialize the ChatGPT scraper and ensure login."""
        try:
            username = os.getenv('CHATGPT_USERNAME')
            password = os.getenv('CHATGPT_PASSWORD')
            
            if not username or not password:
                logger.error("Missing ChatGPT credentials in .env file")
                return False
            
            self.scraper = ChatGPTScraper(
                headless=self.headless,
                timeout=30,
                use_undetected=True,
                username=username,
                password=password
            )
            
            if not self.scraper.start_driver():
                logger.error("Failed to start browser driver")
                return False
            
            logger.info("✅ Browser driver started")
            
            # Navigate to ChatGPT
            if not self.scraper.navigate_to_chatgpt():
                logger.error("Failed to navigate to ChatGPT")
                return False
            
            logger.info("✅ Successfully navigated to ChatGPT")
            
            # Check if already logged in
            logger.info("🔍 Checking login status...")
            if self.scraper.is_logged_in():
                logger.info("✅ Already logged in!")
                return True
            else:
                logger.info("ℹ️ Not logged in, attempting login...")
                if not self.scraper.ensure_login_modern(allow_manual=True, manual_timeout=60):
                    logger.error("❌ Failed to log in - cannot proceed with batch processing")
                    return False
                logger.info("✅ Login successful!")
                return True
            
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            return False
    
    def wait_for_chat_ready(self, timeout: int = 30) -> bool:
        """Wait for the chat interface to be ready for input."""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            # Wait for the textarea to be present and enabled
            textarea = WebDriverWait(self.scraper.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))
            )
            
            return textarea.is_displayed() and textarea.is_enabled()
            
        except Exception as e:
            logger.warning(f"Chat not ready within {timeout}s: {e}")
            return False
    
    def send_prompt(self, prompt_text: str) -> bool:
        """Send a prompt to the current chat."""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            
            # Find the textarea
            textarea = self.scraper.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
            
            # Clear and enter the prompt
            textarea.clear()
            textarea.send_keys(prompt_text)
            logger.info("✅ Prompt entered")
            
            # Send the prompt
            textarea.send_keys(Keys.RETURN)
            logger.info("✅ Prompt sent")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send prompt: {e}")
            return False
    
    def capture_response(self, timeout: int = 60) -> Optional[str]:
        """Capture the response from the chat."""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            import time
            
            # Wait for response to start appearing
            WebDriverWait(self.scraper.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-message-author-role='assistant']"))
            )
            
            # Wait a bit more for the response to complete
            time.sleep(5)
            
            # Find the latest assistant response
            assistant_messages = self.scraper.driver.find_elements(
                By.CSS_SELECTOR, "[data-message-author-role='assistant']"
            )
            
            if not assistant_messages:
                logger.warning("No assistant messages found")
                return None
            
            # Get the latest response
            latest_message = assistant_messages[-1]
            response_text = latest_message.text
            
            logger.info(f"✅ Captured response ({len(response_text)} characters)")
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to capture response: {e}")
            return None
    
    def save_output(self, model: str, conversation_id: str, prompt_id: str, response: str) -> bool:
        """Save the response to a file."""
        try:
            # Create model directory
            model_dir = self.output_dir / model
            model_dir.mkdir(exist_ok=True)
            
            # Create conversation directory
            conv_dir = model_dir / conversation_id
            conv_dir.mkdir(exist_ok=True)
            
            # Save response
            output_file = conv_dir / f"{prompt_id}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            logger.info(f"✅ Saved output to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            return False
    
    def get_conversation_content(self, conversation_id: str) -> Optional[str]:
        """Get the content of a conversation for analysis."""
        try:
            # This would typically load from the memory manager or conversation storage
            # For now, return a placeholder
            return f"Conversation content for {conversation_id}"
        except Exception as e:
            logger.error(f"Failed to get conversation content: {e}")
            return None
    
    def close(self):
        """Clean up resources."""
        if self.scraper:
            self.scraper.close()
            logger.info("✅ Scraper closed") 