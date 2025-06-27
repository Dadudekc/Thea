import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory_manager import MemoryNexus


class TestAdvancedSearch(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.nexus = MemoryNexus(self.db_path)

    def tearDown(self):
        if hasattr(self.nexus, 'SessionLocal'):
            try:
                self.nexus.SessionLocal().close()
            except Exception:
                pass
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_negative_term(self):
        data = [
            {
                'title': 'Python Tips',
                'url': 'https://chat.openai.com/c/python',
                'messages': [{'role': 'user', 'content': 'Some Python advice'}]
            },
            {
                'title': 'JavaScript Tricks',
                'url': 'https://chat.openai.com/c/js',
                'messages': [{'role': 'user', 'content': 'JS specifics'}]
            }
        ]
        for conv in data:
            self.nexus.save_conversation(conv)

        results = self.nexus.advanced_search_conversations('Tips -JavaScript')
        self.assertEqual(len(results), 1)
        self.assertIn('Python', results[0]['title'])


if __name__ == '__main__':
    unittest.main()
