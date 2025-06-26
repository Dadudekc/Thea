"""
Cookie Manager for ChatGPT Scraper
Handles cookie persistence, loading, and management operations.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import os
import pickle
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CookieManager:
    """Manages cookie persistence and loading for ChatGPT sessions."""
    
    def __init__(self, cookie_file: Optional[str] = None):
        """
        Initialize the cookie manager.
        
        Args:
            cookie_file: Path to cookie file for session persistence
        """
        self.cookie_file = cookie_file or os.getenv('CHATGPT_COOKIE_FILE', 'chatgpt_cookies.pkl')
        logger.info(f"Cookie file configured: {self.cookie_file}")
    
    def save_cookies(self, driver, filepath: Optional[str] = None):
        """
        Save cookies from the current browser session.
        
        Args:
            driver: Selenium webdriver instance
            filepath: Optional custom filepath for cookies
        """
        if not driver:
            logger.warning("No driver provided for cookie saving")
            return False
            
        try:
            cookie_path = filepath or self.cookie_file
            cookies = driver.get_cookies()
            
            # Ensure directory exists
            cookie_dir = Path(cookie_path).parent
            cookie_dir.mkdir(parents=True, exist_ok=True)
            
            with open(cookie_path, 'wb') as f:
                pickle.dump(cookies, f)
            
            logger.info(f"✅ Saved {len(cookies)} cookies to {cookie_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save cookies: {e}")
            return False
    
    def load_cookies(self, driver, filepath: Optional[str] = None) -> bool:
        """
        Load cookies into the current browser session.
        
        Args:
            driver: Selenium webdriver instance
            filepath: Optional custom filepath for cookies
            
        Returns:
            True if cookies were loaded successfully, False otherwise
        """
        if not driver:
            logger.warning("No driver provided for cookie loading")
            return False
            
        try:
            cookie_path = filepath or self.cookie_file
            
            if not os.path.exists(cookie_path):
                logger.info(f"Cookie file not found: {cookie_path}")
                return False
            
            with open(cookie_path, 'rb') as f:
                cookies = pickle.load(f)
            
            # Remap legacy domains (chatgpt.com -> chat.openai.com) so Selenium
            # can inject them correctly when we are on https://chat.openai.com.
            patched = 0
            for cookie in cookies:
                domain = cookie.get("domain", "")
                if "chatgpt.com" in domain and "chat.openai.com" not in domain:
                    cookie["domain"] = domain.replace("chatgpt.com", "chat.openai.com")
                    patched += 1

            if patched:
                logger.debug("Remapped %s cookie domain(s) to chat.openai.com", patched)

            # Add cookies to driver
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Loaded {len(cookies)} cookies from {cookie_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    def cookie_file_exists(self, filepath: Optional[str] = None) -> bool:
        """
        Check if cookie file exists.
        
        Args:
            filepath: Optional custom filepath for cookies
            
        Returns:
            True if cookie file exists, False otherwise
        """
        cookie_path = filepath or self.cookie_file
        return os.path.exists(cookie_path)
    
    def delete_cookies(self, filepath: Optional[str] = None) -> bool:
        """
        Delete the cookie file.
        
        Args:
            filepath: Optional custom filepath for cookies
            
        Returns:
            True if cookie file was deleted, False otherwise
        """
        try:
            cookie_path = filepath or self.cookie_file
            
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
                logger.info(f"✅ Deleted cookie file: {cookie_path}")
                return True
            else:
                logger.info(f"Cookie file not found: {cookie_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete cookie file: {e}")
            return False 