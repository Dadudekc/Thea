import tempfile
import os
import unittest
from unittest import mock

from core.memory_manager import MemoryManager
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from core.mmorpg_models import QuestType


class TestQuestIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_path = self.temp_db.name
        self.temp_db.close()

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass

    def test_bug_hunt_quest_generated(self):
        # Pre-instantiate MemoryManager with temp DB so the patched processor uses it
        mm = MemoryManager(self.db_path)

        # Patch DreamscapeProcessor.MemoryManager reference to return our instance
        with mock.patch("core.dreamscape_processor.MemoryManager", lambda *a, **k: mm):
            dp = DreamscapeProcessor()
            content = "Please fix bug in API and debug error handling logic."
            dp.process_conversation_for_dreamscape("conv1", content)

            # close internal engine connection to release DB handle
            if hasattr(dp, "_mmorpg"):
                dp._mmorpg.memory_manager.close()

        # Load MMORPGEngine which should restore game_state from same DB
        engine = MMORPGEngine(self.db_path)
        bug_hunt_quests = [q for q in engine.get_quests_by_status("active") if q.quest_type == QuestType.BUG_HUNT]
        self.assertTrue(bug_hunt_quests, "BUG_HUNT quest should be generated and active")
        self.assertGreater(engine.game_state.total_xp, 0, "XP should be awarded")

        # close engine
        engine.memory_manager.close()

        # ensure main mm closed
        mm.close()


if __name__ == "__main__":
    unittest.main() 