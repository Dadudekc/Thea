"""
Simplified ChatGPT Scraper for Digital Dreamscape Standalone
Handles automated ChatGPT conversation extraction without external dependencies.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modular components
from scrapers.browser_manager import BrowserManager
from scrapers.cookie_manager import CookieManager
from scrapers.login_handler import LoginHandler
from scrapers.conversation_extractor import ConversationExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPTScraper:
    """
    Simplified ChatGPT scraper for extracting conversation history.
    Uses modular components for browser management, login, and extraction.
    """
    
    def __init__(self, headless: bool = False, timeout: int = 30, use_undetected: bool = True, 
                 username: Optional[str] = None, password: Optional[str] = None,
                 cookie_file: Optional[str] = None, totp_secret: Optional[str] = None):
        """
        Initialize the ChatGPT scraper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Timeout for web operations
            use_undetected: Use undetected-chromedriver if available
            username: ChatGPT username/email
            password: ChatGPT password
            cookie_file: Path to cookie file for session persistence
            totp_secret: TOTP secret for 2FA
        """
        # Initialize modular components
        self.browser_manager = BrowserManager(headless=headless, use_undetected=use_undetected)
        self.cookie_manager = CookieManager(cookie_file=cookie_file)
        self.login_handler = LoginHandler(username=username, password=password, 
                                        totp_secret=totp_secret, timeout=timeout)
        self.conversation_extractor = ConversationExtractor(timeout=timeout)
        
        self.driver = None
        self.timeout = timeout
        
        # Expose init params for external checks/tests
        self.use_undetected = use_undetected
        self.headless = headless
        self.cookie_file = cookie_file or ""
        
        logger.info("✅ ChatGPT Scraper initialized with modular components")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()
    
    def start_driver(self) -> bool:
        """Start the web driver using the browser manager."""
        self.driver = self.browser_manager.create_driver()
        if self.driver:
            logger.info("✅ Driver started successfully")
            return True
        else:
            logger.error("❌ Failed to start driver")
            return False
    
    def close_driver(self):
        """Close the web driver using the browser manager."""
        self.browser_manager.close_driver()
        self.driver = None
        logger.info("✅ Driver closed")
    
    def navigate_to_chatgpt(self, model: str = "") -> bool:
        """
        Navigate to ChatGPT with optional model selection.
        
        Args:
            model: Specific model to navigate to (e.g., "gpt-4o", "gpt-4o-mini")
            
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.driver:
            logger.error("No driver available")
            return False
        
        try:
            base_url = "https://chat.openai.com/"
            if model:
                base_url += f"?model={model}"
            
            logger.info(f"Navigating to ChatGPT: {base_url}")
            self.driver.get(base_url)
            time.sleep(3)
            
            logger.info("✅ Successfully navigated to ChatGPT")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to ChatGPT: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged in using the login handler.
        
        Returns:
            True if logged in, False otherwise
        """
        return self.login_handler.is_logged_in(self.driver)
    
    def get_conversation_list(self) -> List[Dict[str, str]]:
        """
        Get list of available conversations using the conversation extractor.
        
        Returns:
            List of conversation dictionaries
        """
        return self.conversation_extractor.get_conversation_list(self.driver)
    
    def run_scraper(self, model: str = "", output_file: str = "chatgpt_chats.json") -> bool:
        """
        Run the complete scraping workflow.
        
        Args:
            model: Specific model to scrape
            output_file: Output file for conversations
            
        Returns:
            True if scraping successful, False otherwise
        """
        try:
            logger.info("🚀 Starting ChatGPT scraper workflow")
            
            # Navigate to ChatGPT
            if not self.navigate_to_chatgpt(model):
                return False
            
            # Load cookies if available
            if self.cookie_manager.cookie_file_exists():
                logger.info("Loading saved cookies...")
                self.cookie_manager.load_cookies(self.driver)
            
            # Ensure login
            if not self.login_handler.ensure_login_modern(self.driver):
                logger.error("❌ Login failed")
                return False
            
            # Save cookies after successful login
            self.cookie_manager.save_cookies(self.driver)
            
            # Get conversation list
            conversations = self.get_conversation_list()
            if not conversations:
                logger.warning("No conversations found")
                return False
            
            # Save conversations
            self._save_conversations(conversations, output_file)
            
            logger.info(f"✅ Scraping completed: {len(conversations)} conversations saved")
            return True
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            return False
    
    def _save_conversations(self, conversations: List[Dict[str, str]], output_file: str):
        """Save conversations to JSON file."""
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✅ Saved {len(conversations)} conversations to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save conversations: {e}")
    
    def enter_conversation(self, conversation_url: str) -> bool:
        """
        Enter a specific conversation using the conversation extractor.
        
        Args:
            conversation_url: URL of the conversation to enter
            
        Returns:
            True if successfully entered conversation, False otherwise
        """
        return self.conversation_extractor.enter_conversation(self.driver, conversation_url)
    
    def get_conversation_content(self) -> Dict[str, str]:
        """
        Get content from the current conversation using the conversation extractor.
        
        Returns:
            Dictionary containing conversation content
        """
        return self.conversation_extractor.get_conversation_content(self.driver)
    
    def send_prompt(self, prompt: str, wait_for_response: bool = True) -> bool:
        """
        Send a prompt to the current conversation using the conversation extractor.
        
        Args:
            prompt: Text prompt to send
            wait_for_response: Whether to wait for response
            
        Returns:
            True if prompt sent successfully, False otherwise
        """
        return self.conversation_extractor.send_prompt(self.driver, prompt, wait_for_response)
    
    def run_templated_prompts(self, conversations: List[Dict[str, str]], prompt_template: str) -> List[Dict[str, str]]:
        """
        Run templated prompts on a list of conversations.
        
        Args:
            conversations: List of conversation dictionaries
            prompt_template: Template prompt to use
            
        Returns:
            List of conversation results with prompts
        """
        results = []
        
        for conversation in conversations:
            try:
                logger.info(f"Processing conversation: {conversation.get('title', 'Unknown')}")
                
                # Enter conversation
                if not self.enter_conversation(conversation['url']):
                    logger.warning(f"Failed to enter conversation: {conversation.get('title', 'Unknown')}")
                    continue
                
                # Send templated prompt
                if self.send_prompt(prompt_template):
                    # Get updated content
                    content = self.get_conversation_content()
                    conversation['updated_content'] = content
                    results.append(conversation)
                    logger.info(f"✅ Processed conversation: {conversation.get('title', 'Unknown')}")
                else:
                    logger.warning(f"Failed to send prompt to: {conversation.get('title', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"Error processing conversation: {e}")
                continue
        
        return results

    def _get_demo_conversations(self, limit: int = 5) -> List[Dict[str, str]]:
        """Return a small set of demo conversations for offline/testing flows.

        Priority:
        1. Pull the most recent conversations from the Dreamscape memory DB (if available)
           so demos stay realistic.
        2. Fallback to a static synthetic list if the DB is empty or unavailable.
        """
        try:
            from core.memory_api import get_memory_api
            api = get_memory_api()
            recent = api.get_recent_conversations(limit)
            if recent:
                # Massage to expected shape for examples/tests
                return [
                    {
                        "id": conv["id"],
                        "title": conv.get("title", "Untitled"),
                        "url": conv.get("url", f"https://chat.openai.com/c/{conv['id']}"),
                        "timestamp": conv.get("timestamp", ""),
                        "captured_at": conv.get("timestamp", ""),
                    }
                    for conv in recent
                ]
        except Exception:
            # Memory not ready — fall through to static examples
            pass

        # Static fallback (ensures self-contained demo)
        now = datetime.utcnow().isoformat()
        return [
            {
                "id": f"demo_{i+1}",
                "title": f"Demo Conversation {i+1}",
                "url": f"https://chat.openai.com/c/demo_{i+1}",
                "timestamp": now,
                "captured_at": now,
            }
            for i in range(limit)
        ]

    def ensure_login(self) -> bool:
        """Ensure the user is logged in (backward-compat helper used by older examples)."""
        return self.login_handler.ensure_login_modern(self.driver) if self.driver else False

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ChatGPT Scraper")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--model", default="", help="Specific model to scrape")
    parser.add_argument("--output", default="chatgpt_chats.json", help="Output file")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout for operations")
    
    args = parser.parse_args()
    
    # Run scraper
    with ChatGPTScraper(headless=args.headless, timeout=args.timeout) as scraper:
        success = scraper.run_scraper(model=args.model, output_file=args.output)
        
        if success:
            print(f"✅ Scraping completed successfully. Results saved to {args.output}")
        else:
            print("❌ Scraping failed")
            exit(1)

if __name__ == "__main__":
    main() 