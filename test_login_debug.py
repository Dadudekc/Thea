#!/usr/bin/env python3
"""
ChatGPT Login Debug Test
========================

This test focuses specifically on debugging the login process
to identify why the email field isn't being found.
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
    print(f"🔍 {title}")
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

def debug_login_page():
    """Debug the ChatGPT login page structure."""
    print_section("Login Page Debug")
    
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
            # Navigate to login page
            print_info("Navigating to ChatGPT login page...")
            scraper.driver.get("https://chat.openai.com/auth/login")
            time.sleep(5)
            
            # Debug page information
            print_info(f"Page title: {scraper.driver.title}")
            print_info(f"Current URL: {scraper.driver.current_url}")
            
            # Check if we're redirected
            if "auth/login" not in scraper.driver.current_url:
                print_warning("Page was redirected - may already be logged in")
                if scraper.is_logged_in():
                    print_success("Already logged in!")
                    return True
            
            # Look for common form elements
            print_section("Searching for Form Elements")
            
            # Try to find any input fields
            input_fields = scraper.driver.find_elements("tag name", "input")
            print_info(f"Found {len(input_fields)} input fields on the page")
            
            for i, field in enumerate(input_fields):
                try:
                    field_type = field.get_attribute("type") or "unknown"
                    field_name = field.get_attribute("name") or "no-name"
                    field_id = field.get_attribute("id") or "no-id"
                    field_placeholder = field.get_attribute("placeholder") or "no-placeholder"
                    field_visible = field.is_displayed()
                    field_enabled = field.is_enabled()
                    
                    print_info(f"Input {i+1}: type='{field_type}', name='{field_name}', id='{field_id}', placeholder='{field_placeholder}', visible={field_visible}, enabled={field_enabled}")
                    
                    # Check if this looks like an email field
                    if any(keyword in field_type.lower() or keyword in field_name.lower() or keyword in field_placeholder.lower() 
                           for keyword in ['email', 'username', 'user']):
                        print_success(f"Potential email field found: {field_type} | {field_name} | {field_placeholder}")
                        
                except Exception as e:
                    print_warning(f"Error inspecting input field {i+1}: {e}")
            
            # Look for buttons
            print_section("Searching for Buttons")
            buttons = scraper.driver.find_elements("tag name", "button")
            print_info(f"Found {len(buttons)} buttons on the page")
            
            for i, button in enumerate(buttons):
                try:
                    button_text = button.text.strip() or "no-text"
                    button_type = button.get_attribute("type") or "no-type"
                    button_enabled = button.is_enabled()
                    button_visible = button.is_displayed()
                    
                    print_info(f"Button {i+1}: text='{button_text}', type='{button_type}', enabled={button_enabled}, visible={button_visible}")
                    
                    # Check if this looks like a submit/continue button
                    if any(keyword in button_text.lower() or keyword in button_type.lower() 
                           for keyword in ['continue', 'submit', 'sign in', 'log in', 'next']):
                        print_success(f"Potential submit button found: {button_text} | {button_type}")
                        
                except Exception as e:
                    print_warning(f"Error inspecting button {i+1}: {e}")
            
            # Try to find form elements
            print_section("Searching for Forms")
            forms = scraper.driver.find_elements("tag name", "form")
            print_info(f"Found {len(forms)} forms on the page")
            
            for i, form in enumerate(forms):
                try:
                    form_action = form.get_attribute("action") or "no-action"
                    form_method = form.get_attribute("method") or "no-method"
                    print_info(f"Form {i+1}: action='{form_action}', method='{form_method}'")
                except Exception as e:
                    print_warning(f"Error inspecting form {i+1}: {e}")
            
            # Show page source preview
            print_section("Page Source Preview")
            page_source = scraper.driver.page_source
            print_info(f"Page source length: {len(page_source)} characters")
            
            # Look for key elements in page source
            key_terms = ['email', 'username', 'password', 'login', 'signin', 'continue', 'submit']
            for term in key_terms:
                if term in page_source.lower():
                    print_info(f"Found '{term}' in page source")
            
            # Show first 2000 characters of page source
            preview = page_source[:2000]
            print_info("Page source preview (first 2000 chars):")
            print("=" * 50)
            print(preview)
            print("=" * 50)
            
            print_info("Browser window should be visible for manual inspection")
            print_info("Press Enter to continue...")
            input()
            
            return True
            
    except Exception as e:
        print_error(f"Debug test failed: {e}")
        return False

def main():
    """Run the login debug test."""
    print_header("ChatGPT Login Debug Test")
    print_info("This test will help identify why the login form isn't being found")
    print_info("Make sure you have set CHATGPT_USERNAME and CHATGPT_PASSWORD in your .env file")
    
    success = debug_login_page()
    
    if success:
        print_success("Debug test completed successfully!")
        print_info("Check the output above for form element details")
    else:
        print_error("Debug test failed")
    
    print_header("Debug Complete")

if __name__ == "__main__":
    main() 