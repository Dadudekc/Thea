"""
Conversation Extractor for ChatGPT Scraper
Handles conversation listing, extraction, and content retrieval operations.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import time
import logging
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from scrapers.conversation_list_manager import ConversationListManager
from scrapers.content_extractor import ContentExtractor
from scrapers.prompt_interactor import PromptInteractor

logger = logging.getLogger(__name__)

class ConversationExtractor:
    """Handles conversation extraction and content retrieval from ChatGPT."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the conversation extractor.
        
        Args:
            timeout: Timeout for web operations
        """
        self.timeout = timeout
        self.list_manager = ConversationListManager(timeout)
        self.content_extractor = ContentExtractor(timeout)
        self.prompt_interactor = PromptInteractor(timeout)
    
    def get_conversation_list(self, driver) -> List[Dict[str, str]]:
        """Get list of available conversations."""
        return self.list_manager.get_conversation_list(driver)
    
    def enter_conversation(self, driver, conversation_url: str) -> bool:
        """
        Navigate to a specific conversation.
        
        Args:
            driver: Selenium webdriver instance
            conversation_url: URL of the conversation to enter
            
        Returns:
            True if successfully entered conversation, False otherwise
        """
        if not driver:
            logger.error("No driver provided for conversation navigation")
            return False
        
        try:
            logger.info(f"Navigating to conversation: {conversation_url}")
            
            # Navigate to conversation URL
            driver.get(conversation_url)
            time.sleep(3)  # Wait for page to load
            
            # Wait for conversation content to load
            wait = WebDriverWait(driver, self.timeout)
            
            # Look for conversation content indicators
            content_indicators = [
                "//div[contains(@class, 'markdown')]",
                "//div[contains(@class, 'message')]",
                "//div[contains(@class, 'conversation')]//div[contains(@class, 'text')]",
                "//main//div[contains(@class, 'prose')]"
            ]
            
            content_found = False
            for indicator in content_indicators:
                try:
                    element = wait.until(EC.presence_of_element_located((By.XPATH, indicator)))
                    if element.is_displayed():
                        content_found = True
                        logger.info(f"Conversation content found using: {indicator}")
                        break
                except TimeoutException:
                    continue
            
            if not content_found:
                logger.warning("Conversation content not found")
                return False
            
            logger.info("✅ Successfully entered conversation")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enter conversation: {e}")
            return False
    
    def get_conversation_content(self, driver) -> Dict[str, str]:
        """Extract content from the current conversation."""
        return self.content_extractor.get_conversation_content(driver)
    
    def send_prompt(self, driver, prompt: str, wait_for_response: bool = True) -> bool:
        """Send a prompt to the current conversation."""
        return self.prompt_interactor.send_prompt(driver, prompt, wait_for_response) 