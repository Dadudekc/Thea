#!/usr/bin/env python3
"""
Scraper CLI Demo
================

Demonstrates how to use the ScraperOrchestrator from the command line.
Stays within 300-350 LOC requirement.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scraper_orchestrator import ScraperOrchestrator, ConversationData, ScrapingResult

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def login_command(orchestrator: ScraperOrchestrator, username: Optional[str], password: Optional[str]) -> bool:
    """Handle login command."""
    print("🔐 Attempting to login to ChatGPT...")
    
    result = orchestrator.login_and_save_cookies(username, password)
    
    if result.success:
        method = result.metadata.get('method', 'unknown')
        print(f"✅ Login successful via {method}")
        return True
    else:
        if result.metadata and result.metadata.get("requires_manual_login"):
            print("⚠️  Manual login required")
            print("Please complete the login process in the browser window that opened.")
            print("Press Enter when you've completed the login...")
            input()
            return True
        else:
            print(f"❌ Login failed: {result.error}")
            return False

def extract_conversations_command(orchestrator: ScraperOrchestrator, max_conversations: int) -> Optional[list]:
    """Handle extract conversations command."""
    print(f"📋 Extracting up to {max_conversations} conversations...")
    
    result = orchestrator.extract_conversations(max_conversations)
    
    if result.success:
        conversations = result.data
        print(f"✅ Extracted {len(conversations)} conversations")
        
        # Display conversation list
        print("\n📝 Conversation List:")
        print("-" * 80)
        for i, conv in enumerate(conversations, 1):
            print(f"{i:2d}. {conv.title}")
            print(f"    Messages: {conv.message_count} | URL: {conv.url}")
            print()
        
        return conversations
    else:
        print(f"❌ Failed to extract conversations: {result.error}")
        return None

def extract_content_command(orchestrator: ScraperOrchestrator, conversations: list) -> bool:
    """Handle extract content command."""
    if not conversations:
        print("❌ No conversations to extract content from")
        return False
    
    print(f"📄 Extracting content from {len(conversations)} conversations...")
    
    urls = [conv.url for conv in conversations]
    result = orchestrator.extract_multiple_conversations(urls)
    
    if result.success:
        successful = result.metadata['successful']
        failed = result.metadata['failed']
        print(f"✅ Extracted content from {successful} conversations")
        if failed > 0:
            print(f"⚠️  Failed to extract from {failed} conversations")
        return True
    else:
        print(f"❌ Failed to extract content: {result.error}")
        return False

def generate_blog_command(orchestrator: ScraperOrchestrator, conversations: list) -> bool:
    """Handle generate blog command."""
    if not conversations:
        print("❌ No conversations to generate blog from")
        return False
    
    print("📝 Generating blog post from conversations...")
    
    result = orchestrator.generate_blog_post(conversations)
    
    if result.success:
        processed = result.metadata['conversations_processed']
        print(f"✅ Generated blog post from {processed} conversations")
        
        # Save blog content to file
        output_file = "outputs/generated_blog.md"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.data)
        
        print(f"💾 Blog post saved to: {output_file}")
        return True
    else:
        print(f"❌ Failed to generate blog: {result.error}")
        return False

def generate_devlog_command(orchestrator: ScraperOrchestrator, conversations: list) -> bool:
    """Handle generate devlog command."""
    if not conversations:
        print("❌ No conversations to generate devlog from")
        return False
    
    print("📋 Generating devlog from conversations...")
    
    result = orchestrator.generate_devlog(conversations)
    
    if result.success:
        processed = result.metadata['conversations_processed']
        print(f"✅ Generated devlog from {processed} conversations")
        
        # Save devlog content to file
        output_file = "outputs/generated_devlog.md"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.data)
        
        print(f"💾 Devlog saved to: {output_file}")
        return True
    else:
        print(f"❌ Failed to generate devlog: {result.error}")
        return False

def generate_social_command(orchestrator: ScraperOrchestrator, conversations: list) -> bool:
    """Handle generate social content command."""
    if not conversations:
        print("❌ No conversations to generate social content from")
        return False
    
    print("📱 Generating social media content from conversations...")
    
    result = orchestrator.generate_social_content(conversations)
    
    if result.success:
        processed = result.metadata['conversations_processed']
        print(f"✅ Generated social content from {processed} conversations")
        
        # Save social content to file
        output_file = "outputs/generated_social.md"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.data)
        
        print(f"💾 Social content saved to: {output_file}")
        return True
    else:
        print(f"❌ Failed to generate social content: {result.error}")
        return False

def status_command(orchestrator: ScraperOrchestrator):
    """Handle status command."""
    print("📊 Scraper Status:")
    print("-" * 40)
    
    status = orchestrator.get_status()
    
    for key, value in status.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print()

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="ChatGPT Scraper CLI Demo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to ChatGPT")
    login_parser.add_argument("--username", "-u", help="ChatGPT username/email")
    login_parser.add_argument("--password", "-p", help="ChatGPT password")
    
    # Extract conversations command
    extract_conv_parser = subparsers.add_parser("extract-conversations", help="Extract conversation list")
    extract_conv_parser.add_argument("--max", "-m", type=int, default=50, help="Maximum conversations to extract")
    
    # Extract content command
    subparsers.add_parser("extract-content", help="Extract content from conversations")
    
    # Generate commands
    subparsers.add_parser("generate-blog", help="Generate blog post from conversations")
    subparsers.add_parser("generate-devlog", help="Generate devlog from conversations")
    subparsers.add_parser("generate-social", help="Generate social content from conversations")
    
    # Status command
    subparsers.add_parser("status", help="Show scraper status")
    
    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run complete workflow")
    workflow_parser.add_argument("--username", "-u", help="ChatGPT username/email")
    workflow_parser.add_argument("--password", "-p", help="ChatGPT password")
    workflow_parser.add_argument("--max", "-m", type=int, default=10, help="Maximum conversations to process")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Initialize orchestrator
    try:
        orchestrator = ScraperOrchestrator(headless=args.headless, use_undetected=True)
        print("🚀 ScraperOrchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ScraperOrchestrator: {e}")
        return
    
    conversations = []
    
    try:
        if args.command == "login":
            success = login_command(orchestrator, args.username, args.password)
            if not success:
                return
        
        elif args.command == "extract-conversations":
            if not orchestrator.is_initialized:
                print("❌ Please login first")
                return
            conversations = extract_conversations_command(orchestrator, args.max)
        
        elif args.command == "extract-content":
            if not orchestrator.is_initialized:
                print("❌ Please login first")
                return
            # For demo, we'll need to extract conversations first
            print("⚠️  No conversations loaded. Please run extract-conversations first.")
            return
        
        elif args.command == "generate-blog":
            if not orchestrator.is_initialized:
                print("❌ Please login first")
                return
            generate_blog_command(orchestrator, conversations)
        
        elif args.command == "generate-devlog":
            if not orchestrator.is_initialized:
                print("❌ Please login first")
                return
            generate_devlog_command(orchestrator, conversations)
        
        elif args.command == "generate-social":
            if not orchestrator.is_initialized:
                print("❌ Please login first")
                return
            generate_social_command(orchestrator, conversations)
        
        elif args.command == "status":
            status_command(orchestrator)
        
        elif args.command == "workflow":
            print("🔄 Running complete workflow...")
            
            # Login
            if not login_command(orchestrator, args.username, args.password):
                return
            
            # Extract conversations
            conversations = extract_conversations_command(orchestrator, args.max)
            if not conversations:
                return
            
            # Extract content
            if not extract_content_command(orchestrator, conversations):
                return
            
            # Generate content
            generate_blog_command(orchestrator, conversations)
            generate_devlog_command(orchestrator, conversations)
            generate_social_command(orchestrator, conversations)
            
            print("✅ Workflow completed successfully!")
    
    finally:
        # Clean up
        orchestrator.close()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    main() 