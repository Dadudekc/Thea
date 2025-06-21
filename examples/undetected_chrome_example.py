#!/usr/bin/env python3
"""
Example: Using Undetected ChromeDriver with ChatGPT Scraper
Demonstrates how to use the enhanced anti-detection capabilities.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def example_undetected_scraping():
    """Example of using undetected-chromedriver for ChatGPT scraping."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import logging
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print("🚀 Starting undetected-chromedriver example...")
        
        # Initialize scraper with undetected-chromedriver
        scraper = ChatGPTScraper(
            headless=False,  # Set to True for headless mode
            timeout=30,
            use_undetected=True  # Enable undetected-chromedriver
        )
        
        print(f"✅ Scraper initialized with undetected mode: {scraper.use_undetected}")
        
        # Use context manager for automatic cleanup
        with scraper:
            if not scraper.driver:
                print("❌ Failed to start driver")
                return False
            
            print("🌐 Navigating to ChatGPT...")
            
            # Navigate to ChatGPT
            if scraper.navigate_to_chatgpt():
                print("✅ Successfully navigated to ChatGPT")
                
                # Check login status
                if scraper.is_logged_in():
                    print("✅ User is logged in")
                    
                    # Get conversation list
                    conversations = scraper.get_conversation_list()
                    print(f"📋 Found {len(conversations)} conversations")
                    
                    # Display first few conversations
                    for i, conv in enumerate(conversations[:3]):
                        print(f"  {i+1}. {conv.get('title', 'Untitled')}")
                    
                else:
                    print("⚠️  User is not logged in")
                    print("💡 Please log in manually in the browser window")
                    
                    # Wait for user to log in
                    input("Press Enter after logging in...")
                    
                    # Check again
                    if scraper.is_logged_in():
                        print("✅ User is now logged in")
                        conversations = scraper.get_conversation_list()
                        print(f"📋 Found {len(conversations)} conversations")
                    else:
                        print("❌ Still not logged in")
                
            else:
                print("❌ Failed to navigate to ChatGPT")
                return False
        
        print("✅ Example completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def example_comparison():
    """Compare regular selenium vs undetected-chromedriver."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        
        print("🔍 Comparing regular selenium vs undetected-chromedriver...")
        
        # Test regular selenium
        print("\n1. Testing regular selenium...")
        scraper_regular = ChatGPTScraper(use_undetected=False, headless=True)
        print(f"   Regular mode: {not scraper_regular.use_undetected}")
        
        # Test undetected-chromedriver
        print("\n2. Testing undetected-chromedriver...")
        scraper_undetected = ChatGPTScraper(use_undetected=True, headless=True)
        print(f"   Undetected mode: {scraper_undetected.use_undetected}")
        
        print("\n✅ Comparison completed!")
        return True
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        return False

if __name__ == "__main__":
    print("Digital Dreamscape - Undetected ChromeDriver Example")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scrape":
            example_undetected_scraping()
        elif command == "compare":
            example_comparison()
        elif command == "help":
            print("Available commands:")
            print("  python undetected_chrome_example.py scrape  - Run scraping example")
            print("  python undetected_chrome_example.py compare - Compare modes")
            print("  python undetected_chrome_example.py help    - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    else:
        # Default: run scraping example
        example_undetected_scraping() 