"""
Simplified ChatGPT Scraper for Digital Dreamscape Standalone
Handles automated ChatGPT conversation extraction without external dependencies.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logging.info(f"Loaded environment variables from {env_file}")
    else:
        # Try to load .env from current directory
        load_dotenv()
        logging.info("Loaded environment variables from .env file")
except ImportError:
    logging.info("python-dotenv not available - using system environment variables only")

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, 
        StaleElementReferenceException, WebDriverException
    )
    SELENIUM_AVAILABLE = True
    UNDETECTED_AVAILABLE = True
except ImportError:
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import (
            TimeoutException, NoSuchElementException, 
            StaleElementReferenceException, WebDriverException
        )
        SELENIUM_AVAILABLE = True
        UNDETECTED_AVAILABLE = False
        print("Warning: undetected-chromedriver not available. Using regular selenium.")
    except ImportError:
        SELENIUM_AVAILABLE = False
        UNDETECTED_AVAILABLE = False
        print("Warning: Selenium not available. Scraper functionality will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPTScraper:
    """
    Simplified ChatGPT scraper for extracting conversation history.
    Uses undetected-chromedriver for better anti-detection capabilities.
    Supports environment variable credentials and cookie management.
    """
    
    def __init__(self, headless: bool = False, timeout: int = 30, use_undetected: bool = True, 
                 username: Optional[str] = None, password: Optional[str] = None,
                 cookie_file: Optional[str] = None):
        """
        Initialize the ChatGPT scraper.
        
        Args:
            headless: Run browser in headless mode (can be overridden by CHATGPT_HEADLESS env var)
            timeout: Timeout for web operations (can be overridden by CHATGPT_TIMEOUT env var)
            use_undetected: Use undetected-chromedriver if available (can be overridden by CHATGPT_USE_UNDETECTED env var)
            username: ChatGPT username/email (or use CHATGPT_USERNAME env var)
            password: ChatGPT password (or use CHATGPT_PASSWORD env var)
            cookie_file: Path to cookie file for session persistence (or use CHATGPT_COOKIE_FILE env var)
        """
        # Load settings from environment variables (with fallbacks to constructor args)
        self.headless = self._get_env_bool('CHATGPT_HEADLESS', headless)
        self.timeout = int(os.getenv('CHATGPT_TIMEOUT', timeout))
        self.use_undetected = self._get_env_bool('CHATGPT_USE_UNDETECTED', use_undetected) and UNDETECTED_AVAILABLE
        self.driver = None
        
        # Get credentials from environment variables if not provided
        self.username = username or os.getenv('CHATGPT_USERNAME')
        self.password = password or os.getenv('CHATGPT_PASSWORD')
        self.cookie_file = cookie_file or os.getenv('CHATGPT_COOKIE_FILE', 'chatgpt_cookies.pkl')
        
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available. Scraper will be in demo mode.")
        elif self.use_undetected:
            logger.info("Using undetected-chromedriver for enhanced anti-detection")
        else:
            logger.info("Using regular selenium webdriver")
        
        # Log credential status
        if self.username:
            masked_username = f"{self.username[:3]}***{self.username[-3:] if len(self.username) > 6 else ''}"
            logger.info(f"Username configured: {masked_username}")
        else:
            logger.info("No username configured - will require manual login")
        
        if self.password:
            logger.info("Password configured: [HIDDEN]")
        else:
            logger.info("No password configured - will require manual login")
        
        if self.cookie_file:
            logger.info(f"Cookie file configured: {self.cookie_file}")
        
        # Log configuration
        logger.info(f"Configuration: headless={self.headless}, timeout={self.timeout}, use_undetected={self.use_undetected}")
    
    def _get_env_bool(self, env_var: str, default: bool) -> bool:
        """Helper method to get boolean from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()
    
    def start_driver(self) -> bool:
        """Start the web driver using undetected-chromedriver if available."""
        if not SELENIUM_AVAILABLE:
            logger.warning("Cannot start driver - Selenium not available")
            return False
            
        try:
            logger.info(f"Starting driver with use_undetected={self.use_undetected}, headless={self.headless}")
            
            if self.use_undetected:
                logger.info("Using undetected-chromedriver")
                # Use undetected-chromedriver
                options = uc.ChromeOptions()
                logger.info("Created uc.ChromeOptions()")
                
                # Fix compatibility issue: Add headless property if it doesn't exist
                if not hasattr(options, 'headless'):
                    logger.info("Adding headless property for compatibility")
                    options.headless = False  # Default to False, will be set by argument
                
                if self.headless:
                    logger.info("Setting headless mode for undetected-chromedriver")
                    try:
                        options.add_argument("--headless=new")
                        logger.info("Added --headless=new argument")
                        options.headless = True  # Set property for undetected-chromedriver
                    except Exception as e:
                        logger.error(f"Failed to add --headless=new: {e}")
                
                logger.info("Adding standard Chrome options...")
                try:
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    logger.info("Added standard Chrome arguments")
                except Exception as e:
                    logger.error(f"Failed to add standard arguments: {e}")
                
                # Additional undetected options
                logger.info("Adding undetected-specific options...")
                try:
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    # Remove problematic options that cause Chrome compatibility issues
                    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    # options.add_experimental_option('useAutomationExtension', False)
                    logger.info("Added undetected-specific options")
                except Exception as e:
                    logger.error(f"Failed to add undetected options: {e}")
                
                logger.info("Creating uc.Chrome instance...")
                try:
                    self.driver = uc.Chrome(options=options)
                    logger.info("Successfully created uc.Chrome instance")
                except Exception as e:
                    logger.error(f"Failed to create uc.Chrome: {e}")
                    raise
                
                # Execute script to remove webdriver property
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    logger.info("Executed webdriver property removal script")
                except Exception as e:
                    logger.error(f"Failed to execute webdriver removal script: {e}")
                
            else:
                logger.info("Using regular selenium webdriver")
                # Fallback to regular selenium
                from selenium import webdriver  # Import here to fix NameError
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument("--headless")
                
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                
                logger.info("Creating regular selenium Chrome instance...")
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Successfully created regular Chrome instance")
            
            logger.info("Setting implicit wait...")
            self.driver.implicitly_wait(10)
            logger.info(f"Web driver started successfully using {'undetected-chromedriver' if self.use_undetected else 'regular selenium'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web driver: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            
            # Print more details about the exception
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            
            return False
    
    def close_driver(self):
        """Close the web driver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Web driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None
    
    def navigate_to_chatgpt(self, model: str = "") -> bool:
        """
        Navigate to ChatGPT interface.
        
        Args:
            model: Optional model parameter (e.g., "gpt-4")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            url = "https://chat.openai.com/"
            if model:
                url += f"?model={model}"
                
            self.driver.get(url)
            logger.info(f"Navigated to ChatGPT: {url}")
            
            # Wait for page to load
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to ChatGPT: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged into ChatGPT.
        
        Returns:
            True if logged in, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            # Look for elements that indicate logged-in state
            logged_in_indicators = [
                "//button[contains(text(), 'New chat')]",
                "//div[contains(@class, 'conversation')]",
                "//textarea[@placeholder='Message ChatGPT…']"
            ]
            
            for selector in logged_in_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info("User appears to be logged in")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.info("User does not appear to be logged in")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def get_conversation_list(self) -> List[Dict[str, str]]:
        """
        Get list of available conversations.
        
        Returns:
            List of conversation metadata dictionaries
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return []
            
        if not SELENIUM_AVAILABLE:
            # Return demo data
            return self._get_demo_conversations()
        
        conversations = []
        
        try:
            # Wait for conversation list to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-item']"))
            )
            
            # Find conversation elements
            conversation_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='conversation-item']"
            )
            
            for element in conversation_elements:
                try:
                    title = element.text.strip()
                    if title:
                        conversation = {
                            "title": title,
                            "url": element.get_attribute("href") or "",
                            "timestamp": datetime.now().isoformat(),
                            "captured_at": datetime.now().isoformat()
                        }
                        conversations.append(conversation)
                        
                except (StaleElementReferenceException, NoSuchElementException) as e:
                    logger.warning(f"Error extracting conversation: {e}")
                    continue
            
            logger.info(f"Found {len(conversations)} conversations")
            return conversations
            
        except TimeoutException:
            logger.warning("Timeout waiting for conversation list")
            return []
        except Exception as e:
            logger.error(f"Error getting conversation list: {e}")
            return []
    
    def _get_demo_conversations(self) -> List[Dict[str, str]]:
        """Return demo conversation data when Selenium is not available."""
        return [
            {
                "title": "Demo Conversation 1",
                "url": "https://chat.openai.com/c/demo1",
                "timestamp": "2025-01-20T10:00:00",
                "captured_at": datetime.now().isoformat()
            },
            {
                "title": "Demo Conversation 2", 
                "url": "https://chat.openai.com/c/demo2",
                "timestamp": "2025-01-20T11:00:00",
                "captured_at": datetime.now().isoformat()
            },
            {
                "title": "Demo Conversation 3",
                "url": "https://chat.openai.com/c/demo3", 
                "timestamp": "2025-01-20T12:00:00",
                "captured_at": datetime.now().isoformat()
            }
        ]
    
    def run_scraper(self, model: str = "", output_file: str = "chatgpt_chats.json") -> bool:
        """
        Main scraping workflow with enhanced login handling.
        
        Args:
            model: Optional model parameter
            output_file: Path to save captured data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not SELENIUM_AVAILABLE:
                logger.info("Running in demo mode (Selenium not available)")
                conversations = self._get_demo_conversations()
            else:
                if not self.navigate_to_chatgpt(model):
                    return False
                
                # Use enhanced login handling
                if not self.ensure_login():
                    logger.error("Failed to log in - cannot proceed with scraping")
                    return False
                
                conversations = self.get_conversation_list()
            
            if not conversations:
                logger.warning("No conversations found")
                return False
            
            # Save data
            self._save_conversations(conversations, output_file)
            logger.info(f"Scraping completed. Saved {len(conversations)} conversations to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return False
    
    def _save_conversations(self, conversations: List[Dict[str, str]], output_file: str):
        """Save conversations to file."""
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save conversations: {e}")
            raise
    
    def enter_conversation(self, conversation_url: str) -> bool:
        """
        Navigate to a specific conversation.
        
        Args:
            conversation_url: URL of the conversation to enter
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            self.driver.get(conversation_url)
            logger.info(f"Entered conversation: {conversation_url}")
            
            # Wait for conversation to load
            time.sleep(3)
            
            # Check if we're in a conversation
            try:
                # Look for conversation elements
                conversation_indicators = [
                    "//div[contains(@class, 'conversation')]",
                    "//div[contains(@class, 'markdown')]",
                    "//textarea[@placeholder='Message ChatGPT…']"
                ]
                
                for selector in conversation_indicators:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            logger.info("Successfully entered conversation")
                            return True
                    except NoSuchElementException:
                        continue
                
                logger.warning("Could not confirm conversation entry")
                return False
                
            except Exception as e:
                logger.error(f"Error checking conversation entry: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to enter conversation: {e}")
            return False
    
    def send_prompt(self, prompt: str, wait_for_response: bool = True) -> bool:
        """
        Send a prompt to ChatGPT in the current conversation.
        
        Args:
            prompt: The prompt text to send
            wait_for_response: Whether to wait for ChatGPT's response
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            # Find the input textarea
            textarea_selectors = [
                "//textarea[@placeholder='Message ChatGPT…']",
                "//textarea[contains(@placeholder, 'Message')]",
                "//textarea[@data-id='root']"
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = self.driver.find_element(By.XPATH, selector)
                    if textarea.is_displayed() and textarea.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not textarea:
                logger.error("Could not find input textarea")
                return False
            
            # Clear and enter the prompt
            textarea.clear()
            textarea.send_keys(prompt)
            logger.info(f"Entered prompt: {prompt[:50]}...")
            
            # Find and click the send button
            send_button_selectors = [
                "//button[@data-testid='send-button']",
                "//button[contains(@aria-label, 'Send')]",
                "//button[contains(text(), 'Send')]",
                "//button[@type='submit']"
            ]
            
            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    if send_button.is_displayed() and send_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not send_button:
                logger.error("Could not find send button")
                return False
            
            # Click send
            send_button.click()
            logger.info("Sent prompt to ChatGPT")
            
            if wait_for_response:
                # Wait for response to start appearing
                try:
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-turn-2']"))
                    )
                    logger.info("ChatGPT response started")
                    
                    # Wait a bit more for response to complete
                    time.sleep(5)
                    
                except TimeoutException:
                    logger.warning("Timeout waiting for ChatGPT response")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send prompt: {e}")
            return False
    
    def get_conversation_content(self) -> Dict[str, str]:
        """
        Get the current conversation content including messages and responses.
        
        Returns:
            Dictionary with conversation content
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return {}
            
        try:
            content = {
                "messages": [],
                "responses": [],
                "full_conversation": ""
            }
            
            # Find conversation messages
            message_selectors = [
                "//div[contains(@class, 'markdown')]",
                "//div[contains(@class, 'conversation')]//div[contains(@class, 'text')]",
                "//div[@data-testid='conversation-turn-2']//div[contains(@class, 'markdown')]"
            ]
            
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if text:
                                content["messages"].append(text)
                                content["full_conversation"] += text + "\n\n"
                except Exception as e:
                    logger.warning(f"Error extracting messages: {e}")
                    continue
            
            logger.info(f"Extracted {len(content['messages'])} messages")
            return content
            
        except Exception as e:
            logger.error(f"Failed to get conversation content: {e}")
            return {}
    
    def run_templated_prompts(self, conversations: List[Dict[str, str]], prompt_template: str) -> List[Dict[str, str]]:
        """
        Run templated prompts on a list of conversations.
        
        Args:
            conversations: List of conversation dictionaries
            prompt_template: Jinja2 template for prompts
            
        Returns:
            List of conversation results with prompts and responses
        """
        from core.template_engine import render_template
        
        results = []
        
        for conversation in conversations:
            try:
                # Render the prompt template
                prompt = render_template(prompt_template, {"conversation": conversation})
                
                # Enter the conversation
                if not self.enter_conversation(conversation["url"]):
                    logger.warning(f"Could not enter conversation: {conversation['title']}")
                    continue
                
                # Send the prompt
                if not self.send_prompt(prompt):
                    logger.warning(f"Could not send prompt for: {conversation['title']}")
                    continue
                
                # Get the response
                content = self.get_conversation_content()
                
                # Store result
                result = {
                    "conversation": conversation,
                    "prompt": prompt,
                    "response": content.get("full_conversation", ""),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
                
                logger.info(f"Processed conversation: {conversation['title']}")
                
            except Exception as e:
                logger.error(f"Error processing conversation {conversation.get('title', 'Unknown')}: {e}")
                continue
        
        return results

    def save_cookies(self, filepath: str):
        """Save cookies to a file."""
        import pickle
        if self.driver:
            with open(filepath, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info(f"Cookies saved to {filepath}")

    def load_cookies(self, filepath: str):
        """Load cookies from a file."""
        import pickle
        import os
        if self.driver and os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    # Selenium requires domain to be set for add_cookie
                    if 'sameSite' in cookie:
                        cookie.pop('sameSite')
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.warning(f"Could not add cookie: {e}")
            logger.info(f"Cookies loaded from {filepath}")

    def login_with_credentials(self) -> bool:
        """
        Attempt to log in using stored credentials.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
        
        if not self.username or not self.password:
            logger.warning("No credentials available for automated login")
            return False
        
        try:
            logger.info("Attempting automated login...")
            
            # Navigate to login page
            self.driver.get("https://chat.openai.com/auth/login")
            time.sleep(3)
            
            # Find and fill username/email field
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='username']"))
                )
                email_field.clear()
                email_field.send_keys(self.username)
                logger.info("Entered username/email")
            except TimeoutException:
                logger.error("Could not find email field")
                return False
            
            # Find and click continue button
            try:
                continue_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button:contains('Continue')"))
                )
                continue_button.click()
                logger.info("Clicked continue button")
                time.sleep(3)
            except TimeoutException:
                logger.error("Could not find continue button")
                return False
            
            # Find and fill password field
            try:
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                password_field.clear()
                password_field.send_keys(self.password)
                logger.info("Entered password")
            except TimeoutException:
                logger.error("Could not find password field")
                return False
            
            # Find and click login button
            try:
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button:contains('Continue')"))
                )
                login_button.click()
                logger.info("Clicked login button")
                
                # Wait for login to complete
                time.sleep(5)
                
                # Check if login was successful
                if self.is_logged_in():
                    logger.info("✅ Automated login successful!")
                    
                    # Save cookies for future use
                    if self.cookie_file:
                        self.save_cookies(self.cookie_file)
                        logger.info(f"💾 Cookies saved to {self.cookie_file}")
                    
                    return True
                else:
                    logger.warning("Login may have failed - not logged in after attempt")
                    return False
                    
            except TimeoutException:
                logger.error("Could not find login button")
                return False
                
        except Exception as e:
            logger.error(f"Automated login failed: {e}")
            return False
    
    def ensure_login(self, allow_manual: bool = True) -> bool:
        """
        Ensure user is logged in, trying automated login first, then manual if needed.
        
        Args:
            allow_manual: Allow manual login if automated fails
            
        Returns:
            True if logged in, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
        
        # Check if already logged in
        if self.is_logged_in():
            logger.info("Already logged in")
            return True
        
        # Try to load cookies first
        if self.cookie_file and os.path.exists(self.cookie_file):
            logger.info("Loading saved cookies...")
            self.load_cookies(self.cookie_file)
            self.driver.refresh()
            time.sleep(3)
            
            if self.is_logged_in():
                logger.info("✅ Login successful with saved cookies!")
                return True
        
        # Try automated login if credentials are available
        if self.username and self.password:
            if self.login_with_credentials():
                return True
        
        # Fall back to manual login if allowed
        if allow_manual:
            logger.info("⚠️  Please log in manually in the browser window")
            logger.info("⏳ Waiting 60 seconds for manual login...")
            time.sleep(60)
            
            # Check if manual login was successful
            if self.is_logged_in():
                logger.info("✅ Manual login successful!")
                
                # Save cookies for future use
                if self.cookie_file:
                    self.save_cookies(self.cookie_file)
                    logger.info(f"💾 Cookies saved to {self.cookie_file}")
                
                return True
            else:
                logger.warning("Manual login timeout - still not logged in")
                return False
        
        return False

def main():
    """CLI entry point."""
    print("🚀 Starting ChatGPT Scraper...")
    
    with ChatGPTScraper(headless=False) as scraper:
        success = scraper.run_scraper(model="gpt-4")
        
        if success:
            print("✅ Scraping completed successfully")
            return 0
        else:
            print("❌ Scraping failed")
            return 1

if __name__ == "__main__":
    exit(main()) 