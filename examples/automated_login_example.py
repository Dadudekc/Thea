#!/usr/bin/env python3
"""
Example: Automated ChatGPT Login with Environment Variables and Cookie Management
Demonstrates how to use environment variables for credentials and cookie persistence.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def example_automated_login():
    """Example of automated login using environment variables from .env file."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import logging
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print("🚀 Starting Automated Login Example")
        print("=" * 50)
        
        # Check if .env file exists
        env_file = Path(".env")
        if env_file.exists():
            print("✅ Found .env file - loading credentials automatically!")
        else:
            print("⚠️  No .env file found!")
            print("💡 Create one with: python setup_env.py create")
            print("   Or set environment variables manually:")
            print("   export CHATGPT_USERNAME='your-email@example.com'")
            print("   export CHATGPT_PASSWORD='your-password'")
            print("\n💡 Will fall back to manual login...")
        
        # Check if credentials are available
        username = os.getenv('CHATGPT_USERNAME')
        password = os.getenv('CHATGPT_PASSWORD')
        
        if not username or not password:
            print("⚠️  Credentials not found in environment variables:")
            print("   Set CHATGPT_USERNAME and CHATGPT_PASSWORD in .env file")
            print("   Run: python setup_env.py create")
            print("\n💡 Will fall back to manual login...")
        
        # Initialize scraper with cookie management
        # The scraper will automatically load settings from .env file
        scraper = ChatGPTScraper(
            headless=False,  # Show browser for debugging
            timeout=30,
            use_undetected=True,  # Use anti-detection
            # username and password will be loaded from .env automatically
            cookie_file="my_chatgpt_cookies.pkl"  # Custom cookie file
        )
        
        print(f"✅ Scraper initialized")
        print(f"   Username: {'Configured' if username else 'Not set'}")
        print(f"   Password: {'Configured' if password else 'Not set'}")
        print(f"   Cookie file: {scraper.cookie_file}")
        print(f"   Headless: {scraper.headless}")
        print(f"   Timeout: {scraper.timeout}s")
        print(f"   Undetected: {scraper.use_undetected}")
        
        # Use context manager for automatic cleanup
        with scraper:
            if not scraper.driver:
                print("❌ Failed to start driver")
                return False
            
            print("\n🌐 Navigating to ChatGPT...")
            
            # Navigate to ChatGPT
            if not scraper.navigate_to_chatgpt():
                print("❌ Failed to navigate to ChatGPT")
                return False
            
            print("✅ Successfully navigated to ChatGPT")
            
            # Try automated login
            print("\n🔐 Attempting login...")
            if scraper.ensure_login():
                print("✅ Login successful!")
                
                # Get conversation list
                conversations = scraper.get_conversation_list()
                print(f"📋 Found {len(conversations)} conversations")
                
                # Display first few conversations
                for i, conv in enumerate(conversations[:3]):
                    print(f"  {i+1}. {conv.get('title', 'Untitled')}")
                
                print(f"\n💾 Cookies saved to: {scraper.cookie_file}")
                print("🔄 Next time you run this, it will use saved cookies!")
                
            else:
                print("❌ Login failed")
                return False
        
        print("\n✅ Automated login example completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def example_cookie_persistence():
    """Example of cookie persistence across sessions."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import logging
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print("🔄 Testing Cookie Persistence")
        print("=" * 40)
        
        cookie_file = "test_persistence_cookies.pkl"
        
        # First session - login and save cookies
        print("\n1️⃣ First session - logging in...")
        scraper1 = ChatGPTScraper(
            headless=False,
            use_undetected=True,
            cookie_file=cookie_file
        )
        
        with scraper1:
            scraper1.navigate_to_chatgpt()
            
            if scraper1.ensure_login():
                print("✅ First session login successful")
                print(f"💾 Cookies saved to {cookie_file}")
            else:
                print("❌ First session login failed")
                return False
        
        # Second session - load cookies
        print("\n2️⃣ Second session - loading cookies...")
        scraper2 = ChatGPTScraper(
            headless=False,
            use_undetected=True,
            cookie_file=cookie_file
        )
        
        with scraper2:
            scraper2.navigate_to_chatgpt()
            
            # Try to load cookies
            if os.path.exists(cookie_file):
                scraper2.load_cookies(cookie_file)
                scraper2.driver.refresh()
                
                if scraper2.is_logged_in():
                    print("✅ Second session - still logged in with cookies!")
                    
                    # Get conversations to verify
                    conversations = scraper2.get_conversation_list()
                    print(f"📋 Found {len(conversations)} conversations")
                    
                    print("🎉 Cookie persistence works!")
                    return True
                else:
                    print("❌ Second session - not logged in despite cookies")
                    return False
            else:
                print("❌ Cookie file not found")
                return False
        
    except Exception as e:
        print(f"❌ Cookie persistence test error: {e}")
        return False

def example_environment_setup():
    """Show how to set up environment variables using .env file."""
    
    print("🔧 Environment Variable Setup Guide")
    print("=" * 40)
    
    print("\n📝 Easiest way: Use .env file")
    print("\n1️⃣ Create .env file:")
    print("   python setup_env.py create")
    print("   (This will guide you through the setup)")
    
    print("\n2️⃣ Or create .env file manually:")
    print("   Copy env.example to .env and edit:")
    print("   cp env.example .env")
    print("   # Edit .env with your credentials")
    
    print("\n3️⃣ .env file example:")
    print("   CHATGPT_USERNAME=your-email@example.com")
    print("   CHATGPT_PASSWORD=your-password")
    print("   CHATGPT_COOKIE_FILE=my_cookies.pkl")
    print("   CHATGPT_HEADLESS=false")
    print("   CHATGPT_TIMEOUT=30")
    print("   CHATGPT_USE_UNDETECTED=true")
    
    print("\n💡 Alternative: Manual environment variables")
    print("\nLinux/Mac:")
    print("export CHATGPT_USERNAME='your-email@example.com'")
    print("export CHATGPT_PASSWORD='your-password'")
    print("export CHATGPT_COOKIE_FILE='my_cookies.pkl'")
    
    print("\nWindows (Command Prompt):")
    print("set CHATGPT_USERNAME=your-email@example.com")
    print("set CHATGPT_PASSWORD=your-password")
    print("set CHATGPT_COOKIE_FILE=my_cookies.pkl")
    
    print("\nWindows (PowerShell):")
    print("$env:CHATGPT_USERNAME='your-email@example.com'")
    print("$env:CHATGPT_PASSWORD='your-password'")
    print("$env:CHATGPT_COOKIE_FILE='my_cookies.pkl'")
    
    print("\n💡 Security Tips:")
    print("  • Use .env file for development")
    print("  • Never commit .env to version control")
    print("  • Use environment variables in production")
    print("  • Consider using a password manager")
    
    print("\n🧪 Test your setup:")
    print("  python setup_env.py test")
    print("  python examples/automated_login_example.py login")

if __name__ == "__main__":
    print("Digital Dreamscape - Automated Login Example")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "login":
            example_automated_login()
        elif command == "cookies":
            example_cookie_persistence()
        elif command == "setup":
            example_environment_setup()
        elif command == "help":
            print("Available commands:")
            print("  python automated_login_example.py login   - Test automated login")
            print("  python automated_login_example.py cookies - Test cookie persistence")
            print("  python automated_login_example.py setup   - Show environment setup")
            print("  python automated_login_example.py help    - Show this help")
            print("\n💡 Quick setup:")
            print("  1. python setup_env.py create  - Create .env file")
            print("  2. python automated_login_example.py login  - Test login")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    else:
        # Default: show setup guide
        example_environment_setup()
        print("\n" + "="*50)
        print("💡 Quick start:")
        print("  1. python setup_env.py create  - Create .env file")
        print("  2. python automated_login_example.py login  - Test automated login") 