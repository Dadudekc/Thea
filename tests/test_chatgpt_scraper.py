#!/usr/bin/env python3
"""
Comprehensive tests for ChatGPT Scraper functionality.
Tests actual scraping capabilities, not just imports.
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from scrapers.chatgpt_scraper import ChatGPTScraper

class TestChatGPTScraper:
    """Test suite for ChatGPT Scraper functionality."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization with different modes."""
        # Test undetected mode
        scraper_undetected = ChatGPTScraper(use_undetected=True)
        assert hasattr(scraper_undetected, 'use_undetected')
        
        # Test regular mode
        scraper_regular = ChatGPTScraper(use_undetected=False)
        assert hasattr(scraper_regular, 'use_undetected')
    
    def test_demo_conversations(self):
        """Test demo conversation generation when Selenium is unavailable."""
        scraper = ChatGPTScraper()
        conversations = scraper._get_demo_conversations()
        
        assert isinstance(conversations, list)
        assert len(conversations) > 0
        
        for conv in conversations:
            assert 'title' in conv
            assert 'url' in conv
            assert 'timestamp' in conv
            assert 'captured_at' in conv
    
    def test_conversation_saving(self):
        """Test saving conversations to file."""
        scraper = ChatGPTScraper()
        conversations = scraper._get_demo_conversations()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            scraper._save_conversations(conversations, temp_file)
            
            # Verify file was created and contains data
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert isinstance(saved_data, list)
            assert len(saved_data) == len(conversations)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @pytest.mark.integration
    def test_full_scraping_workflow(self):
        """Test the complete scraping workflow (requires manual login)."""
        # This test requires manual intervention for login
        scraper = ChatGPTScraper(headless=False, use_undetected=True)
        
        try:
            with scraper:
                # Test navigation
                assert scraper.navigate_to_chatgpt()
                
                # Test login detection
                is_logged_in = scraper.is_logged_in()
                print(f"Login status: {is_logged_in}")
                
                if is_logged_in:
                    # Test conversation extraction
                    conversations = scraper.get_conversation_list()
                    print(f"Found {len(conversations)} conversations")
                    
                    # Verify conversation structure
                    for conv in conversations:
                        assert 'title' in conv
                        assert 'url' in conv
                        assert 'timestamp' in conv
                        assert 'captured_at' in conv
                    
                    # Test saving to file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        temp_file = f.name
                    
                    try:
                        scraper._save_conversations(conversations, temp_file)
                        assert os.path.exists(temp_file)
                        
                        # Verify saved data
                        with open(temp_file, 'r', encoding='utf-8') as f:
                            saved_data = json.load(f)
                        assert len(saved_data) == len(conversations)
                        
                    finally:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                else:
                    print("⚠️  User not logged in - skipping conversation extraction")
                    
        except Exception as e:
            print(f"❌ Scraping workflow failed: {e}")
            raise
    
    def test_template_prompt_integration(self):
        """Test integration with template engine for prompts."""
        from core.template_engine import render_template
        
        # Test template rendering for prompts
        prompt_template = """
        Please analyze the following conversation:
        Title: {{ conversation.title }}
        URL: {{ conversation.url }}
        
        Provide a summary of the key points discussed.
        """
        
        conversation = {
            "title": "Test Conversation",
            "url": "https://chat.openai.com/c/test123",
            "timestamp": "2025-01-20T10:00:00",
            "captured_at": "2025-01-20T10:00:00"
        }
        
        rendered_prompt = render_template(prompt_template, {"conversation": conversation})
        
        assert "Test Conversation" in rendered_prompt
        assert "https://chat.openai.com/c/test123" in rendered_prompt
        assert "Please analyze" in rendered_prompt
    
    def test_error_handling(self):
        """Test error handling in scraper."""
        scraper = ChatGPTScraper()
        
        # Test with no driver
        assert not scraper.navigate_to_chatgpt()
        assert not scraper.is_logged_in()
        assert scraper.get_conversation_list() == []
    
    @patch('scrapers.chatgpt_scraper.SELENIUM_AVAILABLE', False)
    def test_demo_mode_workflow(self):
        """Test scraper workflow when Selenium is not available."""
        scraper = ChatGPTScraper()
        
        # Test that demo mode works
        conversations = scraper.get_conversation_list()
        assert isinstance(conversations, list)
        assert len(conversations) > 0
        
        # Test full workflow in demo mode
        success = scraper.run_scraper(output_file="test_demo_output.json")
        assert success
        
        # Clean up
        if os.path.exists("test_demo_output.json"):
            os.unlink("test_demo_output.json")

def test_undetected_chromedriver_compatibility():
    """Test undetected-chromedriver compatibility."""
    try:
        import undetected_chromedriver as uc
        print("✅ Undetected-chromedriver available")
        
        # Test that we can create options
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        
        print("✅ Undetected-chromedriver options created successfully")
        
    except ImportError:
        print("⚠️  Undetected-chromedriver not available")
        pytest.skip("Undetected-chromedriver not available")

if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running ChatGPT Scraper tests...")
    
    # Test initialization
    scraper = ChatGPTScraper()
    print("✅ Scraper initialization: PASSED")
    
    # Test demo conversations
    conversations = scraper._get_demo_conversations()
    print(f"✅ Demo conversations: {len(conversations)} conversations")
    
    # Test template integration
    from core.template_engine import render_template
    prompt_template = "Analyze: {{ conversation.title }}"
    rendered = render_template(prompt_template, {"conversation": conversations[0]})
    print(f"✅ Template integration: {rendered}")
    
    print("✅ All basic tests passed!")
    
    # Note: Full integration tests require manual login
    print("\n💡 For full integration tests, run:")
    print("pytest tests/test_chatgpt_scraper.py::TestChatGPTScraper::test_full_scraping_workflow -v") 