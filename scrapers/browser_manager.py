"""
Browser Manager for ChatGPT Scraper
Handles browser setup, configuration, and management operations.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import os
import logging
from typing import Optional
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
        logging.info("Loaded environment variables from scrapers.env file")
except ImportError:
    logging.info("python-dotenv not available - using system environment variables only")

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options
    UNDETECTED_AVAILABLE = True
except ImportError:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        UNDETECTED_AVAILABLE = False
        print("Warning: undetected-chromedriver not available. Using regular selenium.")
    except ImportError:
        UNDETECTED_AVAILABLE = False
        print("Warning: Selenium not available. Browser functionality will be limited.")

# Attempt to use webdriver_manager for automatic driver install in regular Selenium mode
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser setup and configuration for ChatGPT scraping."""
    
    def __init__(self, headless: bool = False, use_undetected: bool = True):
        """
        Initialize the browser manager.
        
        Args:
            headless: Run browser in headless mode
            use_undetected: Use undetected-chromedriver if available
        """
        self.headless = self._get_env_bool('CHATGPT_HEADLESS', headless)
        # Respect explicit request even in non-headless mode so users can bypass login detection.
        self.use_undetected = (
            self._get_env_bool('CHATGPT_USE_UNDETECTED', use_undetected) and UNDETECTED_AVAILABLE
        )
        self.driver = None
        
        if self.use_undetected:
            logger.info("Using undetected-chromedriver for enhanced anti-detection")
        else:
            logger.info("Using regular selenium webdriver")
    
    def _get_env_bool(self, env_var: str, default: bool) -> bool:
        """Helper method to get boolean from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def create_driver(self):
        """Create and configure the web driver."""
        if not UNDETECTED_AVAILABLE and not self.use_undetected:
            logger.warning("Cannot create driver - Selenium not available")
            return None
            
        try:
            logger.info(f"Creating driver with use_undetected={self.use_undetected}, headless={self.headless}")
            
            if self.use_undetected:
                driver = self._create_undetected_driver()
                if driver:
                    self.driver = driver  # ensure close_driver() can quit instance
                    return driver
                # If undetected failed, fall back automatically
                logger.warning("Undetected-chromedriver failed – falling back to regular Selenium driver")
            # EDIT START: create regular driver and persist reference
            driver = self._create_regular_driver()
            self.driver = driver  # may be None if creation failed
            return driver
            # EDIT END
                
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            return None
    
    def _create_undetected_driver(self):
        """Create undetected-chromedriver instance."""
        logger.info("Using undetected-chromedriver")
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
        
        # ------------------------------------------------------------------
        # Optional driver-version override (helps in CI when Chrome updates).
        # If env UCDRIVER_VERSION_MAIN=137 is set we pre-install that version
        # and point uc.Chrome at it; otherwise fall back to autodetect.
        # ------------------------------------------------------------------
        driver = None
        version_main_env = os.getenv("UCDRIVER_VERSION_MAIN")

        try:
            # Choose driver version: env override → local detection → None (auto)
            chosen_version = None
            if version_main_env:
                chosen_version = int(version_main_env)
            else:
                detected = self._detect_local_chrome_major()
                if detected:
                    chosen_version = detected

            if chosen_version:
                # ------------------------------------------------------------------
                # undetected-chromedriver caches binaries by major version.  If a newer
                # driver is already cached we must force-install and pass explicit path.
                # ------------------------------------------------------------------
                try:
                    logger.info("Installing Chrome driver version_main=%s", chosen_version)
                    driver_bin = uc.install(version_main=chosen_version)
                    logger.info("Driver binary installed at %s", driver_bin)
                except Exception as install_err:
                    logger.warning("Failed to install specified driver version: %s – falling back to default", install_err)
                    driver_bin = None

                chrome_kwargs = {
                    "options": options,
                    "version_main": chosen_version,
                    "patcher_force_close": True,
                }
                if driver_bin:
                    chrome_kwargs["driver_executable_path"] = driver_bin

                driver = uc.Chrome(**chrome_kwargs)
            else:
                logger.info("Creating uc.Chrome instance (auto version)")
                driver = uc.Chrome(options=options)

            logger.info("Successfully created uc.Chrome instance")
            return driver
        except Exception as e:
            logger.error(f"Failed to create uc.Chrome: {e}")
            return None
    
    def _create_regular_driver(self):
        """Create regular selenium webdriver instance."""
        logger.info("Using regular selenium webdriver")
        from selenium import webdriver  # Local import to ensure available even when uc present
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                # EDIT START: auto-install driver matching local Chrome major version when possible
                logger.info("Creating regular Chrome driver via webdriver_manager (auto-download)")
                driver_path = None
                if WEBDRIVER_MANAGER_AVAILABLE:
                    try:
                        local_major = self._detect_local_chrome_major()
                        if local_major:
                            logger.info("Local Chrome major version detected: %s", local_major)
                            try:
                                # webdriver_manager ≥4 supports version_main kwarg
                                driver_path = ChromeDriverManager(version_main=str(local_major)).install()
                            except TypeError:
                                # Fallback for older signature – ignore and install latest
                                logger.debug("webdriver_manager version_main unsupported – fallback to default installer")
                        if not driver_path:
                            driver_path = ChromeDriverManager().install()
                    except Exception as wm_err:
                        logger.warning("webdriver_manager failed to resolve matching driver: %s – falling back to default", wm_err)
                        driver_path = ChromeDriverManager().install()
                # EDIT END
                service = ChromeService(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                logger.info("Creating regular Chrome driver using system-installed chromedriver")
                driver = webdriver.Chrome(options=options)

            logger.info("Successfully created regular Chrome driver")
            return driver
        except Exception as e:
            logger.error(f"Failed to create regular Chrome driver: {e}")
            return None
    
    def close_driver(self):
        """Close the web driver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None 

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_local_chrome_major() -> int | None:
        """Attempt to detect installed Chrome major version (Windows/macOS/Linux).

        Returns the *major* integer (e.g. 137) or None if detection fails.
        """
        try:
            import subprocess, re, platform, shutil

            binary = None
            system = platform.system()
            if system == "Windows":
                binary = shutil.which("chrome") or shutil.which("chrome.exe")
            elif system == "Darwin":
                binary = (
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                )
                if not Path(binary).exists():
                    binary = shutil.which("google-chrome")
            else:
                binary = shutil.which("google-chrome") or shutil.which("chrome")

            if not binary:
                return None

            proc = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
            ver_str = proc.stdout.strip() or proc.stderr.strip()
            match = re.search(r"(\d+)\.\d+\.\d+\.\d+", ver_str)
            if match:
                return int(match.group(1))
        except Exception:
            return None
        return None 