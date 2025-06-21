# Automated Login Guide

## Overview

The Digital Dreamscape ChatGPT scraper now supports **automated login** using `.env` files and **cookie persistence** for seamless session management. This eliminates the need for manual login in most cases.

## Features

### 🔐 Automated Login
- **`.env` File Support**: Easy credential management with `python-dotenv`
- **Environment Variable Credentials**: Use `CHATGPT_USERNAME` and `CHATGPT_PASSWORD`
- **Constructor Override**: Pass credentials directly to scraper constructor
- **Secure Credential Masking**: Passwords are hidden in logs
- **Fallback to Manual**: Graceful degradation if automated login fails

### 🍪 Cookie Management
- **Session Persistence**: Save and reload login sessions
- **Custom Cookie Files**: Specify custom cookie file paths
- **Automatic Cookie Loading**: Load cookies on startup
- **Cross-Session Persistence**: Maintain login across multiple runs

### 🛡️ Security Features
- **Credential Masking**: Usernames and passwords are masked in logs
- **`.env` File Support**: Secure credential storage
- **Cookie Encryption**: Cookies are stored securely
- **Graceful Fallbacks**: Multiple login strategies

## Quick Start

### 1. Easy Setup with .env File

**Option A: Interactive Setup (Recommended)**
```bash
python setup_env.py create
```
This will guide you through creating your `.env` file interactively.

**Option B: Manual Setup**
```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
# CHATGPT_USERNAME=your-email@example.com
# CHATGPT_PASSWORD=your-password
```

### 2. Basic Usage

```python
from scrapers.chatgpt_scraper import ChatGPTScraper

# Automatically loads from .env file
scraper = ChatGPTScraper()

with scraper:
    # Navigate and login automatically
    scraper.navigate_to_chatgpt()
    
    if scraper.ensure_login():
        print("✅ Logged in successfully!")
        
        # Get conversations
        conversations = scraper.get_conversation_list()
        print(f"Found {len(conversations)} conversations")
    else:
        print("❌ Login failed")
```

### 3. Advanced Usage

```python
# Custom credentials and cookie file
scraper = ChatGPTScraper(
    username='custom@example.com',
    password='custompassword',
    cookie_file='custom_cookies.pkl'
)

with scraper:
    scraper.navigate_to_chatgpt()
    
    # Try automated login, fall back to manual if needed
    if scraper.ensure_login(allow_manual=True):
        print("✅ Login successful!")
    else:
        print("❌ All login methods failed")
```

## Login Strategies

The scraper uses a **multi-tier login strategy**:

### 1. Cookie Loading (Fastest)
- Loads saved cookies from previous sessions
- Instant login if cookies are valid
- No credentials needed

### 2. Automated Login (Recommended)
- Uses environment variables or constructor credentials
- Bypasses bot detection with undetected-chromedriver
- Saves cookies for future use

### 3. Manual Login (Fallback)
- Opens browser for manual login
- Waits for user interaction
- Saves cookies after successful login

## Environment Variables

The scraper supports configuration through environment variables, which can be set in a `.env` file or system environment.

### .env File Format

Create a `.env` file in your project root:

```bash
# ChatGPT Credentials
CHATGPT_USERNAME=your-email@example.com
CHATGPT_PASSWORD=your-password

# Cookie file path
CHATGPT_COOKIE_FILE=chatgpt_cookies.pkl

# Scraper settings
CHATGPT_HEADLESS=false
CHATGPT_TIMEOUT=30
CHATGPT_USE_UNDETECTED=true

# Optional: Logging settings
DREAMSCAPE_LOG_LEVEL=INFO
DREAMSCAPE_DEBUG=false
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHATGPT_USERNAME` | Yes* | None | Your ChatGPT email/username |
| `CHATGPT_PASSWORD` | Yes* | None | Your ChatGPT password |
| `CHATGPT_COOKIE_FILE` | No | `chatgpt_cookies.pkl` | Path to cookie file |
| `CHATGPT_HEADLESS` | No | `false` | Run browser in headless mode |
| `CHATGPT_TIMEOUT` | No | `30` | Timeout for web operations (seconds) |
| `CHATGPT_USE_UNDETECTED` | No | `true` | Use undetected-chromedriver |
| `DREAMSCAPE_LOG_LEVEL` | No | `INFO` | Logging level |
| `DREAMSCAPE_DEBUG` | No | `false` | Enable debug mode |

*Required for automated login, optional for manual login

### Quick Setup Commands

```bash
# Interactive setup (recommended)
python setup_env.py create

# Test your .env file
python setup_env.py test

# Manual setup
cp env.example .env
# Edit .env with your credentials
```

## Cookie Management

### Cookie File Locations
- **Default**: `chatgpt_cookies.pkl` (project root)
- **Custom**: Specify path in constructor or environment variable
- **Relative/Absolute**: Both supported

### Cookie Operations

```python
# Save cookies manually
scraper.save_cookies("my_cookies.pkl")

# Load cookies manually
scraper.load_cookies("my_cookies.pkl")

# Check if cookie file exists
import os
if os.path.exists("my_cookies.pkl"):
    scraper.load_cookies("my_cookies.pkl")
```

### Cookie Persistence Example

```python
# First session - login and save cookies
scraper1 = ChatGPTScraper(cookie_file="session_cookies.pkl")
with scraper1:
    scraper1.navigate_to_chatgpt()
    if scraper1.ensure_login():
        print("✅ First session login successful")
        # Cookies automatically saved

# Second session - load cookies
scraper2 = ChatGPTScraper(cookie_file="session_cookies.pkl")
with scraper2:
    scraper2.navigate_to_chatgpt()
    scraper2.load_cookies("session_cookies.pkl")
    scraper2.driver.refresh()
    
    if scraper2.is_logged_in():
        print("✅ Second session - still logged in!")
```

## Security Best Practices

### 1. .env File Management
```bash
# Create .env file securely
python setup_env.py create

# Never commit .env to version control
echo ".env" >> .gitignore

# Use different .env files for different environments
cp .env .env.production
cp .env .env.development
```

### 2. Credential Management
- **Use `.env` files** for development and GUI integration
- **Never commit credentials** to version control
- **Use password managers** for credential storage
- **Rotate credentials** regularly
- **Use environment variables** in production

### 3. Cookie Security
- **Store cookies securely** (not in public directories)
- **Delete old cookies** periodically
- **Use custom cookie paths** for different environments

### 4. GUI Integration
- **Load credentials from `.env`** in GUI applications
- **Provide credential setup wizard** using `setup_env.py`
- **Mask credentials** in GUI displays
- **Store settings** in user preferences

```python
# Example: GUI credential loading
from dotenv import load_dotenv
import os

def load_credentials():
    """Load credentials for GUI application."""
    load_dotenv()
    return {
        'username': os.getenv('CHATGPT_USERNAME'),
        'password': os.getenv('CHATGPT_PASSWORD'),
        'cookie_file': os.getenv('CHATGPT_COOKIE_FILE', 'chatgpt_cookies.pkl')
    }
```

## Error Handling

### Common Issues

**1. "No credentials available for automated login"**
```python
# Solution: Set environment variables or pass credentials
scraper = ChatGPTScraper(
    username='your-email@example.com',
    password='your-password'
)
```

**2. "Could not find email field"**
```python
# Solution: ChatGPT login page may have changed
# Fall back to manual login
scraper.ensure_login(allow_manual=True)
```

**3. "Could not add cookie"**
```python
# Solution: Navigate to domain first
scraper.navigate_to_chatgpt()
scraper.load_cookies("cookies.pkl")
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

scraper = ChatGPTScraper()
# Will show detailed login process
```

## Examples

### Complete Workflow Example

```python
from scrapers.chatgpt_scraper import ChatGPTScraper

def scrape_chatgpt():
    scraper = ChatGPTScraper(
        headless=False,  # Show browser for debugging
        use_undetected=True,  # Bypass bot detection
        cookie_file="my_session.pkl"
    )
    
    with scraper:
        # Navigate to ChatGPT
        scraper.navigate_to_chatgpt()
        
        # Ensure login (tries cookies, then automated, then manual)
        if scraper.ensure_login():
            print("✅ Login successful!")
            
            # Extract conversations
            conversations = scraper.get_conversation_list()
            print(f"📋 Found {len(conversations)} conversations")
            
            # Process conversations
            for conv in conversations[:5]:  # First 5 conversations
                print(f"  - {conv['title']}")
                
            return conversations
        else:
            print("❌ Login failed")
            return []

if __name__ == "__main__":
    conversations = scrape_chatgpt()
    print(f"✅ Scraped {len(conversations)} conversations")
```

### Production Example

```python
import os
from scrapers.chatgpt_scraper import ChatGPTScraper

# Production setup with environment variables
scraper = ChatGPTScraper(
    headless=True,  # Run in background
    use_undetected=True,
    cookie_file=os.getenv('CHATGPT_COOKIE_FILE', 'prod_cookies.pkl')
)

with scraper:
    scraper.navigate_to_chatgpt()
    
    # Automated login only (no manual fallback)
    if scraper.ensure_login(allow_manual=False):
        conversations = scraper.get_conversation_list()
        # Process conversations...
    else:
        print("❌ Automated login failed - check credentials")
```

## Testing

### Setup and Configuration Testing

```bash
# Test .env file setup
python setup_env.py test

# Create .env file interactively
python setup_env.py create

# Test automated login example
python examples/automated_login_example.py login
```

### Run Automated Login Tests

```bash
# Test environment variable loading
pytest tests/test_automated_login.py -v

# Test cookie management
pytest tests/test_automated_login.py -v -k "cookie"

# Test credential masking
pytest tests/test_automated_login.py -v -k "credential"
```

### Manual Testing

```bash
# Test automated login example
python examples/automated_login_example.py login

# Test cookie persistence
python examples/automated_login_example.py cookies

# Show setup guide
python examples/automated_login_example.py setup
```

### GUI Integration Testing

```python
# Test credential loading in GUI context
from dotenv import load_dotenv
import os

def test_gui_credentials():
    """Test credential loading for GUI integration."""
    load_dotenv()
    
    credentials = {
        'username': os.getenv('CHATGPT_USERNAME'),
        'password': os.getenv('CHATGPT_PASSWORD'),
        'cookie_file': os.getenv('CHATGPT_COOKIE_FILE', 'chatgpt_cookies.pkl')
    }
    
    assert credentials['username'], "Username not found in .env"
    assert credentials['password'], "Password not found in .env"
    
    print("✅ GUI credentials loaded successfully")
    return credentials
```

## Troubleshooting

### Login Issues

1. **Check Environment Variables**
   ```bash
   echo $CHATGPT_USERNAME
   echo $CHATGPT_PASSWORD
   ```

2. **Verify Credentials**
   - Test login manually in browser
   - Check for 2FA requirements
   - Ensure account is not locked

3. **Clear Cookies**
   ```python
   import os
   if os.path.exists("chatgpt_cookies.pkl"):
       os.remove("chatgpt_cookies.pkl")
   ```

### Bot Detection Issues

1. **Use Undetected ChromeDriver**
   ```python
   scraper = ChatGPTScraper(use_undetected=True)
   ```

2. **Add Delays**
   ```python
   import time
   time.sleep(5)  # Wait between actions
   ```

3. **Use Headless Mode**
   ```python
   scraper = ChatGPTScraper(headless=True)
   ```

## Migration from Manual Login

### Before (Manual Login)
```python
scraper = ChatGPTScraper()
with scraper:
    scraper.navigate_to_chatgpt()
    # Wait for manual login...
    time.sleep(60)
    if scraper.is_logged_in():
        conversations = scraper.get_conversation_list()
```

### After (Automated Login)
```python
scraper = ChatGPTScraper()  # Uses environment variables
with scraper:
    scraper.navigate_to_chatgpt()
    if scraper.ensure_login():  # Automatic!
        conversations = scraper.get_conversation_list()
```

## Conclusion

The automated login system with `.env` file support provides:

- ✅ **Easy Setup**: Interactive `.env` file creation with `setup_env.py`
- ✅ **GUI Integration Ready**: Perfect for loading credentials in GUI applications
- ✅ **Seamless Authentication**: No more manual login
- ✅ **Session Persistence**: Stay logged in across runs
- ✅ **Security**: Credentials are masked and secure
- ✅ **Flexibility**: Multiple login strategies
- ✅ **Reliability**: Graceful fallbacks

### GUI Integration Benefits

The `.env` file approach makes it easy to integrate automated login into GUI applications:

1. **Credential Management**: GUI can load credentials from `.env` file
2. **Setup Wizard**: Use `setup_env.py` as a credential setup wizard
3. **Configuration**: All scraper settings can be configured via `.env`
4. **Security**: Credentials are stored securely and masked in logs
5. **Portability**: `.env` files work across different environments

Set up your `.env` file and enjoy automated ChatGPT scraping with easy GUI integration! 🚀 