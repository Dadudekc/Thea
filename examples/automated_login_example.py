#!/usr/bin/env python3
"""
Example: Automated ChatGPT Login with Environment Variables and Cookie Management
Demonstrates credentials loading, cookie persistence and basic conversation scrape.
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def example_automated_login():
    """Automated login using environment variables from .env file."""
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import logging

        logging.basicConfig(level=logging.INFO)

        env_file = Path(".env")
        if not env_file.exists():
            print("⚠️  No .env file – falling back to manual creds if set")

        username = os.getenv("CHATGPT_USERNAME")
        password = os.getenv("CHATGPT_PASSWORD")

        scraper = ChatGPTScraper(
            headless=False,
            timeout=30,
            use_undetected=True,
            cookie_file="my_chatgpt_cookies.pkl",
        )

        with scraper:
            scraper.navigate_to_chatgpt()
            if scraper.ensure_login():
                conversations = scraper.get_conversation_list()
                for i, conv in enumerate(conversations[:5]):
                    print(f"{i+1}. {conv.get('title', 'Untitled')}")
            else:
                print("Login failed")
    except Exception as e:
        print("Error in example_automated_login:", e)


def example_cookie_persistence():
    """Validate cookie reuse across sessions."""
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        import logging

        logging.basicConfig(level=logging.INFO)
        cookie_file = "test_persistence_cookies.pkl"

        # First session – login
        with ChatGPTScraper(headless=False, use_undetected=True, cookie_file=cookie_file) as s1:
            s1.navigate_to_chatgpt()
            s1.ensure_login()

        # Second session – reuse cookies
        with ChatGPTScraper(headless=False, use_undetected=True, cookie_file=cookie_file) as s2:
            s2.navigate_to_chatgpt()
            if s2.is_logged_in():
                print("✅ Cookie persistence works!")
            else:
                print("❌ Cookie persistence failed")
    except Exception as e:
        print("Error in example_cookie_persistence:", e)


def example_environment_setup():
    """Prints guidance for setting up .env credentials."""
    print("Create .env with CHATGPT_USERNAME / PASSWORD then run this demo again.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "login"
    if cmd == "login":
        example_automated_login()
    elif cmd == "cookies":
        example_cookie_persistence()
    else:
        example_environment_setup() 