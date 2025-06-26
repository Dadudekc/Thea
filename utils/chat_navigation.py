"""
Robust chat navigation utilities for Dream.OS agents.

This module provides reliable navigation to ChatGPT conversations with model-specific routing,
handling edge cases like session priming and redirect issues.
"""

import time
import logging
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)

def robust_navigate_to_convo(driver, convo_id, model=None, timeout=10):
    """
    Ensures the conversation is accessible and chat input is interactable.
    Handles redirect issues from ?model=... links.
    
    Args:
        driver: Selenium WebDriver instance
        convo_id: Conversation ID
        model: Optional model parameter (e.g., "gpt-4o", "gpt-4-1")
        timeout: Timeout for element detection
        
    Returns:
        WebElement: Chat input element if found, None otherwise
    """
    base_url = f"https://chat.openai.com/c/{convo_id}"
    model_url = f"{base_url}?model={model}" if model else base_url
    
    logger.info(f"🧭 Navigating to conversation: {convo_id} (model: {model or 'default'})")
    
    # Step 1: Prime session with base convo URL
    logger.info(f"📍 Step 1: Priming session with base URL")
    driver.get(base_url)
    time.sleep(3)
    
    # Step 2: Navigate to model URL if applicable
    if model:
        logger.info(f"📍 Step 2: Navigating to model-specific URL")
        driver.get(model_url)
        time.sleep(3)
    
    # Step 3: Retry logic for chat input visibility
    logger.info(f"📍 Step 3: Looking for chat input")
    for attempt in range(3):
        try:
            # Try the correct DOM element first
            input_element = driver.find_element(By.CSS_SELECTOR, "p[data-placeholder]")
            if input_element.is_displayed():
                logger.info(f"✅ Chat input found on attempt {attempt + 1} (p[data-placeholder])")
                return input_element
        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed with p[data-placeholder]: {e}")
        
        try:
            # Fallback to textarea
            input_element = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
            if input_element.is_displayed() and input_element.is_enabled():
                logger.info(f"✅ Chat input found on attempt {attempt + 1} (textarea)")
                return input_element
        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed with textarea: {e}")
        
        time.sleep(2)
        driver.refresh()
    
    # Step 4: Fallback to base URL if model param failed
    logger.info(f"📍 Step 4: Fallback to base URL")
    driver.get(base_url)
    time.sleep(3)
    
    try:
        # Try the correct DOM element first
        input_element = driver.find_element(By.CSS_SELECTOR, "p[data-placeholder]")
        if input_element.is_displayed():
            logger.info(f"✅ Chat input found with fallback (p[data-placeholder])")
            return input_element
    except Exception as e:
        logger.debug(f"Fallback failed with p[data-placeholder]: {e}")
    
    try:
        # Fallback to textarea
        input_element = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
        if input_element.is_displayed() and input_element.is_enabled():
            logger.info(f"✅ Chat input found with fallback (textarea)")
            return input_element
    except Exception as e:
        logger.debug(f"Fallback failed with textarea: {e}")
    
    # Step 5: Dump page source for debugging
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    
    debug_file = debug_dir / f"debug_page_source_{convo_id}_{model or 'default'}.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    # Save screenshot for visual debugging
    screenshot_file = debug_dir / f"debug_screenshot_{convo_id}_{model or 'default'}.png"
    try:
        driver.save_screenshot(str(screenshot_file))
        logger.info(f"📸 Screenshot saved: {screenshot_file}")
    except Exception as e:
        logger.warning(f"Failed to save screenshot: {e}")
    
    logger.error(f"❌ Could not locate chat input for convo={convo_id} model={model}")
    logger.error(f"📁 Debug files saved: {debug_file}, {screenshot_file}")
    return None

def wait_for_chat_ready(driver, timeout=30):
    """
    Wait for the chat interface to be ready for input.
    
    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum time to wait
        
    Returns:
        bool: True if chat is ready, False otherwise
    """
    try:
        # Try the correct DOM element first
        input_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-placeholder]"))
        )
        return input_element.is_displayed()
    except Exception:
        try:
            # Fallback to textarea
            input_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))
            )
            return input_element.is_displayed() and input_element.is_enabled()
        except Exception as e:
            logger.warning(f"Chat not ready within {timeout}s: {e}")
            return False

def send_prompt_to_chat(driver, prompt_text, timeout=60):
    """
    Send a prompt to the current chat and wait for response.
    
    Args:
        driver: Selenium WebDriver instance
        prompt_text: Text to send
        timeout: Timeout for response
        
    Returns:
        str: Response text if captured, None otherwise
    """
    try:
        # Find the input element (try p[data-placeholder] first, then textarea)
        input_element = None
        try:
            input_element = driver.find_element(By.CSS_SELECTOR, "p[data-placeholder]")
            logger.info("✅ Found p[data-placeholder] input element")
        except:
            try:
                input_element = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
                logger.info("✅ Found textarea input element")
            except Exception as e:
                logger.error(f"Could not find input element: {e}")
                return None
        
        # Clear and enter the prompt
        input_element.clear()
        
        # For p[data-placeholder], we need to use JavaScript to set content
        if input_element.tag_name == "p":
            driver.execute_script("arguments[0].textContent = arguments[1];", input_element, prompt_text)
            logger.info("✅ Prompt entered via JavaScript")
        else:
            # For textarea, use send_keys
            input_element.send_keys(prompt_text)
            logger.info("✅ Prompt entered via send_keys")
        
        # Send the prompt
        input_element.send_keys(Keys.RETURN)
        logger.info("✅ Prompt sent")
        
        # Wait for response using better detection
        response = wait_for_chatgpt_response(driver, timeout)
        return response
        
    except Exception as e:
        logger.error(f"Failed to send prompt: {e}")
        return None

def wait_for_chatgpt_response(driver, timeout=60):
    """
    Wait for ChatGPT to finish responding and capture the response.
    
    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum time to wait
        
    Returns:
        str: Response text if captured, None otherwise
    """
    try:
        # Wait for the response to start appearing
        # Look for the streaming indicator or response container
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-turn-2'], .markdown, [class*='response']"))
        )
        
        # Wait for the response to complete (no more streaming)
        time.sleep(3)  # Initial wait
        
        # Check for streaming completion indicators
        max_wait = 30
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Look for the "Stop generating" button - if it's gone, response is complete
                stop_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='stop-generating']")
                if not stop_button.is_displayed():
                    break
            except:
                # No stop button found, response might be complete
                break
            
            time.sleep(1)
        
        # Additional wait to ensure response is fully rendered
        time.sleep(2)
        
        # Find the response content using multiple selectors
        response_selectors = [
            "div[class*='markdown']",
            "[data-testid='conversation-turn-2'] div[class*='markdown']",
            "[class*='response'] div[class*='markdown']",
            "div[class*='prose']",
            "[data-testid='conversation-turn-2']"
        ]
        
        response_text = ""
        for selector in response_selectors:
            try:
                response_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in response_elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text and len(text) > len(response_text):
                            response_text = text
            except:
                continue
        
        if response_text:
            logger.info(f"✅ Captured response ({len(response_text)} characters)")
            return response_text
        else:
            logger.warning("No response content found")
            return None
            
    except Exception as e:
        logger.error(f"Failed to capture response: {e}")
        return None

def requires_chat_ready(func):
    """
    Decorator to ensure chat is ready before executing a function.
    
    Usage:
        @requires_chat_ready
        def my_chat_function(driver, *args, **kwargs):
            # Function that requires chat to be ready
            pass
    """
    def wrapper(driver, *args, **kwargs):
        if not wait_for_chat_ready(driver):
            logger.error("Chat not ready, cannot execute function")
            return None
        return func(driver, *args, **kwargs)
    return wrapper 