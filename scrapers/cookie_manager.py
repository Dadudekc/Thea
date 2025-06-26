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
import time
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse

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
            
            # Dynamically target current host (chat.openai.com or chatgpt.com)
            current_host = urlparse(driver.current_url).hostname or "chat.openai.com"
            patched = 0
            for cookie in cookies:
                domain = cookie.get("domain", "") or ""
                if current_host not in domain:
                    cookie["domain"] = current_host
                    patched += 1
                # prune unsupported keys
                for bad_key in ("sameSite", "sameParty", "priority", "PartitionKey"):
                    cookie.pop(bad_key, None)
                if cookie["domain"].startswith("."):
                    cookie["domain"] = cookie["domain"].lstrip(".")

            if patched:
                logger.debug("Rewrote domain for %s cookie(s) → %s", patched, current_host)

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

    def cookies_fresh(self, max_age_hours: int = 24) -> bool:
        """Return True if cookie file exists and is younger than max_age_hours."""
        cookie_path = self.cookie_file
        try:
            if not os.path.exists(cookie_path):
                return False
            age_hours = (time.time() - os.path.getmtime(cookie_path)) / 3600
            return age_hours <= max_age_hours
        except Exception:
            return False
    
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