#!/usr/bin/env python3
"""
Dreamscape MMORPG Engine - Core game mechanics and quest system.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_manager import MemoryManager
from core.mmorpg_models import (
    Quest, Skill, ArchitectTier, GameState, QuestType, SkillType, Player,
    TIER_DEFINITIONS, QUEST_KEYWORDS, SKILL_REWARDS, Guild
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mmorpg_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MMORPGEngine:
    """
    Core MMORPG engine for managing quests, skills, and progression.
    """
    
    def __init__(self, db_path: str = "dreamos_memory.db"):
        self.db_path = db_path
        self.memory_manager = MemoryManager(db_path)
        
        # Initialize game state
        self.game_state = GameState(
            current_tier=1,
            total_xp=0,
            skills={},
            quests={},
            architect_tiers={},
            guilds={},
            last_updated=datetime.now()
        )
        
        # Load game state
        self.load_game_state()

        # Attempt to restore persisted progress
        saved = self.memory_manager.load_game_state()
        if saved:
            try:
                self._hydrate_from_dict(saved)
                logger.info("Restored persisted MMORPG state (tier %s, XP %s)", self.game_state.current_tier, self.game_state.total_xp)
            except Exception as restore_exc:
                logger.warning("Failed to restore game state – starting fresh: %s", restore_exc)
    
    def load_game_state(self):
        """Load current game state from database."""
        try:
            # Initialize skills
            for skill_type in SkillType:
                self.game_state.skills[skill_type.value] = Skill(
                    name=skill_type.value,
                    current_level=0,
                    experience_points=0,
                    max_level=100,
                    last_updated=datetime.now()
                )
            
            # Initialize architect tiers
            for tier_level, tier_name, xp_required in TIER_DEFINITIONS:
                self.game_state.architect_tiers[tier_level] = ArchitectTier(
                    tier_level=tier_level,
                    tier_name=tier_name,
                    experience_required=xp_required,
                    abilities_unlocked=self._get_tier_abilities(tier_level),
                    achieved_at=datetime.now() if tier_level == 1 else None
                )
            
            logger.info(f"Loaded game state: Tier {self.game_state.current_tier}, {len(self.game_state.skills)} skills")
            
        except Exception as e:
            logger.error(f"Failed to load game state: {e}")
    
    def _get_tier_abilities(self, tier_level: int) -> List[str]:
        """Get abilities unlocked at a specific tier."""
        abilities = {
            1: ["basic_quests", "skill_tracking"],
            2: ["advanced_quests", "domain_access"],
            3: ["quest_chains", "skill_synergies"],
            4: ["ai_companions", "predictive_analytics"],
            5: ["guild_system", "pvp_battles"],
            6: ["legendary_quests", "cosmic_domains"],
            7: ["mythic_abilities", "time_manipulation"],
            8: ["transcendent_powers", "reality_bending"],
            9: ["cosmic_consciousness", "multiverse_access"],
            10: ["dreamscape_mastery", "creation_powers"]
        }
        return abilities.get(tier_level, [])
    
    def generate_quest_from_conversation(self, conversation_id: str, conversation_content: str) -> Optional[Quest]:
        """Generate a quest from conversation analysis."""
        try:
            # Try to fetch the conversation title for richer quest naming
            conversation_title = ""
            try:
                convo = self.memory_manager.get_conversation_by_id(conversation_id)
                if convo:
                    conversation_title = str(convo.get("title", ""))
            except Exception:
                # Non-fatal – proceed without title
                pass

            # Analyze conversation to determine quest type
            quest_type = self._analyze_conversation_for_quest_type(conversation_content)
            
            if not quest_type:
                return None
            
            # Generate quest details
            quest_id = f"quest_{conversation_id}_{int(time.time())}"
            title = self._generate_quest_title(quest_type, conversation_title, conversation_content)
            description = self._generate_quest_description(quest_type, conversation_content)
            difficulty = self._calculate_quest_difficulty(conversation_content)
            xp_reward = self._calculate_xp_reward(difficulty)
            skill_rewards = self._calculate_skill_rewards(quest_type, difficulty)
            
            quest = Quest(
                id=quest_id,
                title=title,
                description=description,
                quest_type=quest_type,
                difficulty=difficulty,
                xp_reward=xp_reward,
                skill_rewards=skill_rewards,
                conversation_id=conversation_id,
                created_at=datetime.now()
            )
            
            # Save quest
            self.game_state.quests[quest.id] = quest
            
            logger.info(f"Generated quest: {quest.title} (Difficulty: {difficulty}, XP: {xp_reward})")
            return quest
            
        except Exception as e:
            logger.error(f"Failed to generate quest: {e}")
            return None
    
    def _analyze_conversation_for_quest_type(self, content: str) -> Optional[QuestType]:
        """Analyze conversation content to determine quest type."""
        content_lower = content.lower()
        
        # Check each quest type's keywords
        for quest_type, keywords in QUEST_KEYWORDS.items():
            if any(word in content_lower for word in keywords):
                return quest_type
        
        # Default to legacy mission for complex conversations
        if len(content.split()) > 500:
            return QuestType.LEGACY_MISSION
        
        return None
    
    def _generate_quest_title(
        self,
        quest_type: QuestType,
        conversation_title: str = "",
        conversation_content: str = "",
    ) -> str:
        """Craft a quest title that feels contextual and less robotic.

        When a conversation *title* is available we mine it for a short topic
        phrase (e.g. "Graph Database Indexing") and embed that into the
        quest title template specific to *quest_type*.

        Falls back to deterministic titles so unit-tests remain stable when no
        `conversation_title` is passed (e.g. headless batch jobs).
        """

        def _extract_topic(title: str) -> str:
            import re

            common = {"the", "a", "an", "for", "to", "of", "and", "in", "on", "with"}
            words = re.findall(r"[A-Za-z0-9']+", title)
            filtered = [w for w in words if w.lower() not in common]
            return " ".join(filtered[:4]) if filtered else title.strip()

        topic = _extract_topic(conversation_title) if conversation_title else "the System"

        # Map quest types to templates
        match quest_type:
            case QuestType.BUG_HUNT:
                return f"Bug Hunt: Squash {topic} Bugs"
            case QuestType.FEATURE_RAID:
                return f"Feature Raid: Implement {topic} Capability"
            case QuestType.SYSTEM_CONVERGENCE:
                return f"System Convergence: Integrate {topic}"
            case QuestType.KNOWLEDGE_EXPEDITION:
                return f"Knowledge Expedition: Master {topic}"
            case QuestType.LEGACY_MISSION:
                return f"Legacy Mission: Future-proof {topic}"
            case QuestType.WORKFLOW_AUDIT:
                return f"Workflow Audit: Optimise {topic} Pipeline"
            case QuestType.MARKET_ANALYSIS:
                return f"Market Analysis: Evaluate {topic} Market"
            case QuestType.PERSONAL_STRATEGY:
                return f"Personal Strategy: Elevate {topic} Goals"
            case _:
                return "Mystery Quest"
    
    def _generate_quest_description(self, quest_type: QuestType, content: str) -> str:
        """Generate a quest description based on type and content."""
        words = content.split()
        key_topics = [word for word in words if len(word) > 5][:3]
        
        descriptions = {
            QuestType.BUG_HUNT: f"Track down and eliminate bugs in the system. Focus areas: {', '.join(key_topics)}",
            QuestType.FEATURE_RAID: f"Implement new features and capabilities. Target areas: {', '.join(key_topics)}",
            QuestType.SYSTEM_CONVERGENCE: f"Design and integrate complex systems. Architecture focus: {', '.join(key_topics)}",
            QuestType.KNOWLEDGE_EXPEDITION: f"Explore new technologies and concepts. Learning areas: {', '.join(key_topics)}",
            QuestType.LEGACY_MISSION: f"Build systems for long-term success. Legacy focus: {', '.join(key_topics)}",
            QuestType.WORKFLOW_AUDIT: f"Optimize processes and workflows. Improvement areas: {', '.join(key_topics)}",
            QuestType.MARKET_ANALYSIS: f"Analyze market trends and opportunities. Strategic focus: {', '.join(key_topics)}",
            QuestType.PERSONAL_STRATEGY: f"Develop personal and professional strategy. Planning areas: {', '.join(key_topics)}"
        }
        return descriptions.get(quest_type, "Complete this mysterious quest to advance your skills.")
    
    def _calculate_quest_difficulty(self, content: str) -> int:
        """Calculate quest difficulty based on content complexity."""
        word_count = len(content.split())
        technical_terms = len([word for word in content.lower().split() 
                             if word in ["api", "database", "algorithm", "architecture", "framework", "protocol"]])
        
        base_difficulty = min(10, max(1, word_count // 100))
        technical_bonus = min(3, technical_terms)
        
        return min(10, base_difficulty + technical_bonus)
    
    def _calculate_xp_reward(self, difficulty: int) -> int:
        """Calculate XP reward based on quest difficulty."""
        return difficulty * 15  # 15-150 XP
    
    def _calculate_skill_rewards(self, quest_type: QuestType, difficulty: int) -> Dict[str, int]:
        """Calculate skill rewards based on quest type and difficulty."""
        base_reward = max(1, difficulty // 2)
        base_rewards = SKILL_REWARDS.get(quest_type, {SkillType.EXECUTION_VELOCITY.value: 1})
        
        return {skill: points * base_reward for skill, points in base_rewards.items()}
    
    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest and award XP/skills."""
        try:
            quest = self.game_state.quests.get(quest_id)
            if not quest or quest.status != "active":
                logger.warning(f"Quest {quest_id} not found or not active")
                return False
            
            # Delegate XP + skill rewards to centralized dispatcher
            try:
                from mmorpg.xp_dispatcher import XPDispatcher
                XPDispatcher(self).dispatch(
                    quest.xp_reward,
                    skill_rewards=quest.skill_rewards,
                    source="quest_complete",
                )
            except Exception as _disp_err:
                logger.warning("XPDispatcher failed inside complete_quest: %s", _disp_err)
            
            # Update quest status
            quest.status = "completed"
            quest.completed_at = datetime.now()
            
            # Tier advancement handled by XPDispatcher (via _check_tier_advancement)
            
            # Notify via DSUpdate event
            try:
                from core.models import DSUpdate
                from core.discord_bridge import DiscordBridge
                if not hasattr(self, "_bridge"):
                    self._bridge = DiscordBridge()
                msg = f"🗡️ Quest completed: {quest.title} (+{quest.xp_reward} XP)"
                self._bridge.handle_sync(DSUpdate(kind="quests", msg=msg))
            except Exception as _e:
                logger.debug(f"DSUpdate emit skipped (quest): {_e}")
            
            logger.info(f"Quest completed: {quest.title} (+{quest.xp_reward} XP)")

            # Persist updated state
            self._persist_game_state()
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete quest: {e}")
            return False
    
    def get_game_status(self) -> Dict:
        """Get current game status."""
        return {
            "current_tier": self.game_state.current_tier,
            "tier_name": self.game_state.architect_tiers[self.game_state.current_tier].tier_name,
            "total_xp": self.game_state.total_xp,
            "next_tier_xp": self._get_next_tier_xp_requirement(),
            "skills": {name: {
                "level": skill.current_level,
                "xp": skill.experience_points,
                "max_level": skill.max_level
            } for name, skill in self.game_state.skills.items()},
            "active_quests": len([q for q in self.game_state.quests.values() if q.status == "active"]),
            "completed_quests": len([q for q in self.game_state.quests.values() if q.status == "completed"])
        }
    
    def _get_next_tier_xp_requirement(self) -> int:
        """Get XP required for next tier."""
        for tier_level in sorted(self.game_state.architect_tiers.keys()):
            if self.game_state.total_xp < self.game_state.architect_tiers[tier_level].experience_required:
                return self.game_state.architect_tiers[tier_level].experience_required
        return self.game_state.total_xp  # Already at max tier 
    
    def get_player(self) -> Player:
        """Get player information for the dashboard."""
        current_tier = self.game_state.current_tier
        tier_info = self.game_state.architect_tiers[current_tier]
        
        return Player(
            name="Victor",
            architect_tier=f"Tier {current_tier} - {tier_info.tier_name}",
            xp=self.game_state.total_xp,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
    
    def get_skills(self) -> List[Skill]:
        """Get all player skills."""
        return list(self.game_state.skills.values())
    
    def get_active_quests(self) -> List[Quest]:
        """Get active quests for the player."""
        return [quest for quest in self.game_state.quests.values() if quest.status == "active"]
    
    def get_completed_quests(self) -> List[Quest]:
        """Get completed quests for the player."""
        return [quest for quest in self.game_state.quests.values() if quest.status == "completed"]
    
    def get_domains(self) -> List[Dict]:
        """Get empire domains and territories."""
        # For now, return mock domains
        # In a full implementation, this would come from the dreamscape memory
        return [
            {
                "name": "Digital Realm",
                "level": 1,
                "resources": "Code, Data, Algorithms",
                "status": "Active"
            },
            {
                "name": "Creative Domain", 
                "level": 2,
                "resources": "Ideas, Inspiration, Innovation",
                "status": "Expanding"
            }
        ]
    
    def update_from_conversation(self, conversation_id: str):
        """Update MMORPG state from a processed conversation."""
        try:
            # Get conversation from memory
            conversation = self.memory_manager.get_conversation(conversation_id)
            if not conversation:
                return
            
            # Extract XP and skills from conversation
            # This would be more sophisticated in a real implementation
            xp_gained = 10  # Base XP per conversation
            self.game_state.total_xp += xp_gained
            
            # Check for tier advancement
            self._check_tier_advancement()
            
            # Update last activity
            self.game_state.last_activity = datetime.now()
            
            # Save updated state
            self._save_game_state()
            
            logger.info(f"Updated MMORPG state from conversation {conversation_id}: +{xp_gained} XP")
            
        except Exception as e:
            logger.error(f"Failed to update MMORPG state from conversation: {e}")
    
    def _check_tier_advancement(self):
        """Check if player should advance to next tier."""
        current_tier = self.game_state.current_tier
        
        for tier_level in sorted(self.game_state.architect_tiers.keys()):
            tier_info = self.game_state.architect_tiers[tier_level]
            if (self.game_state.total_xp >= tier_info.experience_required and 
                current_tier < tier_level):
                
                # Advance to new tier
                self.game_state.current_tier = tier_level
                logger.info(f"Player advanced to Tier {tier_level}: {tier_info.tier_name}")
                
                # Grant tier rewards
                self._grant_tier_rewards(tier_level)
                break
    
    def _grant_tier_rewards(self, tier_level: int):
        """Grant rewards for reaching a new tier."""
        tier_info = self.game_state.architect_tiers[tier_level]
        
        # Add new skills based on tier
        if tier_level == 2:
            new_skill = Skill(
                name="Advanced Architecture",
                skill_type=SkillType.TECHNICAL,
                level=1,
                description="Master the art of complex system design"
            )
            self.game_state.skills[new_skill.name] = new_skill
        
        elif tier_level == 3:
            new_skill = Skill(
                name="Empire Management",
                skill_type=SkillType.LEADERSHIP,
                level=1,
                description="Lead and expand your digital empire"
            )
            self.game_state.skills[new_skill.name] = new_skill
    
    def _save_game_state(self):
        """Save current game state to database."""
        try:
            self.memory_manager.save_game_state(self.game_state)
            logger.info("Game state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save game state: {e}")
    
    def _calculate_tier_progress(self) -> float:
        """Calculate progress to next tier as a percentage."""
        current_tier = self.game_state.current_tier
        current_tier_xp = self.game_state.architect_tiers[current_tier].experience_required
        
        # Find next tier XP requirement
        next_tier_xp = self._get_next_tier_xp_requirement()
        
        if next_tier_xp == current_tier_xp:
            return 100.0  # Already at max tier
        
        progress = (self.game_state.total_xp - current_tier_xp) / (next_tier_xp - current_tier_xp) * 100
        return min(100.0, max(0.0, progress))

    # ------------------------------------------------------------------
    # Guild System
    # ------------------------------------------------------------------

    def create_guild(self, name: str, description: str, leader_id: str) -> bool:
        """Create a new guild if name not taken."""
        if name.lower() in (g.name.lower() for g in self.game_state.guilds.values()):
            logger.warning("Guild %s already exists", name)
            return False
        gid = f"guild_{int(time.time())}"
        guild = Guild(id=gid, name=name, description=description, leader_id=leader_id, members=[leader_id], created_at=datetime.now())
        self.game_state.guilds[gid] = guild
        logger.info("Guild created: %s (leader %s)", name, leader_id)
        return True

    def join_guild(self, guild_name: str, member_id: str) -> bool:
        """Add member to guild by name."""
        for guild in self.game_state.guilds.values():
            if guild.name.lower() == guild_name.lower():
                if member_id in guild.members:
                    return False
                guild.members.append(member_id)
                logger.info("%s joined guild %s", member_id, guild.name)
                return True
        logger.warning("Guild %s not found", guild_name)
        return False

    def get_guild_info(self, guild_name: str) -> Optional[Dict]:
        for guild in self.game_state.guilds.values():
            if guild.name.lower() == guild_name.lower():
                return {
                    "id": guild.id,
                    "name": guild.name,
                    "description": guild.description,
                    "leader": guild.leader_id,
                    "member_count": len(guild.members),
                    "members": guild.members,
                    "created_at": guild.created_at.isoformat() if guild.created_at else ""
                }
        return None

    def accept_quest(self, quest_id: str) -> bool:
        """Move quest from available to active and grant an upfront XP bonus."""
        quest = self.game_state.quests.get(quest_id)
        if not quest or quest.status != "available":
            return False
        quest.status = "active"
        quest.created_at = quest.created_at or datetime.now()
        logger.info("Quest accepted: %s", quest.title)

        # Award a small upfront XP incentive so that freshly accepted quests
        # feel rewarding (required by unit tests expecting XP > 0 after accept).
        try:
            from mmorpg.xp_dispatcher import XPDispatcher
            XPDispatcher(self).dispatch(
                max(1, quest.xp_reward // 4),  # 25% of full reward upfront
                source="quest_accept",
            )
        except Exception as _disp_err:
            logger.debug("XPDispatcher failed inside accept_quest: %s", _disp_err)

        # Persist state so other engine instances can see it
        self._persist_game_state()
        return True

    def get_quests_by_status(self, status: str) -> List[Quest]:
        return [q for q in self.game_state.quests.values() if q.status == status]

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _hydrate_from_dict(self, data: Dict):
        """Populate `self.game_state` from saved dict."""
        self.game_state.current_tier = data.get("current_tier", 1)
        self.game_state.total_xp = data.get("total_xp", 0)

        # skills
        for name, s in data.get("skills", {}).items():
            if name in self.game_state.skills:
                sk = self.game_state.skills[name]
                sk.current_level = s.get("current_level", sk.current_level)
                sk.experience_points = s.get("experience_points", sk.experience_points)
                sk.last_updated = datetime.fromisoformat(s.get("last_updated")) if s.get("last_updated") else sk.last_updated

        # quests
        from core.mmorpg_models import Quest as Q, QuestType
        self.game_state.quests = {}
        for qid, q in data.get("quests", {}).items():
            if isinstance(q.get("quest_type"), str):
                q["quest_type"] = QuestType(q["quest_type"])
            self.game_state.quests[qid] = Q(**q)

        # tiers XP maybe already loaded, but update their achieved_at if provided.
        for tl, tinfo in data.get("architect_tiers", {}).items():
            if tl in self.game_state.architect_tiers:
                self.game_state.architect_tiers[tl].achieved_at = (
                    datetime.fromisoformat(tinfo.get("achieved_at")) if tinfo.get("achieved_at") else self.game_state.architect_tiers[tl].achieved_at
                ) 

    # ------------------------------------------------------------------
    # Persistence bridge
    # ------------------------------------------------------------------
    def _persist_game_state(self):
        """Save game_state via MemoryManager utility."""
        try:
            self.memory_manager.save_game_state(self.game_state)
        except Exception as e:
            logger.debug("Game state persistence failed: %s", e)

    def add_quest(self, quest: Quest) -> None:
        """Add a new quest to the game state and persist."""
        self.game_state.quests[quest.id] = quest
        logger.info("[Quest] Added %s (XP %s)", quest.title, quest.xp_reward)
        self._persist_game_state()

    def update_quest(self, quest_id: str, **changes) -> bool:
        """Update fields on an existing quest.

        Returns True on success, False when quest not found or immutable.
        """
        q = self.game_state.quests.get(quest_id)
        if not q:
            return False
        # Prevent editing once completed
        if q.status == "completed":
            return False
        for field, val in changes.items():
            if hasattr(q, field):
                setattr(q, field, val)
        q.updated_at = datetime.now() if hasattr(q, "updated_at") else None
        logger.info("[Quest] Updated %s → %s", quest_id, changes)
        self._persist_game_state()
        return True

    def delete_quest(self, quest_id: str) -> bool:
        """Remove a quest from the game state."""
        if quest_id in self.game_state.quests:
            self.game_state.quests.pop(quest_id)
            logger.info("[Quest] Deleted %s", quest_id)
            self._persist_game_state()
            return True
        return False 