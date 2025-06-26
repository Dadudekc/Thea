import pytest

from core.memory_manager import MemoryManager
from core.conversation_stats_updater import ConversationStatsUpdater


def test_trend_metrics_keys(tmp_path):
    """Ensure stats summary includes trend keys when requested."""
    db_file = tmp_path / "temp_memory.db"
    mm = MemoryManager(db_path=str(db_file))
    stats_updater = ConversationStatsUpdater(mm)
    summary = stats_updater.get_conversation_stats_summary(trend=True)

    expected_keys = {
        "daily_conversations",
        "weekly_conversations",
        "monthly_conversations",
        "avg_messages_per_conversation_last_30_days",
    }

    assert expected_keys.issubset(summary.keys()), (
        f"Trend metrics missing from summary: {expected_keys - summary.keys()}"
    ) 