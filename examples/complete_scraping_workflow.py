#!/usr/bin/env python3
"""
Complete ChatGPT Scraping Workflow Example
Demonstrates the full pipeline: login → extract conversations → enter conversations → send templated prompts
"""

import sys
import os
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_complete_workflow():
    """Run the complete ChatGPT scraping workflow."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        from core.template_engine import render_template
        import logging
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print("🚀 Starting Complete ChatGPT Scraping Workflow")
        print("=" * 60)
        
        cookies_path = "chatgpt_cookies.pkl"
        
        # Step 1: Initialize scraper with undetected-chromedriver
        print("\n1️⃣ Initializing scraper...")
        scraper = ChatGPTScraper(
            headless=False,  # Show browser for manual login
            timeout=30,
            use_undetected=True  # Use anti-detection
        )
        
        print(f"✅ Scraper initialized with undetected mode: {scraper.use_undetected}")
        
        # Step 2: Start scraping session
        with scraper:
            if not scraper.driver:
                print("❌ Failed to start browser driver")
                return False
            
            print("\n2️⃣ Navigating to ChatGPT...")
            
            # Navigate to ChatGPT (first, to set domain for cookies)
            if not scraper.navigate_to_chatgpt():
                print("❌ Failed to navigate to ChatGPT")
                return False
            
            # Try to load cookies if available
            if os.path.exists(cookies_path):
                scraper.load_cookies(cookies_path)
                print("🔄 Loaded cookies, refreshing page...")
                scraper.driver.refresh()
            
            # Step 3: Check login status
            print("\n3️⃣ Checking login status...")
            is_logged_in = scraper.is_logged_in()
            print(f"🔐 Login status: {is_logged_in}")
            
            if not is_logged_in:
                print("⚠️  Please log in manually in the browser window")
                print("⏳ Waiting 60 seconds for manual login...")
                import time
                time.sleep(60)
                
                # Save cookies after manual login
                scraper.save_cookies(cookies_path)
                print(f"💾 Cookies saved to {cookies_path} for future runs.")
                
                # Refresh and check again
                scraper.driver.refresh()
                is_logged_in = scraper.is_logged_in()
                print(f"🔐 Login status after wait: {is_logged_in}")
                if not is_logged_in:
                    print("❌ Still not logged in. Please log in and try again.")
                    return False
            
            print("✅ User is logged in!")
            
            # Step 4: Extract conversation list
            print("\n4️⃣ Extracting conversation list...")
            conversations = scraper.get_conversation_list()
            print(f"📋 Found {len(conversations)} conversations")
            
            if not conversations:
                print("❌ No conversations found")
                return False
            
            # Display conversations
            for i, conv in enumerate(conversations[:5]):  # Show first 5
                print(f"  {i+1}. {conv['title']} ({conv['url']})")
            
            # Step 5: Define analysis template
            print("\n5️⃣ Setting up analysis template...")
            analysis_template = """
            Please analyze this ChatGPT conversation and provide a comprehensive summary:
            
            **Conversation Details:**
            - Title: {{ conversation.title }}
            - URL: {{ conversation.url }}
            - Captured: {{ conversation.captured_at }}
            
            **Analysis Request:**
            Please provide:
            1. **Key Topics**: What are the main subjects discussed?
            2. **Key Insights**: What are the most important takeaways?
            3. **Technical Details**: Any technical concepts or solutions mentioned?
            4. **Action Items**: What actions or next steps were identified?
            5. **Summary**: A brief overall summary of the conversation
            
            Please format your response clearly with headers and bullet points.
            """
            
            print("✅ Analysis template ready")
            
            # Step 6: Process conversations with templated prompts
            print("\n6️⃣ Processing conversations with templated prompts...")
            results = []
            
            # Process first 3 conversations (to avoid overwhelming)
            for i, conversation in enumerate(conversations[:3]):
                print(f"\n📝 Processing conversation {i+1}/3: {conversation['title']}")
                
                try:
                    # Render the prompt template
                    prompt = render_template(analysis_template, {"conversation": conversation})
                    
                    # Enter the conversation
                    if not scraper.enter_conversation(conversation['url']):
                        print(f"⚠️  Could not enter conversation: {conversation['title']}")
                        continue
                    
                    print("✅ Entered conversation")
                    
                    # Send the templated prompt
                    if not scraper.send_prompt(prompt):
                        print(f"❌ Could not send prompt for: {conversation['title']}")
                        continue
                    
                    print("✅ Sent analysis prompt")
                    
                    # Get the response
                    content = scraper.get_conversation_content()
                    
                    if content.get("full_conversation"):
                        print(f"✅ Received response ({len(content['full_conversation'])} characters)")
                        
                        # Store result
                        result = {
                            "conversation": conversation,
                            "prompt": prompt,
                            "response": content.get("full_conversation", ""),
                            "timestamp": conversation.get("captured_at", ""),
                            "processed_at": conversation.get("captured_at", "")
                        }
                        results.append(result)
                    else:
                        print("⚠️  No response content received")
                    
                except Exception as e:
                    print(f"❌ Error processing conversation {conversation.get('title', 'Unknown')}: {e}")
                    continue
            
            # Step 7: Save results
            print(f"\n7️⃣ Saving results...")
            output_file = "chatgpt_analysis_results.json"
            
            try:
                scraper._save_conversations(results, output_file)
                print(f"✅ Saved {len(results)} analysis results to {output_file}")
                
                # Display summary
                print(f"\n📊 Workflow Summary:")
                print(f"   • Total conversations found: {len(conversations)}")
                print(f"   • Conversations processed: {len(results)}")
                print(f"   • Results saved to: {output_file}")
                
                # Show sample result
                if results:
                    print(f"\n📄 Sample Analysis Result:")
                    sample = results[0]
                    print(f"   • Conversation: {sample['conversation']['title']}")
                    print(f"   • Response length: {len(sample['response'])} characters")
                    print(f"   • Response preview: {sample['response'][:200]}...")
                
            except Exception as e:
                print(f"❌ Error saving results: {e}")
                return False
        
        print("\n🎉 Complete workflow finished successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False

def demo_workflow():
    """Run a demo workflow using demo data."""
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        from core.template_engine import render_template
        
        print("🎭 Running Demo Workflow (No Browser Required)")
        print("=" * 50)
        
        # Initialize scraper (will use demo mode)
        scraper = ChatGPTScraper()
        
        # Get demo conversations
        conversations = scraper._get_demo_conversations()
        print(f"📋 Demo conversations: {len(conversations)}")
        
        # Define analysis template
        analysis_template = """
        Please analyze this ChatGPT conversation and provide a comprehensive summary:
        
        **Conversation Details:**
        - Title: {{ conversation.title }}
        - URL: {{ conversation.url }}
        - Captured: {{ conversation.captured_at }}
        
        **Analysis Request:**
        Please provide:
        1. **Key Topics**: What are the main subjects discussed?
        2. **Key Insights**: What are the most important takeaways?
        3. **Technical Details**: Any technical concepts or solutions mentioned?
        4. **Action Items**: What actions or next steps were identified?
        5. **Summary**: A brief overall summary of the conversation
        """
        
        # Process conversations
        results = []
        for conversation in conversations:
            # Render the prompt template
            prompt = render_template(analysis_template, {"conversation": conversation})
            
            # Create demo response
            demo_response = f"""
            **Analysis for: {conversation['title']}**
            
            **Key Topics:**
            - Demo topic 1
            - Demo topic 2
            
            **Key Insights:**
            - Demo insight 1
            - Demo insight 2
            
            **Technical Details:**
            - Demo technical detail 1
            - Demo technical detail 2
            
            **Action Items:**
            - Demo action item 1
            - Demo action item 2
            
            **Summary:**
            This is a demo analysis of the conversation "{conversation['title']}".
            """
            
            result = {
                "conversation": conversation,
                "prompt": prompt,
                "response": demo_response,
                "timestamp": conversation.get("captured_at", ""),
                "processed_at": conversation.get("captured_at", "")
            }
            results.append(result)
        
        # Save results
        output_file = "demo_analysis_results.json"
        scraper._save_conversations(results, output_file)
        
        print(f"✅ Demo workflow completed!")
        print(f"📊 Processed {len(results)} conversations")
        print(f"💾 Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo workflow error: {e}")
        return False

if __name__ == "__main__":
    print("Digital Dreamscape - Complete Scraping Workflow")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            demo_workflow()
        elif command == "full":
            run_complete_workflow()
        elif command == "help":
            print("Available commands:")
            print("  python complete_scraping_workflow.py demo  - Run demo workflow (no browser)")
            print("  python complete_scraping_workflow.py full  - Run full workflow (requires login)")
            print("  python complete_scraping_workflow.py help  - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    else:
        # Default: run demo
        print("Running demo workflow (use 'full' for complete workflow)")
        demo_workflow() 