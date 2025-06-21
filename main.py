#!/usr/bin/env python3
"""
Digital Dreamscape - Standalone Project
Main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main application entry point."""
    try:
        # Import and run the GUI application
        from gui.main_window import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"Error importing GUI components: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Application error: {e}")
        return 1

def test_template_engine():
    """Test the template engine functionality."""
    try:
        from core.template_engine import render_template
        
        # Create a test template
        test_template = """
        Hello {{ name }}!
        Your value is {{ data.value }}.
        """
        
        # Test rendering
        context = {"name": "World", "data": {"value": 123}}
        result = render_template(test_template, context)
        
        if result:
            print("✅ Template engine test passed!")
            print(f"Result: {result}")
            return True
        else:
            print("❌ Template engine test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Template engine test error: {e}")
        return False

def test_scraper():
    """Test the scraper functionality."""
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        print("✅ Scraper import successful!")
        
        # Test undetected-chromedriver capability
        scraper = ChatGPTScraper(use_undetected=True)
        if hasattr(scraper, 'use_undetected'):
            if scraper.use_undetected:
                print("✅ Undetected-chromedriver capability available!")
            else:
                print("⚠️  Undetected-chromedriver not available, using regular selenium")
        else:
            print("⚠️  Undetected-chromedriver feature not implemented")
        
        # Test demo conversation functionality
        conversations = scraper._get_demo_conversations()
        if conversations and len(conversations) > 0:
            print(f"✅ Demo conversations working: {len(conversations)} conversations")
        else:
            print("❌ Demo conversations not working")
            return False
        
        # Test template integration
        from core.template_engine import render_template
        prompt_template = "Analyze: {{ conversation.title }}"
        rendered = render_template(prompt_template, {"conversation": conversations[0]})
        if rendered and "Analyze:" in rendered:
            print("✅ Template integration working")
        else:
            print("❌ Template integration not working")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Scraper test error: {e}")
        return False

def test_comprehensive_scraping():
    """Test comprehensive scraping functionality (requires manual login)."""
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import tempfile
        import os
        
        print("🧪 Testing comprehensive scraping functionality...")
        print("⚠️  This test requires manual login to ChatGPT")
        
        # Initialize scraper
        scraper = ChatGPTScraper(headless=False, use_undetected=True)
        
        with scraper:
            if not scraper.driver:
                print("❌ Failed to start driver")
                return False
            
            print("🌐 Navigating to ChatGPT...")
            
            # Test navigation
            if not scraper.navigate_to_chatgpt():
                print("❌ Failed to navigate to ChatGPT")
                return False
            
            print("✅ Successfully navigated to ChatGPT")
            
            # Test login detection
            is_logged_in = scraper.is_logged_in()
            print(f"🔐 Login status: {is_logged_in}")
            
            if not is_logged_in:
                print("⚠️  Please log in manually in the browser window")
                print("⏳ Waiting 30 seconds for manual login...")
                import time
                time.sleep(30)
                
                # Check again
                is_logged_in = scraper.is_logged_in()
                print(f"🔐 Login status after wait: {is_logged_in}")
            
            if is_logged_in:
                print("✅ User is logged in")
                
                # Test conversation extraction
                conversations = scraper.get_conversation_list()
                print(f"📋 Found {len(conversations)} conversations")
                
                if conversations:
                    # Test conversation entry and prompting
                    first_conv = conversations[0]
                    print(f"🔍 Testing conversation entry: {first_conv['title']}")
                    
                    if scraper.enter_conversation(first_conv['url']):
                        print("✅ Successfully entered conversation")
                        
                        # Test templated prompt
                        prompt_template = """
                        Please analyze this conversation and provide:
                        1. Key topics discussed
                        2. Main insights
                        3. Action items (if any)
                        
                        Conversation title: {{ conversation.title }}
                        """
                        
                        prompt = render_template(prompt_template, {"conversation": first_conv})
                        print(f"📝 Sending templated prompt: {prompt[:100]}...")
                        
                        if scraper.send_prompt(prompt):
                            print("✅ Successfully sent prompt")
                            
                            # Get response
                            content = scraper.get_conversation_content()
                            if content.get("full_conversation"):
                                print("✅ Successfully received response")
                                print(f"📄 Response length: {len(content['full_conversation'])} characters")
                            else:
                                print("⚠️  No response content received")
                        else:
                            print("❌ Failed to send prompt")
                    else:
                        print("❌ Failed to enter conversation")
                
                # Test saving to file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    temp_file = f.name
                
                try:
                    scraper._save_conversations(conversations, temp_file)
                    if os.path.exists(temp_file):
                        print("✅ Successfully saved conversations to file")
                        os.unlink(temp_file)  # Clean up
                    else:
                        print("❌ Failed to save conversations")
                except Exception as e:
                    print(f"❌ Error saving conversations: {e}")
            else:
                print("❌ User is not logged in - cannot test full functionality")
                return False
        
        print("✅ Comprehensive scraping test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive scraping test error: {e}")
        return False

def test_undetected_chrome():
    """Test the undetected-chromedriver functionality specifically."""
    try:
        import undetected_chromedriver as uc
        print("✅ Undetected-chromedriver import successful!")
        
        # Test basic functionality
        from scrapers.chatgpt_scraper import ChatGPTScraper
        
        # Test with undetected-chromedriver enabled
        scraper_undetected = ChatGPTScraper(use_undetected=True, headless=True)
        print(f"✅ Undetected mode: {scraper_undetected.use_undetected}")
        
        # Test with undetected-chromedriver disabled
        scraper_regular = ChatGPTScraper(use_undetected=False, headless=True)
        print(f"✅ Regular mode: {not scraper_regular.use_undetected}")
        
        return True
    except ImportError as e:
        print(f"❌ Undetected-chromedriver not available: {e}")
        print("Install with: pip install undetected-chromedriver")
        return False
    except Exception as e:
        print(f"❌ Undetected-chromedriver test error: {e}")
        return False

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            print("🧪 Running component tests...")
            template_ok = test_template_engine()
            scraper_ok = test_scraper()
            undetected_ok = test_undetected_chrome()
            
            if template_ok and scraper_ok and undetected_ok:
                print("✅ All component tests passed!")
                sys.exit(0)
            else:
                print("❌ Some component tests failed!")
                sys.exit(1)
        
        elif command == "template":
            test_template_engine()
            sys.exit(0)
        
        elif command == "scraper":
            test_scraper()
            sys.exit(0)
        
        elif command == "undetected_chrome":
            test_undetected_chrome()
            sys.exit(0)
        
        elif command == "comprehensive_scraping":
            test_comprehensive_scraping()
            sys.exit(0)
        
        elif command == "help":
            print("Digital Dreamscape - Available Commands:")
            print("  python main.py          - Start GUI application")
            print("  python main.py test     - Run component tests")
            print("  python main.py template - Test template engine")
            print("  python main.py scraper  - Test scraper")
            print("  python main.py undetected_chrome - Test undetected-chromedriver")
            print("  python main.py comprehensive_scraping - Test comprehensive scraping")
            print("  python main.py help     - Show this help")
            sys.exit(0)
    
    # Default: run the main application
    print("🚀 Starting Digital Dreamscape...")
    sys.exit(main()) 