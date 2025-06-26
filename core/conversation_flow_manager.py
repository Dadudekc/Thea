"""
Conversation Flow Manager for Dream.OS MMORPG

Tracks conversations as MMORPG quests, managing player progress, rewards,
and multi-conversation storylines. Integrates with the MMORPG engine to
provide game-like progression through AI interactions.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

from .mmorpg_engine import MMORPGEngine
from .mmorpg_models import QuestStatus, PlayerStats, QuestReward
from .context_injection import ContextInjectionSystem, ContextConfig
from .template_engine import PromptTemplateEngine

@dataclass
class QuestDifficulty:
    NOVICE = "Novice"          # Simple, single-step tasks
    APPRENTICE = "Apprentice"  # Multi-step, straightforward tasks
    ADEPT = "Adept"           # Complex tasks requiring planning
    EXPERT = "Expert"         # Challenging, multi-phase projects
    MASTER = "Master"         # Critical, system-wide changes
    LEGENDARY = "Legendary"   # Major architectural decisions

@dataclass
class QuestType:
    CODING = "Coding Quest"
    DEBUGGING = "Debug Mission"
    LEARNING = "Knowledge Quest"
    PLANNING = "Strategy Quest"
    REFACTORING = "Refactor Saga"
    ARCHITECTURE = "Architect's Challenge"

@dataclass
class ConversationQuest:
    id: str
    title: str
    description: str
    quest_type: str
    difficulty: str
    status: QuestStatus
    objectives: List[Dict]
    rewards: QuestReward
    parent_quest_id: Optional[str] = None
    player_id: Optional[str] = None
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    checkpoints: List[Dict] = None
    context_ids: List[str] = None

class ConversationFlowManager:
    def __init__(self, 
                 db_path: str,
                 mmorpg_engine: MMORPGEngine,
                 context_injection: ContextInjectionSystem,
                 template_engine: PromptTemplateEngine):
        """Initialize the conversation flow manager."""
        self.db_path = db_path
        self.mmorpg = mmorpg_engine
        self.context_injection = context_injection
        self.template_engine = template_engine
        self.active_quests: Dict[str, ConversationQuest] = {}

    def start_conversation_quest(self,
                               title: str,
                               description: str,
                               quest_type: str,
                               difficulty: str,
                               objectives: List[Dict],
                               player_id: Optional[str] = None,
                               parent_quest_id: Optional[str] = None) -> ConversationQuest:
        """Start a new conversation quest."""
        # Create quest rewards based on difficulty
        rewards = self._calculate_quest_rewards(difficulty, quest_type)

        # Create the quest
        quest = ConversationQuest(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            quest_type=quest_type,
            difficulty=difficulty,
            status=QuestStatus.IN_PROGRESS,
            objectives=objectives,
            rewards=rewards,
            parent_quest_id=parent_quest_id,
            player_id=player_id,
            started_at=datetime.now(),
            checkpoints=[],
            context_ids=[]
        )

        # Register with MMORPG engine
        self.mmorpg.register_quest(
            quest_id=quest.id,
            title=quest.title,
            description=quest.description,
            difficulty=quest.difficulty,
            rewards=quest.rewards
        )

        # Store in active quests
        self.active_quests[quest.id] = quest

        return quest

    def _calculate_quest_rewards(self, difficulty: str, quest_type: str) -> QuestReward:
        """Calculate rewards based on quest difficulty and type."""
        # Base XP and skill points by difficulty
        base_rewards = {
            QuestDifficulty.NOVICE: {"xp": 100, "skill_points": 1},
            QuestDifficulty.APPRENTICE: {"xp": 250, "skill_points": 2},
            QuestDifficulty.ADEPT: {"xp": 500, "skill_points": 3},
            QuestDifficulty.EXPERT: {"xp": 1000, "skill_points": 5},
            QuestDifficulty.MASTER: {"xp": 2000, "skill_points": 8},
            QuestDifficulty.LEGENDARY: {"xp": 5000, "skill_points": 10}
        }

        # Skill focus based on quest type
        skill_focus = {
            QuestType.CODING: ["coding", "problem_solving"],
            QuestType.DEBUGGING: ["debugging", "analysis"],
            QuestType.LEARNING: ["knowledge", "adaptability"],
            QuestType.PLANNING: ["strategy", "architecture"],
            QuestType.REFACTORING: ["refactoring", "code_quality"],
            QuestType.ARCHITECTURE: ["architecture", "system_design"]
        }

        base = base_rewards.get(difficulty, base_rewards[QuestDifficulty.NOVICE])
        skills = skill_focus.get(quest_type, ["general"])

        return QuestReward(
            xp=base["xp"],
            skill_points=base["skill_points"],
            skill_focus=skills
        )

    def update_quest_progress(self,
                            quest_id: str,
                            progress_update: Dict,
                            context_id: Optional[str] = None) -> None:
        """Update quest progress and add checkpoint."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        # Add checkpoint
        checkpoint = {
            "timestamp": datetime.now(),
            "update": progress_update,
            "context_id": context_id
        }
        quest.checkpoints.append(checkpoint)

        # Update context tracking
        if context_id:
            quest.context_ids.append(context_id)

        # Update MMORPG engine
        self.mmorpg.update_quest_progress(
            quest_id=quest_id,
            progress=len(quest.checkpoints) / len(quest.objectives)
        )

        # Check for quest completion
        self._check_quest_completion(quest)

    def _check_quest_completion(self, quest: ConversationQuest) -> None:
        """Check if all objectives are completed and complete quest if so."""
        completed_objectives = sum(1 for obj in quest.objectives if obj.get("completed", False))
        
        if completed_objectives == len(quest.objectives):
            self.complete_quest(quest.id)

    def complete_quest(self, quest_id: str) -> None:
        """Complete a quest and award rewards."""
        quest = self.active_quests.get(quest_id)
        if not quest or quest.status == QuestStatus.COMPLETED:
            return

        # Update quest status
        quest.status = QuestStatus.COMPLETED
        quest.completed_at = datetime.now()

        # Award rewards through MMORPG engine
        if quest.player_id:
            self.mmorpg.award_quest_rewards(
                player_id=quest.player_id,
                quest_id=quest_id,
                rewards=quest.rewards
            )

        # Update parent quest if exists
        if quest.parent_quest_id:
            parent_quest = self.active_quests.get(quest.parent_quest_id)
            if parent_quest:
                self._update_parent_quest_progress(parent_quest)

    def _update_parent_quest_progress(self, parent_quest: ConversationQuest) -> None:
        """Update parent quest progress based on subquest completion."""
        # Find all subquests
        subquests = [q for q in self.active_quests.values() if q.parent_quest_id == parent_quest.id]
        completed_subquests = [q for q in subquests if q.status == QuestStatus.COMPLETED]

        # Update progress
        progress = len(completed_subquests) / len(subquests) if subquests else 0
        self.mmorpg.update_quest_progress(
            quest_id=parent_quest.id,
            progress=progress
        )

    def get_quest_context(self, quest_id: str, include_parent: bool = True) -> str:
        """Get formatted context for a quest, including parent quest if specified."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        contexts = []

        # Add parent quest context if requested
        if include_parent and quest.parent_quest_id:
            parent_quest = self.active_quests.get(quest.parent_quest_id)
            if parent_quest:
                contexts.append(self._format_quest_context(parent_quest))

        # Add current quest context
        contexts.append(self._format_quest_context(quest))

        return "\n\n".join(contexts)

    def _format_quest_context(self, quest: ConversationQuest) -> str:
        """Format a quest's context for inclusion in prompts."""
        context_parts = [
            f"Quest: {quest.title} ({quest.difficulty} {quest.quest_type})",
            f"Description: {quest.description}",
            "\nObjectives:"
        ]

        for obj in quest.objectives:
            status = "✓" if obj.get("completed", False) else "○"
            context_parts.append(f"  {status} {obj['description']}")

        if quest.checkpoints:
            context_parts.append("\nProgress:")
            for checkpoint in quest.checkpoints[-3:]:  # Show last 3 checkpoints
                timestamp = checkpoint["timestamp"].strftime("%Y-%m-%d %H:%M")
                context_parts.append(f"  [{timestamp}] {checkpoint['update']}")

        return "\n".join(context_parts)

    def get_active_quests(self, player_id: Optional[str] = None) -> List[ConversationQuest]:
        """Get all active quests, optionally filtered by player."""
        if player_id:
            return [q for q in self.active_quests.values()
                   if q.player_id == player_id and q.status == QuestStatus.IN_PROGRESS]
        return [q for q in self.active_quests.values()
                if q.status == QuestStatus.IN_PROGRESS]

    def get_quest_stats(self, quest_id: str) -> Dict:
        """Get detailed stats for a quest."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        return {
            "title": quest.title,
            "type": quest.quest_type,
            "difficulty": quest.difficulty,
            "status": quest.status,
            "duration": (quest.completed_at or datetime.now()) - quest.started_at,
            "objectives_completed": sum(1 for obj in quest.objectives if obj.get("completed", False)),
            "total_objectives": len(quest.objectives),
            "checkpoints": len(quest.checkpoints),
            "contexts_used": len(quest.context_ids),
            "rewards": quest.rewards.__dict__
        }

    def suggest_next_quest(self, player_id: str) -> Optional[Dict]:
        """Suggest next quest based on player stats and history."""
        # Get player stats from MMORPG engine
        player_stats = self.mmorpg.get_player_stats(player_id)
        
        # Analyze completed quests
        completed_quests = [q for q in self.active_quests.values()
                          if q.player_id == player_id and q.status == QuestStatus.COMPLETED]

        # Calculate appropriate difficulty
        suggested_difficulty = self._calculate_suggested_difficulty(player_stats, completed_quests)

        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(player_stats)

        return {
            "suggested_difficulty": suggested_difficulty,
            "recommended_quest_types": [qt for qt, skills in QuestType.__dict__.items()
                                      if any(skill in skill_gaps for skill in skills)],
            "skill_focus": skill_gaps[:2]  # Top 2 skills to focus on
        }

    def _calculate_suggested_difficulty(self, player_stats: PlayerStats, completed_quests: List[ConversationQuest]) -> str:
        """Calculate suggested difficulty based on player stats and history."""
        # This is a simplified version - could be made more sophisticated
        if player_stats.level >= 50:
            return QuestDifficulty.LEGENDARY
        elif player_stats.level >= 40:
            return QuestDifficulty.MASTER
        elif player_stats.level >= 30:
            return QuestDifficulty.EXPERT
        elif player_stats.level >= 20:
            return QuestDifficulty.ADEPT
        elif player_stats.level >= 10:
            return QuestDifficulty.APPRENTICE
        else:
            return QuestDifficulty.NOVICE

    def _identify_skill_gaps(self, player_stats: PlayerStats) -> List[str]:
        """Identify skills that need improvement based on player stats."""
        # Compare skill levels and return skills below average
        avg_skill_level = sum(getattr(player_stats, skill, 0) 
                            for skill in ["coding", "debugging", "knowledge", 
                                        "strategy", "refactoring", "architecture"]) / 6
        
        return [skill for skill in ["coding", "debugging", "knowledge", 
                                  "strategy", "refactoring", "architecture"]
                if getattr(player_stats, skill, 0) < avg_skill_level]