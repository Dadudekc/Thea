#!/usr/bin/env python3
"""
Modern ChatGPT Login Test
=========================

This test handles ChatGPT's current authentication flow,
which may use OAuth or a different login method than traditional forms.
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def test_modern_login():
    """Test modern ChatGPT login flow."""
    print_section("Modern Login Test")
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        
        # Check credentials
        email = os.getenv('CHATGPT_USERNAME')
        password = os.getenv('CHATGPT_PASSWORD')
        
        if not email or not password:
            print_error("No credentials found in environment variables")
            return False
        
        print_success(f"Found credentials for: {email}")
        
        # Create scraper with visible browser
        scraper = ChatGPTScraper(
            headless=False,  # Show browser for debugging
            use_undetected=True,
            timeout=30
        )
        
        print_info("Initializing scraper...")
        
        with scraper:
            # Navigate to main ChatGPT page first
            print_info("Navigating to main ChatGPT page...")
            scraper.driver.get("https://chat.openai.com")
            time.sleep(5)
            
            print_info(f"Page title: {scraper.driver.title}")
            print_info(f"Current URL: {scraper.driver.current_url}")
            
            # Check if already logged in
            if scraper.is_logged_in():
                print_success("Already logged in!")
                return True
            
            # Try to find login button on main page
            print_section("Looking for Login Button")
            
            # Common selectors for login buttons
            login_button_selectors = [
                "button:contains('Log in')",
                "button:contains('Sign in')",
                "a:contains('Log in')",
                "a:contains('Sign in')",
                "[data-testid='login-button']",
                ".login-button",
                ".signin-button"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    print_info(f"Trying login button selector: {selector}")
                    login_button = scraper.driver.find_element("css selector", selector)
                    if login_button.is_displayed() and login_button.is_enabled():
                        print_success(f"Found login button with selector: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                # Try XPath selectors
                xpath_selectors = [
                    "//button[contains(text(), 'Log in')]",
                    "//button[contains(text(), 'Sign in')]",
                    "//a[contains(text(), 'Log in')]",
                    "//a[contains(text(), 'Sign in')]",
                    "//*[contains(text(), 'Log in')]",
                    "//*[contains(text(), 'Sign in')]"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        print_info(f"Trying login button XPath: {xpath}")
                        login_button = scraper.driver.find_element("xpath", xpath)
                        if login_button.is_displayed() and login_button.is_enabled():
                            print_success(f"Found login button with XPath: {xpath}")
                            break
                    except:
                        continue
            
            if login_button:
                print_info("Clicking login button...")
                login_button.click()
                time.sleep(5)
                
                print_info(f"After login click - URL: {scraper.driver.current_url}")
                print_info(f"After login click - Title: {scraper.driver.title}")
            else:
                print_warning("No login button found, trying direct navigation...")
                scraper.driver.get("https://chat.openai.com/auth/login")
                time.sleep(5)
            
            # Now look for the actual login form
            print_section("Looking for Login Form")
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if we're on a login page
            current_url = scraper.driver.current_url
            print_info(f"Current URL: {current_url}")
            
            if "auth/login" in current_url or "login" in current_url.lower():
                print_info("On login page, looking for form elements...")
                
                # Look for any input fields
                inputs = scraper.driver.find_elements("tag name", "input")
                print_info(f"Found {len(inputs)} input fields")
                
                for i, inp in enumerate(inputs):
                    try:
                        inp_type = inp.get_attribute("type") or "unknown"
                        inp_name = inp.get_attribute("name") or "no-name"
                        inp_id = inp.get_attribute("id") or "no-id"
                        inp_placeholder = inp.get_attribute("placeholder") or "no-placeholder"
                        
                        print_info(f"Input {i+1}: type='{inp_type}', name='{inp_name}', id='{inp_id}', placeholder='{inp_placeholder}'")
                        
                        # If this looks like an email field, try to fill it
                        if any(keyword in inp_type.lower() or keyword in inp_name.lower() or keyword in inp_placeholder.lower() 
                               for keyword in ['email', 'username', 'user']):
                            print_success(f"Found email field: {inp_type} | {inp_name} | {inp_placeholder}")
                            
                            # Try to fill the email field
                            try:
                                inp.clear()
                                inp.send_keys(email)
                                print_success("Entered email address")
                                time.sleep(1)
                                
                                # Look for continue/submit button
                                buttons = scraper.driver.find_elements("tag name", "button")
                                for button in buttons:
                                    try:
                                        button_text = button.text.strip()
                                        if any(keyword in button_text.lower() for keyword in ['continue', 'next', 'submit']):
                                            print_success(f"Found continue button: {button_text}")
                                            button.click()
                                            print_success("Clicked continue button")
                                            time.sleep(3)
                                            break
                                    except:
                                        continue
                                
                                break
                                
                            except Exception as e:
                                print_warning(f"Error filling email field: {e}")
                                
                    except Exception as e:
                        print_warning(f"Error inspecting input {i+1}: {e}")
                
                # Look for password field
                print_section("Looking for Password Field")
                time.sleep(2)
                
                password_inputs = scraper.driver.find_elements("css selector", "input[type='password']")
                if password_inputs:
                    for inp in password_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            print_success("Found password field")
                            try:
                                inp.clear()
                                inp.send_keys(password)
                                print_success("Entered password")
                                time.sleep(1)
                                
                                # Look for login/submit button
                                buttons = scraper.driver.find_elements("tag name", "button")
                                for button in buttons:
                                    try:
                                        button_text = button.text.strip()
                                        if any(keyword in button_text.lower() for keyword in ['continue', 'sign in', 'log in', 'submit']):
                                            print_success(f"Found login button: {button_text}")
                                            button.click()
                                            print_success("Clicked login button")
                                            time.sleep(10)
                                            break
                                    except:
                                        continue
                                
                                break
                                
                            except Exception as e:
                                print_warning(f"Error filling password field: {e}")
                else:
                    print_warning("No password field found - may be using OAuth")
            
            # Check if login was successful
            time.sleep(5)
            if scraper.is_logged_in():
                print_success("✅ Login successful!")
                
                # Save cookies for future use
                if scraper.cookie_file:
                    scraper.save_cookies(scraper.cookie_file)
                    print_success(f"💾 Cookies saved to {scraper.cookie_file}")
                
                return True
            else:
                print_warning("Login may have failed - not logged in after attempt")
                print_info("This might be due to:")
                print_info("1. OAuth/SSO authentication required")
                print_info("2. CAPTCHA or verification needed")
                print_info("3. Different login flow than expected")
                
                # Offer manual login option
                print_info("Browser window is open for manual login")
                print_info("Please log in manually and press Enter when done...")
                input()
                
                # Check again after manual login
                if scraper.is_logged_in():
                    print_success("✅ Manual login successful!")
                    
                    # Save cookies for future use
                    if scraper.cookie_file:
                        scraper.save_cookies(scraper.cookie_file)
                        print_success(f"💾 Cookies saved to {scraper.cookie_file}")
                    
                    return True
                else:
                    print_error("Manual login also failed")
                    return False
            
    except Exception as e:
        print_error(f"Modern login test failed: {e}")
        return False

def main():
    """Run the modern login test."""
    print_header("Modern ChatGPT Login Test")
    print_info("This test handles ChatGPT's current authentication flow")
    print_info("Make sure you have set CHATGPT_USERNAME and CHATGPT_PASSWORD in your .env file")
    
    success = test_modern_login()
    
    if success:
        print_success("Modern login test completed successfully!")
        print_info("You can now run the full scraping test")
    else:
        print_error("Modern login test failed")
        print_info("Try running the test again or check your credentials")
    
    print_header("Test Complete")

if __name__ == "__main__":
    main() 