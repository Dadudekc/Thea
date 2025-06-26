import pytest

from core.mmorpg_engine import MMORPGEngine


def test_engine_quest_consistency():
    engine = MMORPGEngine()
    active_via_method = engine.get_active_quests()
    active_via_state = [q for q in engine.game_state.quests.values() if q.status == "active"]
    assert active_via_method == active_via_state 