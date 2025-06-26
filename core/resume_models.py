#!/usr/bin/env python3
"""
Dream.OS Resume Models
=====================

Data structures for the resume tracking system.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Achievement:
    """Achievement data structure."""
    id: str
    name: str
    description: str
    category: str  # 'quest', 'skill', 'project', 'milestone', 'special'
    difficulty: int  # 1-10 scale
    xp_reward: int
    completed_at: str
    evidence: str  # URL, file path, or description of proof
    tags: List[str]
    impact_score: int  # 1-10 scale for resume impact

@dataclass
class Skill:
    """Skill data structure."""
    name: str
    category: str  # 'technical', 'soft', 'domain', 'ai'
    current_level: int
    max_level: int
    current_xp: int
    next_level_xp: int
    description: str
    last_updated: str
    achievements: List[str]  # Achievement IDs that contributed

@dataclass
class Project:
    """Project data structure."""
    id: str
    name: str
    description: str
    start_date: str
    end_date: Optional[str]
    status: str  # 'active', 'completed', 'paused', 'cancelled'
    technologies: List[str]
    achievements: List[str]
    impact_description: str
    team_size: int
    role: str 