"""Task tracking utilities for Dream.OS GUI panels.
Provides a lightweight in-memory TaskTracker so the Quest/Task panels
can operate without a full database backend.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional

# Optional dependency on the MMORPG engine – used only to grant XP when a task is completed.
try:
    from core.mmorpg_engine import MMORPGEngine
except Exception:  # pragma: no cover – circular import / missing dependency edge-case
    MMORPGEngine = None  # type: ignore


class TaskPriority(str, Enum):
    """Difficulty tiers map to MMORPG roles."""

    SCOUT = "Scout"
    ADVENTURER = "Adventurer"
    HERO = "Hero"
    LEGENDARY = "Legendary"


class TaskStatus(str, Enum):
    """High-level workflow states."""

    TODO = "Available"
    IN_PROGRESS = "Accepted"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"


@dataclass(slots=True)
class Task:
    """Simple dataclass representing a quest / development task."""

    id: str
    title: str
    description: str
    priority: TaskPriority = TaskPriority.SCOUT
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    xp_reward: int = 0

    # Parent relationship for sub-quests; not used by the tracker directly but
    # required for tree views in Tk / Qt panels.
    parent_quest_id: Optional[str] = None


class TaskTracker:
    """In-memory tracker storing tasks for the GUI.

    This is deliberately lightweight – persistence can be layered on later via
    the database or the MMORPG engine quest system.
    """

    _XP_TABLE = {
        TaskPriority.SCOUT: 10,
        TaskPriority.ADVENTURER: 25,
        TaskPriority.HERO: 50,
        TaskPriority.LEGENDARY: 100,
    }

    def __init__(self, mmorpg_engine: Optional["MMORPGEngine"] = None):
        self.engine = mmorpg_engine
        self.tasks: Dict[str, Task] = {}

    # ---------- helpers ----------
    @staticmethod
    def _new_id() -> str:
        """Return a short reproducible-enough identifier."""
        return uuid.uuid4().hex[:8]

    # ---------- CRUD ----------
    def create_task(
        self,
        *,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.SCOUT,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        parent_quest_id: Optional[str] = None,
    ) -> Task:
        task_id = self._new_id()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags or [],
            xp_reward=self._XP_TABLE.get(priority, 0),
            parent_quest_id=parent_quest_id,
        )
        self.tasks[task_id] = task
        return task

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = status

        if status is TaskStatus.COMPLETED and self.engine is not None:
            # Best-effort XP grant – ignore if the engine is missing a method.
            try:
                self.engine.add_xp(task.xp_reward)
            except Exception:
                pass
        return True

    # ---------- analytics ----------
    def get_daily_summary(self) -> Dict[str, object]:
        today: date = datetime.utcnow().date()
        status_breakdown: Dict[TaskStatus, int] = {s: 0 for s in TaskStatus}
        overdue_tasks = 0
        total_xp_available = 0

        for task in self.tasks.values():
            # Status counts
            status_breakdown[task.status] += 1

            # Overdue? (ignore completed ones)
            if (
                task.due_date
                and task.due_date.date() < today
                and task.status is not TaskStatus.COMPLETED
            ):
                overdue_tasks += 1

            # XP still obtainable
            if task.status is not TaskStatus.COMPLETED:
                total_xp_available += task.xp_reward

        return {
            "total_tasks": len(self.tasks),
            "status_breakdown": status_breakdown,
            "overdue_tasks": overdue_tasks,
            "total_xp_available": total_xp_available,
        } 