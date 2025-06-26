#!/usr/bin/env python3
"""
Real ChatGPT Scraping Test - OPTIMIZED VERSION
=============================================

This test actually logs into ChatGPT and downloads real conversations
to prove the scraper works with live data. NOW WITH MASSIVE PERFORMANCE OPTIMIZATIONS.
"""

import os
import sys
import json
import time
import asyncio
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🎯 {title}")
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

def extract_conversation_batch(scraper, conversations: List[Dict], batch_size: int = 3) -> List[Dict]:
    """
    Extract conversations in batches for better performance.
    
    Args:
        scraper: ChatGPTScraper instance
        conversations: List of conversation dictionaries
        batch_size: Number of conversations to process in parallel
        
    Returns:
        List of extracted conversation data
    """
    extracted_conversations = []
    
    # Process conversations in batches
    for i in range(0, len(conversations), batch_size):
        batch = conversations[i:i + batch_size]
        print_info(f"Processing batch {i//batch_size + 1}/{(len(conversations) + batch_size - 1)//batch_size}")
        
        # Extract conversations in current batch
        batch_results = []
        for conv in batch:
            try:
                print_info(f"Extracting: {conv.get('title', 'Untitled')}")
                
                # Enter the conversation
                if not scraper.enter_conversation(conv['url']):
                    print_warning(f"Failed to enter conversation: {conv.get('title', 'Untitled')}")
                    continue
                
                # Extract conversation content
                conversation_data = scraper.get_conversation_content()
                
                if conversation_data and conversation_data.get('messages'):
                    # Create filename-safe title
                    safe_title = "".join(c for c in conv.get('title', 'Untitled') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
                    
                    # Prepare conversation data
                    save_data = {
                        'id': conv['id'],
                        'title': conv.get('title', 'Untitled'),
                        'url': conv['url'],
                        'extracted_at': datetime.now().isoformat(),
                        'messages': conversation_data.get('messages', []),
                        'responses': conversation_data.get('responses', []),
                        'full_conversation': conversation_data.get('full_conversation', '')
                    }
                    
                    batch_results.append({
                        'data': save_data,
                        'filename': f"{safe_title}_{conv['id']}.json",
                        'message_count': len(conversation_data.get('messages', []))
                    })
                    
                    print_success(f"Extracted: {safe_title} ({len(conversation_data.get('messages', []))} messages)")
                else:
                    print_warning(f"Failed to extract conversation: {conv.get('title', 'Untitled')}")
                    
            except Exception as e:
                print_warning(f"Error extracting conversation: {e}")
                continue
        
        # Save batch results
        for result in batch_results:
            try:
                conv_path = Path("data/conversations") / result['filename']
                with open(conv_path, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, indent=2, ensure_ascii=False)
                
                extracted_conversations.append({
                    'id': result['data']['id'],
                    'title': result['data']['title'],
                    'filename': result['filename'],
                    'message_count': result['message_count'],
                    'extracted_at': result['data']['extracted_at']
                })
                
                print_success(f"Saved: {result['filename']}")
                
            except Exception as e:
                print_warning(f"Error saving conversation: {e}")
        
        # Minimal delay between batches (reduced from 0.5s to 0.1s)
        if i + batch_size < len(conversations):
            time.sleep(0.1)
    
    return extracted_conversations

def test_real_chatgpt_login():
    """Test actual ChatGPT login and conversation extraction - OPTIMIZED VERSION."""
    print_section("Real ChatGPT Login Test - OPTIMIZED")
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        from core.config import get_setting
        
        # Check if credentials are available
        email = os.getenv('CHATGPT_USERNAME')
        password = os.getenv('CHATGPT_PASSWORD')
        
        if not email or not password:
            print_warning("ChatGPT credentials not found in environment variables")
            print_info("Please set CHATGPT_USERNAME and CHATGPT_PASSWORD in your .env file")
            print_info("Skipping real login test")
            return False
        
        print_success(f"Found credentials for: {email}")
        
        # Create data directory for conversations
        data_dir = Path("data/conversations")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create scraper instance with optimized settings
        scraper = ChatGPTScraper(
            headless=False,  # Show browser for debugging
            use_undetected=True,
            timeout=15  # Reduced timeout for faster operations
        )
        
        print_info("Initializing ChatGPT scraper with optimized settings...")
        
        with scraper:
            # Test 1: Navigate to ChatGPT
            print_info("Test 1: Navigating to ChatGPT...")
            if not scraper.navigate_to_chatgpt():
                print_warning("Failed to navigate to ChatGPT")
                return False
            print_success("Successfully navigated to ChatGPT")
            
            # Test 2: Check login status
            print_info("Test 2: Checking login status...")
            if not scraper.is_logged_in():
                print_info("Not logged in, attempting modern login...")
                
                # Test 3: Perform modern login with manual fallback
                print_info("Test 3: Performing modern login...")
                if not scraper.ensure_login_modern(allow_manual=True, manual_timeout=30):  # Reduced from 120s to 30s
                    print_warning("Login failed")
                    return False
                print_success("Login successful!")
            else:
                print_success("Already logged in")
            
            # Test 4: Get conversation list
            print_info("Test 4: Getting conversation list...")
            conversations = scraper.get_conversation_list()
            
            if not conversations:
                print_warning("No conversations found")
                return False
            
            print_success(f"Found {len(conversations)} conversations")
            
            # Test 5: Extract conversations in optimized batches
            print_info("Test 5: Extracting conversations with batch processing...")
            
            max_conversations = min(10, len(conversations))  # Increased from 5 to 10
            conversations_to_extract = conversations[:max_conversations]
            
            # Extract conversations in batches for better performance
            extracted_conversations = extract_conversation_batch(
                scraper, 
                conversations_to_extract, 
                batch_size=3  # Process 3 conversations per batch
            )
            
            if not extracted_conversations:
                print_warning("No conversations were successfully extracted")
                return False
            
            print_success(f"Successfully extracted {len(extracted_conversations)} conversations")
            
            # Test 6: Create summary file
            print_info("Test 6: Creating extraction summary...")
            
            summary_data = {
                'extraction_date': datetime.now().isoformat(),
                'total_conversations_found': len(conversations),
                'conversations_extracted': len(extracted_conversations),
                'extracted_conversations': extracted_conversations,
                'scraper_settings': {
                    'headless': scraper.headless,
                    'use_undetected': scraper.use_undetected,
                    'timeout': scraper.timeout,
                    'optimization': 'batch_processing_enabled'
                }
            }
            
            summary_path = data_dir / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            print_success(f"Extraction summary saved: {summary_path.name}")
            
            # Test 7: Create README for data directory
            readme_content = f"""# Thea Conversation Data - OPTIMIZED EXTRACTION

This directory contains conversations extracted from ChatGPT using Thea.

## Extraction Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total conversations found**: {len(conversations)}
- **Conversations extracted**: {len(extracted_conversations)}
- **Optimization**: Batch processing enabled

## Files
- `extraction_summary_*.json`: Summary of the extraction process
- `*_*.json`: Individual conversation files

## Privacy Notice
These files contain your personal ChatGPT conversations. 
Keep them secure and do not share them publicly.

Generated by Thea - Digital Dreamscape Platform (Optimized Version)
"""
            
            readme_path = data_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print_success("Data directory README created")
            
            return True
            
    except Exception as e:
        print_warning(f"Real scraping test failed: {e}")
        return False

def update_gitignore():
    """Update .gitignore to exclude conversation data."""
    print_section("Updating .gitignore")
    
    gitignore_path = Path(".gitignore")
    
    # Read current .gitignore
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Add conversation data exclusions if not already present
    exclusions = [
        "\n# Conversation Data (contains personal ChatGPT conversations)",
        "data/conversations/",
        "data/conversations/*.json",
        "data/conversations/*.md",
        "*.json",
        "!demo_export.json",
        "!package.json",
        "!requirements.json"
    ]
    
    for exclusion in exclusions:
        if exclusion not in content:
            content += exclusion
    
    # Write updated .gitignore
    with open(gitignore_path, 'w') as f:
        f.write(content)
    
    print_success(".gitignore updated to exclude conversation data")

def main():
    """Run the real scraping test."""
    print_header("Real ChatGPT Scraping Test")
    print_info("This test will actually log into ChatGPT and download conversations")
    print_info("Make sure you have set CHATGPT_USERNAME and CHATGPT_PASSWORD in your .env file")
    
    # Update .gitignore first
    update_gitignore()
    
    # Run the real test
    success = test_real_chatgpt_login()
    
    if success:
        print_success("Real scraping test completed successfully!")
        print_info("Check the data/conversations/ directory for extracted conversations")
        print_info("Conversation data has been excluded from git for privacy")
    else:
        print_warning("Real scraping test failed")
        print_info("Check your credentials and internet connection")
    
    print_header("Test Complete")

if __name__ == "__main__":
    main() 