#!/usr/bin/env python3
"""
Prompt Interactor for ChatGPT Scraper
Handles prompt sending and response interaction operations.
"""

import sys
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

class PromptInteractor:
    """Handles prompt interaction with ChatGPT."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the prompt interactor.
        
        Args:
            timeout: Timeout for web operations
        """
        self.timeout = timeout
        self.max_retries = 3
        self.typing_delay = 0.1  # Delay between characters to simulate human typing
    
    def send_prompt(self, driver, prompt: str, wait_for_response: bool = True, 
                   streaming: bool = True, retry_on_error: bool = True) -> bool:
        """
        Send a prompt to the current conversation.
        
        Args:
            driver: Selenium webdriver instance
            prompt: Text prompt to send
            wait_for_response: Whether to wait for response
            streaming: Whether to wait for streaming response
            retry_on_error: Whether to retry on error
            
        Returns:
            True if prompt sent successfully, False otherwise
        """
        if not driver:
            logger.error("No driver provided for prompt sending")
            return False
        
        try:
            logger.info(f"Sending prompt: {prompt[:50]}...")
            
            # Find and fill the input field
            input_field = self._find_input_field(driver)
            if not input_field:
                logger.error("Input field not found")
                return False
            
            # Clear any existing text
            input_field.clear()
            
            # Type the prompt with human-like delays
            self._type_with_delay(input_field, prompt)
            
            # Send the prompt
            if not self._submit_prompt(input_field):
                logger.error("Failed to submit prompt")
                return False
            
            # Wait for response if requested
            if wait_for_response:
                return self._wait_for_response(driver, streaming)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending prompt: {e}")
            if retry_on_error and self.max_retries > 0:
                logger.info("Retrying prompt send...")
                self.max_retries -= 1
                time.sleep(2)  # Wait before retry
                return self.send_prompt(driver, prompt, wait_for_response, streaming)
            return False
    
    def _find_input_field(self, driver):
        """Find the input field using various selectors."""
        wait = WebDriverWait(driver, self.timeout)
        
        # Try different selectors for the input field
        input_selectors = [
            "//textarea[@placeholder]",
            "//div[@contenteditable='true']",
            "//textarea[contains(@class, 'prompt-textarea')]",
            "//input[@type='text']",
            "//textarea"
        ]
        
        for selector in input_selectors:
            try:
                input_field = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                if input_field.is_displayed() and input_field.is_enabled():
                    logger.info(f"Found input field using: {selector}")
                    return input_field
            except:
                continue
        
        return None
    
    def _type_with_delay(self, element, text: str):
        """Type text with random delays to simulate human typing."""
        try:
            # Type characters with slight delays
            for char in text:
                element.send_keys(char)
                time.sleep(self.typing_delay)
            
            logger.info("Entered prompt text")
            return True
            
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def _submit_prompt(self, element) -> bool:
        """Submit the prompt using various methods."""
        try:
            # Try different submission methods
            submission_methods = [
                lambda: element.send_keys(Keys.CONTROL + Keys.ENTER),
                lambda: element.send_keys(Keys.ENTER),
                lambda: element.submit(),
                lambda: self._click_send_button(element.parent)
            ]
            
            for method in submission_methods:
                try:
                    method()
                    time.sleep(1)  # Wait to see if submission worked
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error submitting prompt: {e}")
            return False
    
    def _click_send_button(self, parent_element):
        """Try to find and click a send button."""
        send_button_selectors = [
            "//button[contains(@class, 'send')]",
            "//button[contains(@aria-label, 'Send')]",
            "//button[contains(@title, 'Send')]"
        ]
        
        for selector in send_button_selectors:
            try:
                button = parent_element.find_element(By.XPATH, selector)
                if button and button.is_displayed() and button.is_enabled():
                    button.click()
                    return True
            except:
                continue
        
        return False
    
    def _wait_for_response(self, driver, streaming: bool = True) -> bool:
        """
        Wait for the AI response.
        
        Args:
            driver: Selenium webdriver instance
            streaming: Whether to wait for streaming response
            
        Returns:
            True if response received, False if timeout
        """
        try:
            wait = WebDriverWait(driver, self.timeout)
            
            # Wait for response to start
            response_started = wait.until(EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class, 'markdown')]"
            )))
            
            if not streaming:
                return True
            
            # Wait for streaming to complete
            time.sleep(2)  # Initial wait for streaming to begin
            
            previous_text = ""
            unchanged_count = 0
            max_unchanged = 5  # Number of checks before considering streaming complete
            
            while unchanged_count < max_unchanged:
                current_text = response_started.text
                
                if current_text == previous_text:
                    unchanged_count += 1
                else:
                    unchanged_count = 0
                    previous_text = current_text
                
                time.sleep(1)
            
            logger.info("Response streaming completed")
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for response")
            return False
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return False
    
    def get_last_response(self, driver) -> str:
        """
        Get the last response from the conversation.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            The text of the last response
        """
        try:
            # Find all response elements
            responses = driver.find_elements(By.XPATH, "//div[contains(@class, 'markdown')]")
            
            if responses:
                # Get the last response
                last_response = responses[-1]
                return last_response.text.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting last response: {e}")
            return ""