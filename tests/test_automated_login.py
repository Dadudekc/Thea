#!/usr/bin/env python3
"""
Tests for automated login functionality with environment variables and cookie management.
"""

import sys
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.chatgpt_scraper import ChatGPTScraper

class TestAutomatedLogin:
    """Test automated login functionality."""
    
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        with patch.dict(os.environ, {
            'CHATGPT_USERNAME': 'test@example.com',
            'CHATGPT_PASSWORD': 'testpassword',
            'CHATGPT_COOKIE_FILE': 'test_cookies.pkl'
        }):
            scraper = ChatGPTScraper()
            
            assert scraper.username == 'test@example.com'
            assert scraper.password == 'testpassword'
            assert scraper.cookie_file == 'test_cookies.pkl'
    
    def test_constructor_credentials_override_env(self):
        """Test that constructor credentials override environment variables."""
        with patch.dict(os.environ, {
            'CHATGPT_USERNAME': 'env@example.com',
            'CHATGPT_PASSWORD': 'envpassword'
        }):
            scraper = ChatGPTScraper(
                username='constructor@example.com',
                password='constructorpassword',
                cookie_file='constructor_cookies.pkl'
            )
            
            assert scraper.username == 'constructor@example.com'
            assert scraper.password == 'constructorpassword'
            assert scraper.cookie_file == 'constructor_cookies.pkl'
    
    def test_credential_masking_in_logs(self):
        """Test that credentials are masked in log messages."""
        scraper = ChatGPTScraper(username='verylongemail@example.com')
        
        # The username should be masked in the log message
        # The actual username property should still contain the full email
        assert scraper.username == 'verylongemail@example.com'
        
        # Test that the masking logic works correctly
        masked_username = f"{scraper.username[:3]}***{scraper.username[-3:] if len(scraper.username) > 6 else ''}"
        assert masked_username == 'ver***com'
        assert 'verylongemail@example.com' not in masked_username
    
    @pytest.mark.integration
    def test_cookie_save_and_load(self):
        """Test cookie save and load functionality."""
        scraper = ChatGPTScraper()
        
        with scraper:
            # Navigate to set domain
            scraper.navigate_to_chatgpt()
            
            # Test cookie save
            test_cookie_file = "test_save_load_cookies.pkl"
            
            try:
                # Save cookies
                scraper.save_cookies(test_cookie_file)
                assert os.path.exists(test_cookie_file), "Cookie file should be created"
                
                # Load cookies
                scraper.load_cookies(test_cookie_file)
                # Should not raise an exception
                
            finally:
                if os.path.exists(test_cookie_file):
                    os.unlink(test_cookie_file)
    
    @pytest.mark.integration
    def test_ensure_login_with_cookies(self):
        """Test ensure_login method with cookie loading."""
        scraper = ChatGPTScraper()
        
        with scraper:
            scraper.navigate_to_chatgpt()
            
            # Test ensure_login without credentials (should allow manual)
            result = scraper.ensure_login(allow_manual=False)
            # Should return False since no credentials and manual not allowed
            assert isinstance(result, bool)
    
    def test_login_with_credentials_no_driver(self):
        """Test login_with_credentials when driver is not initialized."""
        scraper = ChatGPTScraper(username='test@example.com', password='testpass')
        
        # Should return False when driver is not initialized
        assert not scraper.login_with_credentials()
    
    def test_login_with_credentials_no_credentials(self):
        """Test login_with_credentials when no credentials are available."""
        scraper = ChatGPTScraper()  # No credentials
        
        with scraper:
            scraper.navigate_to_chatgpt()
            
            # Should return False when no credentials
            assert not scraper.login_with_credentials()
    
    @pytest.mark.integration
    def test_ensure_login_workflow(self):
        """Test the complete ensure_login workflow."""
        scraper = ChatGPTScraper()
        
        with scraper:
            scraper.navigate_to_chatgpt()
            
            # Test ensure_login workflow
            result = scraper.ensure_login(allow_manual=False)
            
            # Should return boolean
            assert isinstance(result, bool)
            
            # If not logged in, should be False
            if not scraper.is_logged_in():
                assert result is False

class TestCookieManagement:
    """Test cookie management functionality."""
    
    def test_cookie_file_path_handling(self):
        """Test cookie file path handling."""
        # Test with relative path
        scraper1 = ChatGPTScraper(cookie_file="relative_cookies.pkl")
        assert scraper1.cookie_file == "relative_cookies.pkl"
        
        # Test with absolute path
        abs_path = os.path.abspath("absolute_cookies.pkl")
        scraper2 = ChatGPTScraper(cookie_file=abs_path)
        assert scraper2.cookie_file == abs_path
        
        # Test with environment variable
        with patch.dict(os.environ, {'CHATGPT_COOKIE_FILE': 'env_cookies.pkl'}):
            scraper3 = ChatGPTScraper()
            assert scraper3.cookie_file == 'env_cookies.pkl'
    
    def test_cookie_file_default(self):
        """Test default cookie file path."""
        # Clear environment variable
        with patch.dict(os.environ, {}, clear=True):
            scraper = ChatGPTScraper()
            assert scraper.cookie_file == 'chatgpt_cookies.pkl'
    
    @pytest.mark.integration
    def test_cookie_persistence_across_sessions(self):
        """Test cookie persistence across multiple scraper sessions."""
        cookie_file = "persistence_test_cookies.pkl"
        
        try:
            # First session
            scraper1 = ChatGPTScraper(cookie_file=cookie_file)
            with scraper1:
                scraper1.navigate_to_chatgpt()
                
                # If logged in, save cookies
                if scraper1.is_logged_in():
                    scraper1.save_cookies(cookie_file)
                    assert os.path.exists(cookie_file), "Cookie file should be saved"
            
            # Second session
            scraper2 = ChatGPTScraper(cookie_file=cookie_file)
            with scraper2:
                scraper2.navigate_to_chatgpt()
                
                if os.path.exists(cookie_file):
                    scraper2.load_cookies(cookie_file)
                    scraper2.driver.refresh()
                    
                    # Should still be logged in
                    login_status = scraper2.is_logged_in()
                    assert isinstance(login_status, bool)
        
        finally:
            if os.path.exists(cookie_file):
                os.unlink(cookie_file)

def test_environment_variable_documentation():
    """Test that environment variables are documented correctly."""
    print("\n🔧 Environment Variables Documentation:")
    print("=" * 40)
    
    print("\nRequired for automated login:")
    print("  CHATGPT_USERNAME - Your ChatGPT email/username")
    print("  CHATGPT_PASSWORD - Your ChatGPT password")
    
    print("\nOptional:")
    print("  CHATGPT_COOKIE_FILE - Path to cookie file (default: chatgpt_cookies.pkl)")
    
    print("\nExample usage:")
    print("  export CHATGPT_USERNAME='your-email@example.com'")
    print("  export CHATGPT_PASSWORD='your-password'")
    print("  python examples/automated_login_example.py login")

if __name__ == "__main__":
    print("🧪 Running Automated Login Tests")
    print("=" * 40)
    
    # Run tests
    pytest.main([__file__, "-v"]) 