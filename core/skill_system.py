"""
RuneScape-inspired Skill System for Dream.OS

Manages skill progression, experience calculations, and unlocks similar to RuneScape's
skill system. Each skill levels independently and has its own progression path.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from math import floor
import json

@dataclass
class SkillLevel:
    level: int
    current_xp: int
    xp_to_next: int
    unlocks: List[str]

@dataclass
class SkillDefinition:
    name: str
    description: str
    category: str
    related_skills: List[str]
    max_level: int = 99  # Classic RuneScape max level

class SkillSystem:
    # RuneScape-style XP formula constants
    XP_TABLE = [0]  # Will be populated with XP requirements for each level
    
    # Skill Categories
    COMBAT_SKILLS = ["debugging", "error_handling", "security"]
    PRODUCTION_SKILLS = ["coding", "refactoring", "optimization"]
    GATHERING_SKILLS = ["research", "analysis", "documentation"]
    SUPPORT_SKILLS = ["architecture", "design_patterns", "testing"]
    
    def __init__(self):
        """Initialize the skill system."""
        self._generate_xp_table()
        self.skills = self._initialize_skills()
        self.unlocks = self._initialize_unlocks()

    def _generate_xp_table(self):
        """Generate RuneScape-style XP table for levels 1-99."""
        for level in range(1, 100):
            points = floor(sum(floor(level + 300 * (2 ** (level / 7.0))) for level in range(1, level)) / 4)
            self.XP_TABLE.append(points)

    def _initialize_skills(self) -> Dict[str, SkillDefinition]:
        """Initialize all available skills."""
        return {
            # Combat Skills (Debug & Security)
            "debugging": SkillDefinition(
                name="Debugging",
                description="Combat bugs and errors in code",
                category="combat",
                related_skills=["error_handling", "analysis"]
            ),
            "error_handling": SkillDefinition(
                name="Error Handling",
                description="Defend against and manage errors",
                category="combat",
                related_skills=["debugging", "security"]
            ),
            "security": SkillDefinition(
                name="Security",
                description="Protect code and systems",
                category="combat",
                related_skills=["error_handling", "architecture"]
            ),

            # Production Skills (Code Creation)
            "coding": SkillDefinition(
                name="Coding",
                description="Write efficient and clean code",
                category="production",
                related_skills=["refactoring", "design_patterns"]
            ),
            "refactoring": SkillDefinition(
                name="Refactoring",
                description="Improve existing code",
                category="production",
                related_skills=["coding", "optimization"]
            ),
            "optimization": SkillDefinition(
                name="Optimization",
                description="Enhance code performance",
                category="production",
                related_skills=["refactoring", "performance"]
            ),

            # Gathering Skills (Research & Analysis)
            "research": SkillDefinition(
                name="Research",
                description="Gather information and solutions",
                category="gathering",
                related_skills=["analysis", "documentation"]
            ),
            "analysis": SkillDefinition(
                name="Analysis",
                description="Understand complex systems",
                category="gathering",
                related_skills=["research", "architecture"]
            ),
            "documentation": SkillDefinition(
                name="Documentation",
                description="Create and maintain documentation",
                category="gathering",
                related_skills=["research", "technical_writing"]
            ),

            # Support Skills (Architecture & Design)
            "architecture": SkillDefinition(
                name="Architecture",
                description="Design system structures",
                category="support",
                related_skills=["design_patterns", "system_design"]
            ),
            "design_patterns": SkillDefinition(
                name="Design Patterns",
                description="Implement reusable solutions",
                category="support",
                related_skills=["architecture", "coding"]
            ),
            "testing": SkillDefinition(
                name="Testing",
                description="Verify code quality",
                category="support",
                related_skills=["debugging", "quality_assurance"]
            )
        }

    def _initialize_unlocks(self) -> Dict[str, Dict[int, List[str]]]:
        """Initialize skill unlocks for each level."""
        return {
            "debugging": {
                1: ["Basic error messages"],
                10: ["Stack trace analysis"],
                20: ["Debugger tools"],
                30: ["Advanced breakpoints"],
                40: ["Memory inspection"],
                50: ["Performance profiling"],
                60: ["Thread debugging"],
                70: ["Remote debugging"],
                80: ["Kernel debugging"],
                90: ["Time travel debugging"],
                99: ["Master debugger cape"]
            },
            "coding": {
                1: ["Basic syntax"],
                10: ["Functions and classes"],
                20: ["Design patterns"],
                30: ["APIs and interfaces"],
                40: ["System integration"],
                50: ["Microservices"],
                60: ["Distributed systems"],
                70: ["Cloud architecture"],
                80: ["System scaling"],
                90: ["Enterprise architecture"],
                99: ["Master coder cape"]
            },
            # ... similar unlocks for other skills
        }

    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP (RuneScape formula)."""
        for level, requirement in enumerate(self.XP_TABLE):
            if xp < requirement:
                return max(1, level - 1)
        return 99

    def get_xp_for_level(self, level: int) -> int:
        """Get XP required for a specific level."""
        if level < 1 or level > 99:
            raise ValueError("Level must be between 1 and 99")
        return self.XP_TABLE[level]

    def get_skill_info(self, skill_name: str, current_xp: int) -> SkillLevel:
        """Get current level info for a skill."""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")

        current_level = self.calculate_level(current_xp)
        next_level = min(current_level + 1, 99)
        xp_to_next = self.XP_TABLE[next_level] - current_xp

        # Get unlocks for current level
        current_unlocks = self.unlocks.get(skill_name, {}).get(current_level, [])

        return SkillLevel(
            level=current_level,
            current_xp=current_xp,
            xp_to_next=xp_to_next,
            unlocks=current_unlocks
        )

    def award_xp(self, current_xp: int, xp_award: int) -> Tuple[int, List[int]]:
        """
        Award XP and return new total and levels gained.
        Returns: (new_total_xp, levels_gained)
        """
        old_level = self.calculate_level(current_xp)
        new_total = current_xp + xp_award
        new_level = self.calculate_level(new_total)
        
        levels_gained = []
        if new_level > old_level:
            levels_gained = list(range(old_level + 1, new_level + 1))
            
        return new_total, levels_gained

    def get_skill_milestones(self, skill_name: str) -> List[Dict]:
        """Get all milestones for a skill."""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")

        milestones = []
        for level, unlocks in self.unlocks.get(skill_name, {}).items():
            milestones.append({
                "level": level,
                "xp_required": self.XP_TABLE[level],
                "unlocks": unlocks
            })
        
        return sorted(milestones, key=lambda x: x["level"])

    def get_total_level(self, skill_levels: Dict[str, int]) -> int:
        """Calculate total level across all skills."""
        return sum(skill_levels.values())

    def get_combat_level(self, combat_skills: Dict[str, int]) -> int:
        """
        Calculate combat level based on combat-related skills.
        Uses a RuneScape-inspired formula.
        """
        debug_level = combat_skills.get("debugging", 1)
        error_level = combat_skills.get("error_handling", 1)
        security_level = combat_skills.get("security", 1)
        
        base = (debug_level + error_level + security_level) / 3
        return min(99, floor(base))

    def get_skill_category_levels(self, skill_levels: Dict[str, int]) -> Dict[str, float]:
        """Get average levels for each skill category."""
        categories = {
            "combat": self.COMBAT_SKILLS,
            "production": self.PRODUCTION_SKILLS,
            "gathering": self.GATHERING_SKILLS,
            "support": self.SUPPORT_SKILLS
        }
        
        averages = {}
        for category, skills in categories.items():
            levels = [skill_levels.get(skill, 1) for skill in skills]
            averages[category] = sum(levels) / len(levels)
            
        return averages

    def calculate_xp_bonus(self, skill_name: str, skill_levels: Dict[str, int]) -> float:
        """
        Calculate XP bonus based on related skills.
        Higher levels in related skills give small XP bonuses.
        """
        if skill_name not in self.skills:
            return 1.0

        skill_def = self.skills[skill_name]
        related_levels = [skill_levels.get(skill, 1) for skill in skill_def.related_skills]
        
        # Max 10% bonus based on related skills
        bonus = sum(level / 99 for level in related_levels) / len(related_levels)
        return 1.0 + (bonus * 0.1)

    def get_high_scores(self, all_player_skills: Dict[str, Dict[str, int]]) -> Dict[str, List[Tuple[str, int]]]:
        """Get high scores for all skills."""
        high_scores = {skill: [] for skill in self.skills}
        high_scores["total"] = []
        
        for player_id, skills in all_player_skills.items():
            # Add individual skill levels
            for skill, xp in skills.items():
                if skill in high_scores:
                    level = self.calculate_level(xp)
                    high_scores[skill].append((player_id, level))
            
            # Add total level
            total = sum(self.calculate_level(xp) for xp in skills.values())
            high_scores["total"].append((player_id, total))
        
        # Sort all high scores
        for skill in high_scores:
            high_scores[skill] = sorted(high_scores[skill], key=lambda x: x[1], reverse=True)
            
        return high_scores