#!/usr/bin/env python3
"""
Setup script to help users create their .env file with ChatGPT credentials.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with user input."""
    
    print("🔧 ChatGPT Credentials Setup")
    print("=" * 40)
    print("This script will help you create a .env file with your ChatGPT credentials.")
    print("Your credentials will be stored locally and used for automated login.")
    print()
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response not in ('y', 'yes'):
            print("Setup cancelled.")
            return False
    
    # Get credentials from user
    print("\n📝 Enter your ChatGPT credentials:")
    
    username = input("Email/Username: ").strip()
    if not username:
        print("❌ Username is required!")
        return False
    
    password = input("Password: ").strip()
    if not password:
        print("❌ Password is required!")
        return False
    
    # Optional settings
    print("\n⚙️  Optional settings (press Enter to use defaults):")
    
    cookie_file = input("Cookie file path (default: chatgpt_cookies.pkl): ").strip()
    if not cookie_file:
        cookie_file = "chatgpt_cookies.pkl"
    
    headless = input("Run in headless mode? (y/N): ").strip().lower()
    headless = "true" if headless in ('y', 'yes') else "false"
    
    timeout = input("Timeout in seconds (default: 30): ").strip()
    if not timeout:
        timeout = "30"
    
    use_undetected = input("Use undetected-chromedriver? (Y/n): ").strip().lower()
    use_undetected = "false" if use_undetected in ('n', 'no') else "true"
    
    # Create .env content
    env_content = f"""# ChatGPT Credentials
CHATGPT_USERNAME={username}
CHATGPT_PASSWORD={password}

# Cookie file path
CHATGPT_COOKIE_FILE={cookie_file}

# Scraper settings
CHATGPT_HEADLESS={headless}
CHATGPT_TIMEOUT={timeout}
CHATGPT_USE_UNDETECTED={use_undetected}

# Optional: Logging settings
# DREAMSCAPE_LOG_LEVEL=INFO
# DREAMSCAPE_DEBUG=false
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        print(f"🔐 Username: {username[:3]}***{username[-3:] if len(username) > 6 else ''}")
        print(f"🍪 Cookie file: {cookie_file}")
        print(f"⚙️  Headless: {headless}")
        print(f"⏱️  Timeout: {timeout}s")
        print(f"🛡️  Undetected: {use_undetected}")
        
        print("\n🚀 You can now run the scraper with automated login!")
        print("   python examples/automated_login_example.py login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_env_file():
    """Test if .env file is properly configured."""
    
    print("\n🧪 Testing .env file configuration...")
    
    # Try to load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not installed - install with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False
    
    # Check required variables
    username = os.getenv('CHATGPT_USERNAME')
    password = os.getenv('CHATGPT_PASSWORD')
    
    if not username:
        print("❌ CHATGPT_USERNAME not found in .env file")
        return False
    
    if not password:
        print("❌ CHATGPT_PASSWORD not found in .env file")
        return False
    
    print(f"✅ Username: {username[:3]}***{username[-3:] if len(username) > 6 else ''}")
    print("✅ Password: [HIDDEN]")
    
    # Check optional variables
    cookie_file = os.getenv('CHATGPT_COOKIE_FILE', 'chatgpt_cookies.pkl')
    headless = os.getenv('CHATGPT_HEADLESS', 'false')
    timeout = os.getenv('CHATGPT_TIMEOUT', '30')
    use_undetected = os.getenv('CHATGPT_USE_UNDETECTED', 'true')
    
    print(f"✅ Cookie file: {cookie_file}")
    print(f"✅ Headless: {headless}")
    print(f"✅ Timeout: {timeout}s")
    print(f"✅ Undetected: {use_undetected}")
    
    print("\n🎉 .env file is properly configured!")
    return True

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_env_file()
        elif command == "test":
            test_env_file()
        elif command == "help":
            print("Setup script commands:")
            print("  python setup_env.py create  - Create new .env file")
            print("  python setup_env.py test    - Test existing .env file")
            print("  python setup_env.py help    - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    else:
        # Default: create .env file
        create_env_file()

if __name__ == "__main__":
    main() 