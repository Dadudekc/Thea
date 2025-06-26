#!/usr/bin/env python3
"""
Test suite for Dream.OS Memory Manager
=====================================

Tests the core memory management functionality including:
- Database initialization and schema
- Conversation ingestion
- Search and retrieval
- Context window generation
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.memory_manager import MemoryManager


class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def sample_conversations(self):
        """Sample conversation data for testing."""
        return [
            {
                "id": "test_conv_1",
                "title": "Python Web Scraping Tutorial",
                "timestamp": "2024-01-15T10:30:00",
                "captured_at": "2024-01-15T10:35:00",
                "model": "gpt-4o",
                "tags": "python,web-scraping,tutorial",
                "summary": "A comprehensive guide to web scraping with Python",
                "content": "This conversation covers web scraping techniques using BeautifulSoup and requests libraries.",
                "url": "https://chat.openai.com/c/test_conv_1",
                "messages": [
                    {"role": "user", "content": "How do I scrape a website with Python?"},
                    {"role": "assistant", "content": "You can use BeautifulSoup and requests libraries for web scraping."}
                ]
            },
            {
                "id": "test_conv_2", 
                "title": "Machine Learning Basics",
                "timestamp": "2024-01-16T14:20:00",
                "captured_at": "2024-01-16T14:25:00",
                "model": "gpt-4o",
                "tags": "machine-learning,ai,basics",
                "summary": "Introduction to machine learning concepts and algorithms",
                "content": "This conversation explains fundamental machine learning concepts including supervised and unsupervised learning.",
                "url": "https://chat.openai.com/c/test_conv_2",
                "messages": [
                    {"role": "user", "content": "What is machine learning?"},
                    {"role": "assistant", "content": "Machine learning is a subset of AI that enables computers to learn from data."}
                ]
            },
            {
                "id": "test_conv_3",
                "title": "Data Analysis with Pandas",
                "timestamp": "2024-01-17T09:15:00", 
                "captured_at": "2024-01-17T09:20:00",
                "model": "gpt-4o",
                "tags": "data-analysis,pandas,python",
                "summary": "Data manipulation and analysis using pandas library",
                "content": "This conversation demonstrates pandas operations for data cleaning, filtering, and analysis.",
                "url": "https://chat.openai.com/c/test_conv_3",
                "messages": [
                    {"role": "user", "content": "How do I analyze data with pandas?"},
                    {"role": "assistant", "content": "Pandas provides powerful tools for data manipulation and analysis."}
                ]
            }
        ]
    
    @pytest.fixture
    def temp_conversations_dir(self, sample_conversations):
        """Create temporary directory with sample conversation files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversations_dir = Path(temp_dir) / "conversations"
            conversations_dir.mkdir()
            
            # Create sample conversation files
            for i, conv in enumerate(sample_conversations):
                filename = f"conversation_{i+1}_{conv['id']}.json"
                filepath = conversations_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(conv, f, indent=2)
            
            yield str(conversations_dir)
    
    def test_memory_manager_initialization(self, temp_db):
        """Test MemoryManager initialization and database creation."""
        memory = MemoryManager(temp_db)
        
        assert memory.db_path == temp_db
        assert memory.conn is not None
        
        # Check if tables were created
        cursor = memory.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'conversations' in tables
        assert 'memory_index' in tables
        
        memory.close()
    
    def test_schema_creation(self, temp_db):
        """Test database schema creation."""
        memory = MemoryManager(temp_db)
        
        cursor = memory.conn.cursor()
        
        # Check conversations table structure
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'TEXT',
            'title': 'TEXT', 
            'timestamp': 'TEXT',
            'captured_at': 'TEXT',
            'model': 'TEXT',
            'tags': 'TEXT',
            'summary': 'TEXT',
            'content': 'TEXT',
            'url': 'TEXT',
            'message_count': 'INTEGER',
            'word_count': 'INTEGER',
            'created_at': 'TEXT',
            'updated_at': 'TEXT'
        }
        
        for col, col_type in expected_columns.items():
            assert col in columns
            assert columns[col] == col_type
        
        # Check memory_index table structure
        cursor.execute("PRAGMA table_info(memory_index)")
        index_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_index_columns = {
            'id': 'INTEGER',
            'conversation_id': 'TEXT',
            'content_hash': 'TEXT',
            'content_type': 'TEXT',
            'content_text': 'TEXT',
            'created_at': 'TEXT'
        }
        
        for col, col_type in expected_index_columns.items():
            assert col in index_columns
            assert index_columns[col] == col_type
        
        memory.close()
    
    def test_conversation_ingestion(self, temp_db, temp_conversations_dir):
        """Test conversation ingestion from JSON files."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations
        count = memory.ingest_conversations(temp_conversations_dir)
        assert count == 3
        
        # Verify conversations were stored
        cursor = memory.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stored_count = cursor.fetchone()[0]
        assert stored_count == 3
        
        # Check specific conversation data
        cursor.execute("SELECT title, model, message_count FROM conversations WHERE id = 'test_conv_1'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "Python Web Scraping Tutorial"
        assert row[1] == "gpt-4o"
        assert row[2] == 2
        
        memory.close()
    
    def test_content_extraction(self, temp_db):
        """Test conversation content extraction."""
        memory = MemoryManager(temp_db)
        
        # Test with different content structures
        test_data = {
            "id": "test_extract",
            "title": "Test Extraction",
            "full_conversation": "This is the full conversation content.",
            "messages": [
                {"role": "user", "content": "User message 1"},
                {"role": "assistant", "content": "Assistant response 1"}
            ],
            "responses": [
                {"role": "assistant", "content": "Additional response"}
            ]
        }
        
        content = memory._extract_content(test_data)
        expected = "This is the full conversation content.\n\nUser message 1\n\nAssistant response 1\n\nAdditional response"
        assert content == expected
        
        memory.close()
    
    def test_content_chunking(self, temp_db):
        """Test content chunking for search indexing."""
        memory = MemoryManager(temp_db)
        
        # Test with short content
        short_content = "Short content"
        chunks = memory._chunk_content(short_content, chunk_size=5)
        assert len(chunks) == 1
        assert chunks[0] == "Short content"
        
        # Test with longer content
        long_content = "This is a longer piece of content that should be split into multiple chunks for better search indexing"
        chunks = memory._chunk_content(long_content, chunk_size=5)
        assert len(chunks) > 1
        
        # Verify all words are included
        original_words = long_content.split()
        chunked_words = []
        for chunk in chunks:
            chunked_words.extend(chunk.split())
        assert chunked_words == original_words
        
        memory.close()
    
    def test_context_window_search(self, temp_db, temp_conversations_dir):
        """Test context window search functionality."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations first
        memory.ingest_conversations(temp_conversations_dir)
        
        # Test search by title
        results = memory.get_context_window("Python", limit=2)
        assert len(results) > 0
        assert any("Python" in conv['title'] for conv in results)
        
        # Test search by content
        results = memory.get_context_window("web scraping", limit=2)
        assert len(results) > 0
        
        # Test search by tags
        results = memory.get_context_window("machine-learning", limit=2)
        assert len(results) > 0
        assert any("machine-learning" in conv['tags'] for conv in results)
        
        # Test search with no results
        results = memory.get_context_window("nonexistent term", limit=2)
        assert len(results) == 0
        
        memory.close()
    
    def test_conversation_by_id(self, temp_db, temp_conversations_dir):
        """Test getting conversation by ID."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations first
        memory.ingest_conversations(temp_conversations_dir)
        
        # Test existing conversation
        conv = memory.get_conversation_by_id("test_conv_1")
        assert conv is not None
        assert conv['title'] == "Python Web Scraping Tutorial"
        assert conv['id'] == "test_conv_1"
        
        # Test non-existing conversation
        conv = memory.get_conversation_by_id("nonexistent_id")
        assert conv is None
        
        memory.close()
    
    def test_recent_conversations(self, temp_db, temp_conversations_dir):
        """Test getting recent conversations."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations first
        memory.ingest_conversations(temp_conversations_dir)
        
        # Test getting recent conversations
        recent = memory.get_recent_conversations(limit=2)
        assert len(recent) == 2
        
        # Verify they're ordered by timestamp (most recent first)
        timestamps = [conv['timestamp'] for conv in recent]
        assert timestamps == sorted(timestamps, reverse=True)
        
        memory.close()
    
    def test_conversation_stats(self, temp_db, temp_conversations_dir):
        """Test conversation statistics."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations first
        memory.ingest_conversations(temp_conversations_dir)
        
        # Get statistics
        stats = memory.get_conversation_stats()
        
        assert stats['total_conversations'] == 3
        assert stats['total_messages'] == 6  # 2 messages per conversation
        assert stats['total_words'] > 0
        assert 'gpt-4o' in stats['models']
        assert stats['models']['gpt-4o'] == 3
        assert stats['date_range']['earliest'] is not None
        assert stats['date_range']['latest'] is not None
        
        memory.close()
    
    def test_memory_indexing(self, temp_db, temp_conversations_dir):
        """Test memory indexing functionality."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations first
        memory.ingest_conversations(temp_conversations_dir)
        
        # Check if content was indexed
        cursor = memory.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_index")
        index_count = cursor.fetchone()[0]
        assert index_count > 0
        
        # Check different content types were indexed
        cursor.execute("SELECT DISTINCT content_type FROM memory_index")
        content_types = [row[0] for row in cursor.fetchall()]
        assert 'title' in content_types
        assert 'content' in content_types
        
        memory.close()
    
    def test_context_manager(self, temp_db):
        """Test MemoryManager as context manager."""
        with MemoryManager(temp_db) as memory:
            assert memory.conn is not None
            cursor = memory.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            # Should not raise an exception
        
        # Connection should be closed after context exit
        assert memory.conn is None
    
    def test_error_handling(self, temp_db):
        """Test error handling in MemoryManager."""
        memory = MemoryManager(temp_db)
        
        # Test with invalid conversation ID
        result = memory.get_conversation_by_id("invalid_id")
        assert result is None
        
        # Test with invalid search query
        results = memory.get_context_window("", limit=0)
        assert results == []
        
        # Test with non-existent directory
        count = memory.ingest_conversations("nonexistent_directory")
        assert count == 0
        
        memory.close()
    
    def test_duplicate_ingestion(self, temp_db, temp_conversations_dir):
        """Test handling of duplicate conversation ingestion."""
        memory = MemoryManager(temp_db)
        
        # Ingest conversations twice
        count1 = memory.ingest_conversations(temp_conversations_dir)
        count2 = memory.ingest_conversations(temp_conversations_dir)
        
        assert count1 == 3
        assert count2 == 3  # Should handle duplicates gracefully
        
        # Verify only unique conversations exist
        cursor = memory.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_count = cursor.fetchone()[0]
        assert total_count == 3
        
        memory.close()


def test_memory_manager_cli():
    """Test MemoryManager CLI functionality."""
    with patch('sys.argv', ['test_memory_manager.py', '--help']):
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            mock_args = MagicMock()
            mock_args.ingest = False
            mock_args.stats = False
            mock_args.search = None
            mock_args.db = "test.db"
            mock_parse.return_value = mock_args
            
            # Should not raise an exception
            from core.memory_manager import main
            main()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 