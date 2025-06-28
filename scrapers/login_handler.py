"""
Login Handler for ChatGPT Scraper
Handles authentication, login, and session management operations.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import os
import time
import logging
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class LoginHandler:
    """Handles ChatGPT login and authentication operations."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, 
                 totp_secret: Optional[str] = None, timeout: int = 30):
        """
        Initialize the login handler.
        
        Args:
            username: ChatGPT username/email
            password: ChatGPT password
            totp_secret: TOTP secret for 2FA
            timeout: Timeout for web operations
        """
        self.username = username or os.getenv('CHATGPT_USERNAME')
        self.password = password or os.getenv('CHATGPT_PASSWORD')
        self.totp_secret = totp_secret or os.getenv('CHATGPT_TOTP_SECRET')
        self.timeout = int(os.getenv('CHATGPT_TIMEOUT', timeout))
        
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
        
        if self.totp_secret:
            logger.info("TOTP secret configured: [HIDDEN]")
        else:
            logger.info("No TOTP secret configured - will require manual 2FA")
    
    def login_with_credentials(self, driver) -> bool:
        """
        Attempt to login with stored credentials.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            True if login successful, False otherwise
        """
        if not driver:
            logger.error("No driver provided for login")
            return False
        
        if not self.username or not self.password:
            logger.warning("Username or password not configured")
            return False
        
        try:
            logger.info("Attempting automated login...")
            
            # Wait for login form to be present
            wait = WebDriverWait(driver, self.timeout)
            
            # Look for login button and click it (new UI sometimes wraps text in <div>)
            try:
                login_btn_xpath = (
                    "//button[.//div[contains(normalize-space(text()),'Log in')] or contains(normalize-space(text()),'Log in') or contains(normalize-space(text()),'Sign in')]"
                )
                login_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, login_btn_xpath))
                )
                login_button.click()
                logger.info("Clicked login button")
                time.sleep(2)
            except TimeoutException:
                logger.info("Login button not found, may already be on login page")
            
            # Find and fill username field
            username_selectors = [
                "//input[@id='username']",
                "//input[@id='email']",
                "//input[@name='username']",
                "//input[@name='email']",
                "//input[@type='email']",
                "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email')]",
                "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'username')]",
                "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'user')]",
                "//input[@data-testid='email-input']",
                "//input[@data-testid='username-input']",
                "//input[contains(@class, 'email')]",
                "//input[contains(@class, 'username')]",
                "//input[contains(@class, 'user')]",
            ]
            username_field = None
            for sel in username_selectors:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.XPATH, sel))
                    )
                    if username_field and username_field.is_displayed() and username_field.is_enabled():
                        logger.info(f"Found username field with selector: {sel}")
                        break
                except TimeoutException:
                    continue

            if not username_field:
                logger.error("Username/email field not found via any selector")
                # Try to find any input field that might be for email/username
                try:
                    all_inputs = driver.find_elements("tag name", "input")
                    for inp in all_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            inp_type = inp.get_attribute("type") or ""
                            inp_name = inp.get_attribute("name") or ""
                            inp_id = inp.get_attribute("id") or ""
                            inp_placeholder = inp.get_attribute("placeholder") or ""
                            
                            # Check if this looks like an email/username field
                            if (inp_type.lower() in ['email', 'text'] or 
                                'email' in inp_name.lower() or 'user' in inp_name.lower() or
                                'email' in inp_id.lower() or 'user' in inp_id.lower() or
                                'email' in inp_placeholder.lower() or 'user' in inp_placeholder.lower()):
                                username_field = inp
                                logger.info(f"Found username field by inspection: type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder}")
                                break
                except Exception as e:
                    logger.error(f"Error during fallback username field search: {e}")
                
                if not username_field:
                    return False

            username_field.clear()
            username_field.send_keys(self.username)
            logger.info("Entered username/email")
            
            # Find and fill password field
            password_selectors = [
                "//input[@id='password']",
                "//input[@name='password']",
                "//input[@type='password']",
                "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'password')]",
            ]
            password_field = None
            for sel in password_selectors:
                try:
                    password_field = wait.until(
                        EC.presence_of_element_located((By.XPATH, sel))
                    )
                    if password_field:
                        break
                except TimeoutException:
                    continue

            if not password_field:
                logger.error("Password field not found via any selector")
                return False

            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Entered password")
            
            # Click continue/submit button – new UI shows "Continue" text
            try:
                submit_xpath = (
                    "//button[@type='submit' or contains(normalize-space(text()),'Continue') or contains(normalize-space(text()),'Verify') or contains(normalize-space(text()),'Next')]"
                )
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, submit_xpath))
                )
                submit_button.click()
                logger.info("Clicked submit/continue button")
            except TimeoutException:
                logger.error("Submit/Continue button not found")
                return False
            
            # Handle 2FA if configured
            if self.totp_secret:
                return self._handle_2fa(driver)
            
            # Wait for successful login
            time.sleep(3)
            return self.is_logged_in(driver)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _handle_2fa(self, driver) -> bool:
        """
        Handle two-factor authentication.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            True if 2FA successful, False otherwise
        """
        try:
            logger.info("Handling 2FA...")
            
            # Generate TOTP code
            totp_code = self._generate_totp_code()
            if not totp_code:
                logger.error("Failed to generate TOTP code")
                return False
            
            # Wait for 2FA input field
            wait = WebDriverWait(driver, self.timeout)
            try:
                totp_field = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='code' or @placeholder='Enter code']"))
                )
                totp_field.clear()
                totp_field.send_keys(totp_code)
                logger.info("Entered TOTP code")
            except TimeoutException:
                logger.error("2FA input field not found")
                return False
            
            # Submit 2FA code
            try:
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                submit_button.click()
                logger.info("Submitted 2FA code")
            except TimeoutException:
                logger.error("2FA submit button not found")
                return False
            
            # Wait for successful authentication
            time.sleep(3)
            return self.is_logged_in(driver)
            
        except Exception as e:
            logger.error(f"2FA failed: {e}")
            return False
    
    def _generate_totp_code(self) -> Optional[str]:
        """
        Generate TOTP code for 2FA.
        
        Returns:
            TOTP code string or None if generation failed
        """
        if not self.totp_secret:
            return None
        
        try:
            import pyotp
            totp = pyotp.TOTP(self.totp_secret)
            code = totp.now()
            logger.info(f"Generated TOTP code: {code}")
            return code
        except ImportError:
            logger.error("pyotp not installed - cannot generate TOTP code")
            return None
        except Exception as e:
            logger.error(f"Failed to generate TOTP code: {e}")
            return None
    
    def is_logged_in(self, driver) -> bool:
        """
        Check if user is logged in to ChatGPT.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            True if logged in, False otherwise
        """
        if not driver:
            logger.error("No driver provided")
            return False
        
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
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        # Check if any of the elements are visible
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            logger.info(f"Logged in detected via profile image: {selector}")
                            return True
                except Exception:
                    continue
            
            # Secondary indicators (fallback)
            logged_in_indicators = [
                "//a[contains(@href, '/c/')]",  # Conversation links
                "//button[contains(@aria-label, 'New chat')]",  # New chat button
                "//button[contains(text(), 'New chat')]",  # New chat button (text)
                "//div[contains(@class, 'conversation')]//a",  # Conversation items
                "//nav//a[contains(@href, '/c/')]"  # Navigation conversation links
            ]
            
            for indicator in logged_in_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements and len(elements) > 0:
                        # Check if any of the elements are visible
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            logger.info(f"Logged in detected via: {indicator}")
                            return True
                except NoSuchElementException:
                    continue
            
            # Check for login form (indicates not logged in)
            try:
                login_form = driver.find_element(By.XPATH, "//form[contains(@action, 'login')]")
                if login_form.is_displayed():
                    logger.info("Login form found - not logged in")
                    return False
            except NoSuchElementException:
                pass
            
            # Check for login/signup buttons (indicates not logged in)
            try:
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
                if login_button.is_displayed():
                    logger.info("Log in button found - not logged in")
                    return False
            except NoSuchElementException:
                pass
            
            # If we can't determine, assume not logged in
            logger.debug("Could not determine login status - assuming not logged in")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def ensure_login_modern(self, driver, allow_manual: bool = True, manual_timeout: int = 30) -> bool:
        """
        Ensure user is logged in, with fallback to manual login.
        
        Args:
            driver: Selenium webdriver instance
            allow_manual: Allow manual login if automated fails
            manual_timeout: Timeout for manual login
            
        Returns:
            True if logged in, False otherwise
        """
        if not driver:
            logger.error("No driver provided")
            return False
        
        # Check if already logged in
        if self.is_logged_in(driver):
            logger.info("Already logged in")
            return True
        
        # Try automated login
        if self.username and self.password:
            if self.login_with_credentials(driver):
                logger.info("Automated login successful")
                return True
            else:
                logger.warning("Automated login failed")
        
        # Manual login fallback
        if allow_manual:
            logger.info(f"Please log in manually within {manual_timeout} seconds...")
            start_time = time.time()
            
            while time.time() - start_time < manual_timeout:
                if self.is_logged_in(driver):
                    logger.info("Manual login detected")
                    return True
                time.sleep(1)
            
            logger.error("Manual login timeout")
        
        return False
    
    def ensure_login_with_cookies(self, driver, cookie_manager, allow_manual: bool = True, manual_timeout: int = 30) -> bool:
        """
        Ensure user is logged in with proper cookie management.
        
        Args:
            driver: Selenium webdriver instance
            cookie_manager: CookieManager instance for saving cookies
            allow_manual: Allow manual login if automated fails
            manual_timeout: Timeout for manual login
            
        Returns:
            True if logged in, False otherwise
        """
        if not driver:
            logger.error("No driver provided")
            return False
        
        # ------------------------------------------------------------------
        # Navigate to ChatGPT landing page FIRST so that:
        #   • Any subsequent cookie injection matches the correct domain
        #   • Automated login selectors are present
        # ------------------------------------------------------------------

        target_url = os.getenv("CHATGPT_BASE_URL", "https://chat.openai.com")
        try:
            logger.info("[Nav] Opening %s …", target_url)
            driver.get(target_url)
            logger.debug("[Nav] Current URL after get(): %s", driver.current_url)
        except Exception as nav_err:
            logger.error("[Nav] Failed to navigate to %s – %s", target_url, nav_err)

        # ------------------------------------------------------------------
        # Phase-3: verbose diagnostics – emit clear milestones so operators
        # can see *where* the flow is stalling when running the script.
        # ------------------------------------------------------------------

        # 1️⃣  Inject cookies if we have any
        if cookie_manager.cookie_file_exists() and cookie_manager.cookies_fresh():
            logger.info("[Cookies] Loading saved cookies from %s", cookie_manager.cookie_file)
            cookie_manager.load_cookies(driver)
            logger.debug("[Cookies] %s injected; refreshing page…", driver.current_url)
            driver.refresh()
        elif cookie_manager.cookie_file_exists():
            logger.info("[Cookies] Stored cookies appear stale; skipping load")

        # 2️⃣  Automated login attempt ------------------------------------------------
        if self.username and self.password:
            logger.info("[Login] Attempting automated credential login…")
            if self.login_with_credentials(driver):
                logger.info("Automated login successful")
                # Save cookies after successful automated login
                cookie_manager.save_cookies(driver)
                logger.info("Cookies saved after automated login")
                return True
            else:
                logger.warning("Automated login failed – will %smanual fallback", "" if allow_manual else "NOT ")

        if allow_manual:
            logger.info("[Manual] Awaiting user login – window is now interactive")
            logger.info("          Timeout: %d seconds", manual_timeout)

            start_time = time.time()
            last_ping = 0

            while time.time() - start_time < manual_timeout:
                elapsed = int(time.time() - start_time)
                if elapsed - last_ping >= 5:
                    logger.info("[Manual] %d s elapsed – still waiting…", elapsed)
                    last_ping = elapsed

                if self.is_logged_in(driver):
                    logger.info("✅ Manual login detected – saving cookies…")
                    cookie_manager.save_cookies(driver)
                    logger.info("✅ Cookies saved after manual login")
                    return True

                time.sleep(1)

            logger.error("❌ Manual login timeout after %d s", manual_timeout)

        return False 