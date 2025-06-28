import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import tempfile
import os
from pathlib import Path

from core.mmorpg_engine import MMORPGEngine
from core.mmorpg_models import QuestType, Quest
from mmorpg.xp_dispatcher import XPDispatcher
from datetime import datetime


def _make_engine():
    # Use a temporary file-backed DB to avoid interfering with real data
    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tf.close()
    engine = MMORPGEngine(db_path=tf.name)
    return engine, tf.name


def test_simple_xp_dispatch():
    engine, db_path = _make_engine()
    try:
        xp_before = engine.game_state.total_xp
        assert XPDispatcher(engine).dispatch(42, source="unit-test") is True
        assert engine.game_state.total_xp == xp_before + 42
    finally:
        try:
            engine.memory_manager.close()
        except Exception:
            pass
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_quest_completion_uses_dispatcher():
    engine, db_path = _make_engine()
    try:
        # Create a dummy quest and inject into game state
        quest_id = "quest_test_1"
        quest = Quest(
            id=quest_id,
            title="Unit Test Quest",
            description="Test XP dispatch via quest completion",
            quest_type=QuestType.BUG_HUNT,
            difficulty=1,
            xp_reward=25,
            skill_rewards={},
            created_at=datetime.now(),
        )
        engine.game_state.quests[quest_id] = quest
        engine.accept_quest(quest_id)
        pre_xp = engine.game_state.total_xp
        assert engine.complete_quest(quest_id) is True
        assert engine.game_state.total_xp == pre_xp + quest.xp_reward
        assert engine.game_state.quests[quest_id].status == "completed"
    finally:
        try:
            engine.memory_manager.close()
        except Exception:
            pass
        if os.path.exists(db_path):
            os.unlink(db_path) 