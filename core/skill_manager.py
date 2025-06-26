#!/usr/bin/env python3
"""
Dream.OS Skill Manager
======================

Skill tracking and progression management.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from .resume_models import Skill, Achievement

logger = logging.getLogger(__name__)

class SkillManager:
    """Manage skill tracking and progression."""
    
    def __init__(self, db_connection):
        """
        Initialize the skill manager.
        
        Args:
            db_connection: Database connection object
        """
        self.conn = db_connection
        self._initialize_default_skills()
    
    def _initialize_default_skills(self):
        """Initialize default skills in the database."""
        # Default skill definitions
        default_skills = {
            'System Convergence': {
                'category': 'technical',
                'description': 'Ability to integrate complex systems and architectures',
                'max_level': 100
            },
            'Execution Velocity': {
                'category': 'technical', 
                'description': 'Speed and efficiency of development and deployment',
                'max_level': 100
            },
            'Strategic Intelligence': {
                'category': 'soft',
                'description': 'Long-term planning and strategic decision-making',
                'max_level': 100
            },
            'AI-Driven Self-Organization': {
                'category': 'ai',
                'description': 'Automation and AI integration capabilities',
                'max_level': 100
            },
            'Domain Stabilization': {
                'category': 'domain',
                'description': 'Maintaining and improving system stability',
                'max_level': 100
            },
            'Multi-Model Mastery': {
                'category': 'ai',
                'description': 'Expertise in comparative AI testing and optimization',
                'max_level': 100
            },
            'Prompt Engineering': {
                'category': 'ai',
                'description': 'Skill in creating effective AI prompts and templates',
                'max_level': 100
            },
            'Code Quality': {
                'category': 'technical',
                'description': 'Writing clean, maintainable, and efficient code',
                'max_level': 100
            },
            'Problem Solving': {
                'category': 'soft',
                'description': 'Analytical thinking and creative problem resolution',
                'max_level': 100
            },
            'Leadership': {
                'category': 'soft',
                'description': 'Team leadership and project management',
                'max_level': 100
            }
        }
        
        cursor = self.conn.cursor()
        
        for skill_name, skill_data in default_skills.items():
            cursor.execute("""
                INSERT OR IGNORE INTO skills 
                (name, category, description, max_level, next_level_xp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                skill_name,
                skill_data['category'],
                skill_data['description'],
                skill_data['max_level'],
                100  # Initial next level XP
            ))
        
        self.conn.commit()
        logger.info("✅ Default skills initialized")
    
    def update_skills_from_achievement(self, achievement: Achievement):
        """Update skills based on achievement completion."""
        cursor = self.conn.cursor()
        
        # Determine which skills this achievement affects
        affected_skills = self._map_achievement_to_skills(achievement)
        
        for skill_name in affected_skills:
            # Get current skill data
            cursor.execute("SELECT * FROM skills WHERE name = ?", (skill_name,))
            skill_row = cursor.fetchone()
            
            if skill_row:
                current_xp = skill_row['current_xp'] + achievement.xp_reward
                current_level = skill_row['current_level']
                next_level_xp = skill_row['next_level_xp']
                
                # Check for level up
                while current_xp >= next_level_xp and current_level < skill_row['max_level']:
                    current_level += 1
                    current_xp -= next_level_xp
                    next_level_xp = int(next_level_xp * 1.5)  # Exponential XP requirement
                
                # Update skill
                cursor.execute("""
                    UPDATE skills 
                    SET current_level = ?, current_xp = ?, next_level_xp = ?, 
                        last_updated = ?, achievements = ?
                    WHERE name = ?
                """, (
                    current_level,
                    current_xp,
                    next_level_xp,
                    datetime.now().isoformat(),
                    json.dumps(affected_skills),
                    skill_name
                ))
    
    def _map_achievement_to_skills(self, achievement: Achievement) -> List[str]:
        """Map an achievement to relevant skills based on category and content."""
        skill_mapping = {
            'quest': ['System Convergence', 'Execution Velocity'],
            'skill': ['Strategic Intelligence', 'Problem Solving'],
            'project': ['Code Quality', 'Leadership', 'System Convergence'],
            'milestone': ['Strategic Intelligence', 'Domain Stabilization'],
            'special': ['AI-Driven Self-Organization', 'Multi-Model Mastery']
        }
        
        # Base skills from category
        skills = skill_mapping.get(achievement.category, [])
        
        # Add skills based on achievement name/content
        achievement_text = f"{achievement.name} {achievement.description}".lower()
        
        if any(word in achievement_text for word in ['ai', 'model', 'prompt', 'gpt']):
            skills.extend(['Multi-Model Mastery', 'Prompt Engineering'])
        
        if any(word in achievement_text for word in ['system', 'architecture', 'integration']):
            skills.append('System Convergence')
        
        if any(word in achievement_text for word in ['speed', 'velocity', 'fast', 'efficient']):
            skills.append('Execution Velocity')
        
        if any(word in achievement_text for word in ['strategy', 'planning', 'vision']):
            skills.append('Strategic Intelligence')
        
        if any(word in achievement_text for word in ['automation', 'auto', 'self']):
            skills.append('AI-Driven Self-Organization')
        
        if any(word in achievement_text for word in ['stability', 'maintain', 'improve']):
            skills.append('Domain Stabilization')
        
        if any(word in achievement_text for word in ['code', 'programming', 'development']):
            skills.append('Code Quality')
        
        if any(word in achievement_text for word in ['team', 'lead', 'manage']):
            skills.append('Leadership')
        
        # Remove duplicates and return
        return list(set(skills))
    
    def get_skills(self) -> List[Skill]:
        """
        Get all skills from the database.
        
        Returns:
            List of Skill objects
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM skills ORDER BY category, name")
            
            skills = []
            for row in cursor.fetchall():
                skill = Skill(
                    name=row['name'],
                    category=row['category'],
                    current_level=row['current_level'],
                    max_level=row['max_level'],
                    current_xp=row['current_xp'],
                    next_level_xp=row['next_level_xp'],
                    description=row['description'],
                    last_updated=row['last_updated'],
                    achievements=json.loads(row['achievements'])
                )
                skills.append(skill)
            
            return skills
            
        except Exception as e:
            logger.error(f"❌ Failed to get skills: {e}")
            return []
    
    def get_skill_stats(self) -> Dict[str, Any]:
        """
        Get skill statistics.
        
        Returns:
            Dictionary with skill statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Count skills
            cursor.execute("SELECT COUNT(*) as count FROM skills")
            skill_count = cursor.fetchone()['count']
            
            # Get top skills
            cursor.execute("""
                SELECT name, current_level, current_xp 
                FROM skills 
                ORDER BY current_level DESC, current_xp DESC 
                LIMIT 5
            """)
            top_skills = [dict(row) for row in cursor.fetchall()]
            
            return {
                'skill_count': skill_count,
                'top_skills': top_skills
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get skill stats: {e}")
            return {} 