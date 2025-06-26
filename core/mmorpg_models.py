#!/usr/bin/env python3
"""
Dreamscape MMORPG Models - Data structures for the MMORPG system.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class QuestType(Enum):
    """Types of quests in the Dreamscape MMORPG."""
    BUG_HUNT = "bug_hunt"
    FEATURE_RAID = "feature_raid"
    SYSTEM_CONVERGENCE = "system_convergence"
    KNOWLEDGE_EXPEDITION = "knowledge_expedition"
    LEGACY_MISSION = "legacy_mission"
    WORKFLOW_AUDIT = "workflow_audit"
    MARKET_ANALYSIS = "market_analysis"
    PERSONAL_STRATEGY = "personal_strategy"

class SkillType(Enum):
    """Core skills in the Dreamscape MMORPG."""
    SYSTEM_CONVERGENCE = "system_convergence"
    EXECUTION_VELOCITY = "execution_velocity"
    STRATEGIC_INTELLIGENCE = "strategic_intelligence"
    AI_SELF_ORGANIZATION = "ai_self_organization"
    DOMAIN_STABILIZATION = "domain_stabilization"

@dataclass
class Quest:
    """Quest data structure."""
    id: str
    title: str
    description: str
    quest_type: QuestType
    difficulty: int  # 1-10
    xp_reward: int
    skill_rewards: Dict[str, int]
    status: str = "available"  # available, active, completed, failed
    created_at: datetime = None
    completed_at: datetime = None
    conversation_id: str = None

@dataclass
class Skill:
    """Skill data structure."""
    name: str
    current_level: int = 0
    experience_points: int = 0
    max_level: int = 100
    last_updated: datetime = None

@dataclass
class ArchitectTier:
    """Architect tier data structure."""
    tier_level: int
    tier_name: str
    experience_required: int
    abilities_unlocked: List[str]
    achieved_at: datetime = None

@dataclass
class Guild:
    """Guild data structure."""
    id: str
    name: str
    description: str = ""
    leader_id: str = ""
    members: List[str] = None
    created_at: datetime = None
    def __post_init__(self):
        if self.members is None:
            self.members = []

@dataclass
class GameState:
    """Complete game state data structure."""
    current_tier: int
    total_xp: int
    skills: Dict[str, Skill]
    quests: Dict[str, Quest]
    architect_tiers: Dict[int, ArchitectTier]
    guilds: Dict[str, Guild]
    last_updated: datetime = None

@dataclass
class Player:
    """Player data structure."""
    name: str
    architect_tier: str = "Tier 1 - Novice"
    xp: int = 0
    total_conversations: int = 0
    total_messages: int = 0
    total_words: int = 0
    created_at: datetime = None
    last_active: datetime = None
    
    def get_next_level_xp(self) -> int:
        """Get XP required for next level."""
        try:
            # Extract current tier number from architect_tier string
            tier_parts = self.architect_tier.split()
            if len(tier_parts) >= 2:
                current_tier = int(tier_parts[1])
            else:
                current_tier = 1
            
            # Find the next tier's XP requirement
            for tier_level, tier_name, xp_required in TIER_DEFINITIONS:
                if tier_level > current_tier:
                    return xp_required
            
            # If already at max tier, return current XP
            return self.xp
            
        except (ValueError, IndexError) as e:
            # Fallback to a reasonable default
            return 100

# Tier definitions for easy access
TIER_DEFINITIONS = [
    (1, "Novice Architect", 0),
    (2, "Apprentice Architect", 100),
    (3, "Journeyman Architect", 500),
    (4, "Master Architect", 1000),
    (5, "Grand Architect", 2500),
    (6, "Legendary Architect", 5000),
    (7, "Mythic Architect", 10000),
    (8, "Transcendent Architect", 25000),
    (9, "Cosmic Architect", 50000),
    (10, "Dreamscape Architect", 100000)
]

# Quest type mappings for analysis
QUEST_KEYWORDS = {
    QuestType.BUG_HUNT: ["bug", "error", "fix", "debug", "issue", "problem"],
    QuestType.FEATURE_RAID: ["feature", "implement", "add", "create", "build", "develop"],
    QuestType.SYSTEM_CONVERGENCE: ["architecture", "system", "design", "structure", "integration"],
    QuestType.KNOWLEDGE_EXPEDITION: ["learn", "study", "research", "explore", "understand", "tutorial"],
    QuestType.PERSONAL_STRATEGY: ["strategy", "plan", "roadmap", "vision", "future", "long-term"],
    QuestType.WORKFLOW_AUDIT: ["workflow", "process", "optimize", "improve", "efficiency"],
    QuestType.MARKET_ANALYSIS: ["market", "business", "competition", "industry", "trend"]
}

# Skill reward mappings
SKILL_REWARDS = {
    QuestType.BUG_HUNT: {SkillType.EXECUTION_VELOCITY.value: 2},
    QuestType.FEATURE_RAID: {SkillType.EXECUTION_VELOCITY.value: 1, SkillType.SYSTEM_CONVERGENCE.value: 1},
    QuestType.SYSTEM_CONVERGENCE: {SkillType.SYSTEM_CONVERGENCE.value: 2, SkillType.STRATEGIC_INTELLIGENCE.value: 1},
    QuestType.KNOWLEDGE_EXPEDITION: {SkillType.STRATEGIC_INTELLIGENCE.value: 2},
    QuestType.LEGACY_MISSION: {SkillType.STRATEGIC_INTELLIGENCE.value: 1, SkillType.DOMAIN_STABILIZATION.value: 2},
    QuestType.WORKFLOW_AUDIT: {SkillType.AI_SELF_ORGANIZATION.value: 2},
    QuestType.MARKET_ANALYSIS: {SkillType.STRATEGIC_INTELLIGENCE.value: 2},
    QuestType.PERSONAL_STRATEGY: {SkillType.STRATEGIC_INTELLIGENCE.value: 2}
} 