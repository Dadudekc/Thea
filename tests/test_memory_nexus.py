"""
Digital Dreamscape - Memory Nexus Test Suite
Validation rituals for the Memory Core and its artifacts
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory_manager import MemoryNexus
from core.models import Conversation, Message, Tag, Template, Setting


class TestMemoryNexus(unittest.TestCase):
    """Test suite for Memory Nexus functionality"""
    
    def setUp(self):
        """Set up test database"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize Memory Nexus
        self.memory_nexus = MemoryNexus(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        # Attempt to close any open connections (if implemented)
        if hasattr(self.memory_nexus, 'SessionLocal'):
            try:
                self.memory_nexus.SessionLocal().close()
            except Exception:
                pass
        # Remove temporary database (with retry for Windows file locking)
        import time
        for _ in range(5):
            try:
                if os.path.exists(self.db_path):
                    os.unlink(self.db_path)
                break
            except PermissionError:
                time.sleep(0.2)
    
    def test_database_initialization(self):
        """Test that database is properly initialized with default data"""
        # Check that default templates were created
        templates = self.memory_nexus.get_templates()
        self.assertGreater(len(templates), 0)
        
        # Check that default settings were created
        db_version = self.memory_nexus.get_setting('database_version')
        self.assertEqual(db_version, '1.0')
        
        # Check that we can get statistics
        stats = self.memory_nexus.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_conversations', stats)
    
    def test_conversation_creation(self):
        """Test creating and retrieving conversations"""
        # Create test conversation data
        conversation_data = {
            'title': 'Test Conversation',
            'url': 'https://chat.openai.com/c/test123',
            'source': 'chatgpt',
            'status': 'active',
            'metadata': {'test_key': 'test_value'},
            'messages': [
                {
                    'role': 'user',
                    'content': 'Hello, this is a test message.',
                    'timestamp': datetime.now()
                },
                {
                    'role': 'assistant',
                    'content': 'Hello! I understand this is a test message.',
                    'timestamp': datetime.now()
                }
            ]
        }
        
        # Save conversation
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        self.assertIsInstance(conversation_id, int)
        self.assertGreater(conversation_id, 0)
        
        # Retrieve conversation
        retrieved = self.memory_nexus.get_conversation(conversation_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], 'Test Conversation')
        self.assertEqual(retrieved['url'], 'https://chat.openai.com/c/test123')
        self.assertEqual(len(retrieved['messages']), 2)
        
        # Check message content
        self.assertEqual(retrieved['messages'][0]['role'], 'user')
        self.assertEqual(retrieved['messages'][0]['content'], 'Hello, this is a test message.')
        self.assertEqual(retrieved['messages'][1]['role'], 'assistant')
    
    def test_conversation_update(self):
        """Test updating existing conversations"""
        # Create initial conversation
        conversation_data = {
            'title': 'Original Title',
            'url': 'https://chat.openai.com/c/update123',
            'messages': [{'role': 'user', 'content': 'Original message'}]
        }
        
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        
        # Update conversation
        updated_data = {
            'title': 'Updated Title',
            'url': 'https://chat.openai.com/c/update123',  # Same URL
            'messages': [
                {'role': 'user', 'content': 'Updated message 1'},
                {'role': 'assistant', 'content': 'Updated response 1'}
            ]
        }
        
        updated_id = self.memory_nexus.save_conversation(updated_data)
        self.assertEqual(updated_id, conversation_id)  # Should be same ID
        
        # Verify update
        retrieved = self.memory_nexus.get_conversation(conversation_id)
        self.assertEqual(retrieved['title'], 'Updated Title')
        self.assertEqual(len(retrieved['messages']), 2)
    
    def test_conversation_listing(self):
        """Test listing conversations with filtering"""
        # Create multiple conversations
        for i in range(5):
            conversation_data = {
                'title': f'Test Conversation {i}',
                'url': f'https://chat.openai.com/c/test{i}',
                'source': 'chatgpt',
                'messages': [{'role': 'user', 'content': f'Message {i}'}]
            }
            self.memory_nexus.save_conversation(conversation_data)
        
        # Test basic listing
        conversations = self.memory_nexus.get_conversations(limit=10)
        self.assertEqual(len(conversations), 5)
        
        # Test with limit
        limited = self.memory_nexus.get_conversations(limit=3)
        self.assertEqual(len(limited), 3)
        
        # Test filtering by source
        chatgpt_conversations = self.memory_nexus.get_conversations(source='chatgpt')
        self.assertEqual(len(chatgpt_conversations), 5)
    
    def test_conversation_search(self):
        """Test searching conversations"""
        # Create conversations with searchable content
        test_conversations = [
            {
                'title': 'Python Programming Discussion',
                'url': 'https://chat.openai.com/c/python123',
                'messages': [{'role': 'user', 'content': 'How do I use Python decorators?'}]
            },
            {
                'title': 'JavaScript Framework Comparison',
                'url': 'https://chat.openai.com/c/js123',
                'messages': [{'role': 'user', 'content': 'React vs Vue vs Angular comparison'}]
            },
            {
                'title': 'Database Design',
                'url': 'https://chat.openai.com/c/db123',
                'messages': [{'role': 'user', 'content': 'SQL vs NoSQL database design patterns'}]
            }
        ]
        
        for conv_data in test_conversations:
            self.memory_nexus.save_conversation(conv_data)
        
        # Debug: List all conversations
        all_conversations = self.memory_nexus.get_conversations()
        print(f"DEBUG: Saved {len(all_conversations)} conversations:")
        for conv in all_conversations:
            print(f"  - {conv['title']}")
        
        # Search by title
        python_results = self.memory_nexus.search_conversations('Python')
        print(f"DEBUG: Search for 'Python' returned {len(python_results)} results")
        for result in python_results:
            print(f"  - Found: {result['title']}")
        
        self.assertEqual(len(python_results), 1)
        self.assertIn('Python', python_results[0]['title'])
        
        # Search by content
        database_results = self.memory_nexus.search_conversations('database')
        print(f"DEBUG: Search for 'database' returned {len(database_results)} results")
        for result in database_results:
            print(f"  - Found: {result['title']}")
        
        self.assertEqual(len(database_results), 1)
        self.assertIn('Database', database_results[0]['title'])
        
        # Search with no results
        no_results = self.memory_nexus.search_conversations('nonexistent')
        self.assertEqual(len(no_results), 0)
    
    def test_tag_management(self):
        """Test tag creation and assignment"""
        # Create tags
        tag1_id = self.memory_nexus.create_tag('Programming', '#007bff', 'Programming related conversations')
        tag2_id = self.memory_nexus.create_tag('Design', '#28a745', 'Design related conversations')
        
        self.assertIsInstance(tag1_id, int)
        self.assertIsInstance(tag2_id, int)
        
        # Get all tags
        tags = self.memory_nexus.get_tags()
        self.assertEqual(len(tags), 2)
        
        # Create conversation
        conversation_data = {
            'title': 'Tagged Conversation',
            'url': 'https://chat.openai.com/c/tagged123',
            'messages': [{'role': 'user', 'content': 'Test message'}]
        }
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        
        # Add tags to conversation
        self.memory_nexus.add_tag_to_conversation(conversation_id, tag1_id)
        self.memory_nexus.add_tag_to_conversation(conversation_id, tag2_id)
        
        # Verify tags
        conversation = self.memory_nexus.get_conversation(conversation_id)
        self.assertIn(tag1_id, conversation['tags'])
        self.assertIn(tag2_id, conversation['tags'])
        
        # Remove tag
        self.memory_nexus.remove_tag_from_conversation(conversation_id, tag1_id)
        conversation = self.memory_nexus.get_conversation(conversation_id)
        self.assertNotIn(tag1_id, conversation['tags'])
        self.assertIn(tag2_id, conversation['tags'])
    
    def test_analysis_results(self):
        """Test saving and retrieving analysis results"""
        # Create conversation
        conversation_data = {
            'title': 'Analysis Test',
            'url': 'https://chat.openai.com/c/analysis123',
            'messages': [{'role': 'user', 'content': 'Test for analysis'}]
        }
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        
        # Save analysis result
        analysis_data = {
            'summary': 'This is a test conversation',
            'key_points': ['Point 1', 'Point 2'],
            'sentiment': 'positive'
        }
        
        analysis_id = self.memory_nexus.save_analysis_result(
            conversation_id=conversation_id,
            analysis_type='summary',
            result_data=analysis_data,
            template_used='Basic Summary',
            processing_time=1.5
        )
        
        self.assertIsInstance(analysis_id, int)
        
        # Retrieve analysis results
        results = self.memory_nexus.get_analysis_results(conversation_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['analysis_type'], 'summary')
        self.assertEqual(results[0]['result_data']['summary'], 'This is a test conversation')
        self.assertEqual(results[0]['processing_time'], 1.5)
    
    def test_template_management(self):
        """Test template creation and retrieval"""
        # Create custom template
        template_content = '''
        Analyze this conversation and provide:
        1. Main topics
        2. Key insights
        3. Action items
        
        Conversation: {{ conversation.title }}
        '''
        
        template_id = self.memory_nexus.create_template(
            name='Custom Analysis',
            template_content=template_content,
            description='Custom analysis template',
            category='custom'
        )
        
        self.assertIsInstance(template_id, int)
        
        # Get templates by category
        custom_templates = self.memory_nexus.get_templates(category='custom')
        self.assertEqual(len(custom_templates), 1)
        self.assertEqual(custom_templates[0]['name'], 'Custom Analysis')
        
        # Get all templates
        all_templates = self.memory_nexus.get_templates()
        self.assertGreater(len(all_templates), 1)  # Should have defaults + custom
    
    def test_settings_management(self):
        """Test settings storage and retrieval"""
        # Set custom setting
        self.memory_nexus.set_setting('test_setting', 'test_value', 'Test setting')
        
        # Retrieve setting
        value = self.memory_nexus.get_setting('test_setting')
        self.assertEqual(value, 'test_value')
        
        # Test default value
        default_value = self.memory_nexus.get_setting('nonexistent_setting', 'default')
        self.assertEqual(default_value, 'default')
        
        # Update setting
        self.memory_nexus.set_setting('test_setting', 'updated_value')
        updated_value = self.memory_nexus.get_setting('test_setting')
        self.assertEqual(updated_value, 'updated_value')
    
    def test_statistics(self):
        """Test statistics calculation"""
        # Create some test data
        for i in range(3):
            conversation_data = {
                'title': f'Stats Test {i}',
                'url': f'https://chat.openai.com/c/stats{i}',
                'messages': [
                    {'role': 'user', 'content': f'Message {i} with some words'},
                    {'role': 'assistant', 'content': f'Response {i} with more words'}
                ]
            }
            self.memory_nexus.save_conversation(conversation_data)
        
        # Create tags
        self.memory_nexus.create_tag('Test Tag')
        
        # Get statistics
        stats = self.memory_nexus.get_statistics()
        
        self.assertEqual(stats['total_conversations'], 3)
        self.assertEqual(stats['total_messages'], 6)  # 2 messages per conversation
        self.assertGreater(stats['total_words'], 0)
        self.assertEqual(stats['total_tags'], 1)
        self.assertEqual(stats['total_analyses'], 0)
        self.assertEqual(stats['recent_conversations'], 3)
    
    def test_conversation_deletion(self):
        """Test conversation deletion"""
        # Create conversation
        conversation_data = {
            'title': 'Delete Test',
            'url': 'https://chat.openai.com/c/delete123',
            'messages': [{'role': 'user', 'content': 'Delete me'}]
        }
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        
        # Verify it exists
        conversation = self.memory_nexus.get_conversation(conversation_id)
        self.assertIsNotNone(conversation)
        
        # Delete it
        success = self.memory_nexus.delete_conversation(conversation_id)
        self.assertTrue(success)
        
        # Verify it's gone
        deleted_conversation = self.memory_nexus.get_conversation(conversation_id)
        self.assertIsNone(deleted_conversation)
    
    def test_database_backup(self):
        """Test database backup functionality"""
        # Create some data
        conversation_data = {
            'title': 'Backup Test',
            'url': 'https://chat.openai.com/c/backup123',
            'messages': [{'role': 'user', 'content': 'Backup me'}]
        }
        self.memory_nexus.save_conversation(conversation_data)
        
        # Create backup
        backup_success = self.memory_nexus.backup_database()
        self.assertTrue(backup_success)
        
        # Check that backup file exists
        backup_dir = Path("data/backups")
        backup_files = list(backup_dir.glob("dreamscape_backup_*.db"))
        self.assertGreater(len(backup_files), 0)
        
        # Clean up backup
        for backup_file in backup_files:
            backup_file.unlink()


class TestMemoryNexusIntegration(unittest.TestCase):
    """Integration tests for Memory Nexus with real data scenarios"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.memory_nexus = MemoryNexus(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if hasattr(self.memory_nexus, 'SessionLocal'):
            try:
                self.memory_nexus.SessionLocal().close()
            except Exception:
                pass
        import time
        for _ in range(5):
            try:
                if os.path.exists(self.db_path):
                    os.unlink(self.db_path)
                break
            except PermissionError:
                time.sleep(0.2)
    
    def test_full_conversation_workflow(self):
        """Test complete conversation workflow from creation to analysis"""
        # 1. Create conversation with realistic data
        conversation_data = {
            'title': 'Python Web Development Discussion',
            'url': 'https://chat.openai.com/c/python-web-dev',
            'source': 'chatgpt',
            'status': 'active',
            'metadata': {
                'topic': 'web development',
                'language': 'python',
                'difficulty': 'intermediate'
            },
            'messages': [
                {
                    'role': 'user',
                    'content': 'I want to build a web application using Python. What framework would you recommend?',
                    'timestamp': datetime.now()
                },
                {
                    'role': 'assistant',
                    'content': 'For Python web development, I recommend Flask for smaller applications or Django for larger, more complex projects. Flask is lightweight and flexible, while Django provides more built-in features and follows the "batteries-included" philosophy.',
                    'timestamp': datetime.now()
                },
                {
                    'role': 'user',
                    'content': 'Can you explain the differences between Flask and Django in more detail?',
                    'timestamp': datetime.now()
                },
                {
                    'role': 'assistant',
                    'content': 'Flask is a micro-framework that gives you the basics to build web applications. You have more control over components and can choose what to include. Django is a full-stack framework with built-in admin interface, ORM, authentication, and many other features out of the box.',
                    'timestamp': datetime.now()
                }
            ]
        }
        
        # 2. Save conversation
        conversation_id = self.memory_nexus.save_conversation(conversation_data)
        self.assertGreater(conversation_id, 0)
        
        # 3. Create and assign tags
        python_tag_id = self.memory_nexus.create_tag('Python', '#3776ab')
        webdev_tag_id = self.memory_nexus.create_tag('Web Development', '#f7df1e')
        
        self.memory_nexus.add_tag_to_conversation(conversation_id, python_tag_id)
        self.memory_nexus.add_tag_to_conversation(conversation_id, webdev_tag_id)
        
        # 4. Retrieve and verify conversation
        conversation = self.memory_nexus.get_conversation(conversation_id)
        self.assertEqual(conversation['title'], 'Python Web Development Discussion')
        self.assertEqual(len(conversation['messages']), 4)
        self.assertEqual(conversation['message_count'], 4)
        self.assertIn(python_tag_id, conversation['tags'])
        self.assertIn(webdev_tag_id, conversation['tags'])
        
        # 5. Perform analysis
        analysis_data = {
            'summary': 'Discussion about Python web development frameworks',
            'key_topics': ['Flask', 'Django', 'Web Development', 'Python'],
            'recommendations': ['Flask for smaller apps', 'Django for larger projects'],
            'complexity': 'intermediate'
        }
        
        analysis_id = self.memory_nexus.save_analysis_result(
            conversation_id=conversation_id,
            analysis_type='summary',
            result_data=analysis_data,
            template_used='Custom Analysis',
            processing_time=2.3
        )
        
        # 6. Verify analysis
        analyses = self.memory_nexus.get_analysis_results(conversation_id)
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0]['analysis_type'], 'summary')
        self.assertEqual(analyses[0]['result_data']['summary'], 'Discussion about Python web development frameworks')
        
        # 7. Search functionality
        search_results = self.memory_nexus.search_conversations('Flask')
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['id'], conversation_id)
        
        # 8. Check statistics
        stats = self.memory_nexus.get_statistics()
        self.assertEqual(stats['total_conversations'], 1)
        self.assertEqual(stats['total_messages'], 4)
        self.assertEqual(stats['total_tags'], 2)
        self.assertEqual(stats['total_analyses'], 1)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMemoryNexus))
    test_suite.addTest(unittest.makeSuite(TestMemoryNexusIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Memory Nexus Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("✅ All Memory Nexus tests passed!")
        sys.exit(0) 