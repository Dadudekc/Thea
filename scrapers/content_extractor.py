#!/usr/bin/env python3
"""
Content Extractor for ChatGPT Scraper
Handles message extraction and content formatting operations.
"""

import sys
import os
import logging
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Handles content extraction from conversations."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the content extractor.
        
        Args:
            timeout: Timeout for web operations
        """
        self.timeout = timeout
    
    def get_conversation_content(self, driver) -> Dict[str, str]:
        """
        Extract content from the current conversation.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            Dictionary containing conversation content
        """
        if not driver:
            logger.error("No driver provided for content extraction")
            return {'title': 'Error', 'content': 'No driver available'}
        
        try:
            logger.info("Extracting conversation content...")
            
            # Wait for content to load
            wait = WebDriverWait(driver, self.timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
            
            # Get page title
            title = driver.title
            if title and 'ChatGPT' in title:
                title = title.replace(' - ChatGPT', '').strip()
            
            # Extract conversation messages
            messages = self._extract_messages(driver)
            
            # Combine messages into content
            content = self._format_messages(messages)
            
            # Get conversation URL and metadata
            url = driver.current_url
            model = self._extract_model_info(driver)
            timestamp = self._extract_timestamp(driver)
            
            result = {
                'title': title or 'Untitled Conversation',
                'content': content,
                'url': url,
                'message_count': len(messages),
                'messages': messages,
                'model': model,
                'timestamp': timestamp
            }
            
            logger.info(f"✅ Extracted conversation: {result['title']} ({len(messages)} messages)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to extract conversation content: {e}")
            return {'title': 'Error', 'content': f'Extraction failed: {e}'}
    
    def _extract_messages(self, driver) -> List[Dict[str, str]]:
        """
        Extract individual messages from the conversation.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            # Wait for messages to load
            wait = WebDriverWait(driver, self.timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
            
            # Look for message containers with improved selectors
            message_selectors = [
                "//div[contains(@class, 'text-base')]//div[contains(@class, 'markdown')]",
                "//div[contains(@class, 'text-base')]//div[contains(@class, 'prose')]",
                "//div[contains(@class, 'text-base')]//div[contains(@class, 'text')]",
                "//div[contains(@class, 'markdown')]",
                "//div[contains(@class, 'prose')]//div[contains(@class, 'text')]",
                "//main//div[contains(@class, 'text')]"
            ]
            
            for selector in message_selectors:
                try:
                    message_elements = driver.find_elements(By.XPATH, selector)
                    if message_elements:
                        logger.info(f"Found messages using selector: {selector}")
                        break
                except Exception:
                    continue
            
            # Process each message
            for idx, msg_elem in enumerate(message_elements):
                try:
                    # Determine message role
                    role = self._determine_message_role(msg_elem)
                    
                    # Extract message content with code blocks
                    content = self._extract_message_content(msg_elem)
                    
                    if content:
                        messages.append({
                            'role': role,
                            'content': content,
                            'index': idx
                        })
                        
                except StaleElementReferenceException:
                    logger.warning(f"Stale element for message {idx}, skipping")
                    continue
                except Exception as e:
                    logger.warning(f"Error extracting message {idx}: {e}")
                    continue
            
            # If no structured messages found, try to get all text
            if not messages:
                logger.info("No structured messages found, extracting all text")
                try:
                    main_content = driver.find_element(By.TAG_NAME, "main")
                    if main_content:
                        text = main_content.text.strip()
                        if text:
                            messages.append({
                                'role': 'assistant',
                                'content': text,
                                'index': 0
                            })
                except Exception as e:
                    logger.warning(f"Failed to extract main content: {e}")
            
        except Exception as e:
            logger.error(f"Error extracting messages: {e}")
        
        return messages
    
    def _determine_message_role(self, element) -> str:
        """Determine if message is from user or assistant."""
        try:
            # Check various role indicators
            role_indicators = {
                'user': ['user', 'human', 'you:'],
                'assistant': ['assistant', 'chatgpt', 'gpt:', 'model:']
            }
            
            element_text = element.text.lower()
            element_class = element.get_attribute('class').lower()
            
            for role, indicators in role_indicators.items():
                if any(ind in element_class or ind in element_text for ind in indicators):
                    return role
            
            # Default to assistant if unclear
            return 'assistant'
            
        except Exception:
            return 'unknown'
    
    def _extract_message_content(self, element) -> str:
        """Extract message content including code blocks."""
        try:
            # Check for code blocks
            code_blocks = element.find_elements(By.TAG_NAME, "code")
            if code_blocks:
                # Replace code blocks with marked versions
                content = element.text
                for idx, code_block in enumerate(code_blocks):
                    code_text = code_block.text
                    content = content.replace(code_text, f"```\n{code_text}\n```")
                return content
            
            # Regular text content
            return element.text.strip()
            
        except Exception as e:
            logger.warning(f"Error extracting message content: {e}")
            return ""
    
    def _extract_model_info(self, driver) -> str:
        """Extract the model information if available."""
        try:
            model_indicators = [
                "//div[contains(text(), 'Model:')]",
                "//span[contains(text(), 'GPT-4')]",
                "//span[contains(text(), 'GPT-3.5')]"
            ]
            
            for indicator in model_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element:
                        return element.text.replace('Model:', '').strip()
                except:
                    continue
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def _extract_timestamp(self, driver) -> str:
        """Extract conversation timestamp if available."""
        try:
            timestamp_indicators = [
                "//div[contains(@class, 'timestamp')]",
                "//span[contains(@class, 'date')]",
                "//time"
            ]
            
            for indicator in timestamp_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element:
                        return element.get_attribute('datetime') or element.text.strip()
                except:
                    continue
            
            return ""
            
        except Exception:
            return ""
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into readable text.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted conversation text
        """
        if not messages:
            return "No messages found"
        
        formatted_lines = []
        for msg in messages:
            role = msg.get('role', 'unknown').title()
            content = msg.get('content', '')
            formatted_lines.append(f"{role}: {content}\n")
        
        return "\n".join(formatted_lines)