#!/usr/bin/env python3
"""
Dream.OS Resume Tracker
=======================

Comprehensive resume tracking system with achievement database, skill tracking,
and automated resume generation from MMORPG activities and development work.
"""

import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from .resume_models import Achievement, Skill, Project
from .resume_database import ResumeDatabase
from .resume_generator import ResumeGenerator
from .skill_manager import SkillManager

logger = logging.getLogger(__name__)

class ResumeTracker:
    """
    Orchestrates resume tracking, skill management, and resume generation.
    """
    def __init__(self, db_path: str = "dreamos_resume.db"):
        self.db = ResumeDatabase(db_path)
        self.skill_manager = SkillManager(self.db.get_connection())
        self.generator = ResumeGenerator()

    def add_achievement(self, achievement: Achievement) -> bool:
        """Add a new achievement to the database."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO achievements
                (id, name, description, category, difficulty, xp_reward, completed_at, 
                 evidence, tags, impact_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    achievement.id,
                    achievement.name,
                    achievement.description,
                    achievement.category,
                    achievement.difficulty,
                    achievement.xp_reward,
                    achievement.completed_at,
                    achievement.evidence,
                    json.dumps(achievement.tags),
                    achievement.impact_score,
                    datetime.now().isoformat()
                )
            )
            self.skill_manager.update_skills_from_achievement(achievement)
            self.db.get_connection().commit()
            logger.info(f"✅ Achievement added: {achievement.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add achievement: {e}")
            return False

    def get_achievements(self, category: str = None, limit: int = 50) -> List[Achievement]:
        """Get achievements from the database."""
        try:
            cursor = self.db.get_connection().cursor()
            if category:
                cursor.execute(
                    """
                    SELECT * FROM achievements 
                    WHERE category = ? 
                    ORDER BY completed_at DESC 
                    LIMIT ?
                    """, (category, limit))
            else:
                cursor.execute(
                    """
                    SELECT * FROM achievements 
                    ORDER BY completed_at DESC 
                    LIMIT ?
                    """, (limit,))
            achievements = []
            for row in cursor.fetchall():
                achievement = Achievement(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    category=row['category'],
                    difficulty=row['difficulty'],
                    xp_reward=row['xp_reward'],
                    completed_at=row['completed_at'],
                    evidence=row['evidence'],
                    tags=json.loads(row['tags']),
                    impact_score=row['impact_score']
                )
                achievements.append(achievement)
            return achievements
        except Exception as e:
            logger.error(f"❌ Failed to get achievements: {e}")
            return []

    def add_project(self, project: Project) -> bool:
        """Add a new project to the database."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO projects
                (id, name, description, start_date, end_date, status, technologies,
                 achievements, impact_description, team_size, role, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    project.name,
                    project.description,
                    project.start_date,
                    project.end_date,
                    project.status,
                    json.dumps(project.technologies),
                    json.dumps(project.achievements),
                    project.impact_description,
                    project.team_size,
                    project.role,
                    datetime.now().isoformat()
                )
            )
            self.db.get_connection().commit()
            logger.info(f"✅ Project added: {project.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add project: {e}")
            return False

    def get_projects(self, status: str = None, limit: int = 20) -> List[Project]:
        """Get projects from the database."""
        try:
            cursor = self.db.get_connection().cursor()
            if status:
                cursor.execute(
                    """
                    SELECT * FROM projects 
                    WHERE status = ? 
                    ORDER BY start_date DESC 
                    LIMIT ?
                    """, (status, limit))
            else:
                cursor.execute(
                    """
                    SELECT * FROM projects 
                    ORDER BY start_date DESC 
                    LIMIT ?
                    """, (limit,))
            projects = []
            for row in cursor.fetchall():
                project = Project(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    status=row['status'],
                    technologies=json.loads(row['technologies']),
                    achievements=json.loads(row['achievements']),
                    impact_description=row['impact_description'],
                    team_size=row['team_size'],
                    role=row['role']
                )
                projects.append(project)
            return projects
        except Exception as e:
            logger.error(f"❌ Failed to get projects: {e}")
            return []

    def get_skills(self) -> List[Skill]:
        """Get all skills from the database."""
        return self.skill_manager.get_all_skills()

    def generate_resume(self, format_type: str = 'markdown', include_achievements: bool = True) -> str:
        """Generate a resume in the specified format."""
        return self.generator.generate_resume(self, format_type, include_achievements)

    def export_resume(self, output_path: str, format_type: str = 'markdown') -> bool:
        """Export resume to a file."""
        return self.generator.export_resume(self, output_path, format_type)

    def get_resume_stats(self) -> Dict[str, Any]:
        """Get resume statistics."""
        try:
            cursor = self.db.get_connection().cursor()
            
            # Get achievement stats
            cursor.execute("SELECT COUNT(*) as total FROM achievements")
            total_achievements = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(xp_reward) as total_xp FROM achievements")
            total_xp = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) as completed FROM achievements WHERE completed_at IS NOT NULL")
            completed_achievements = cursor.fetchone()[0]
            
            # Get project stats
            cursor.execute("SELECT COUNT(*) as total FROM projects")
            total_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as active FROM projects WHERE status = 'active'")
            active_projects = cursor.fetchone()[0]
            
            # Get skill stats
            cursor.execute("SELECT COUNT(*) as total FROM skills")
            total_skills = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(current_level) as avg_level FROM skills")
            avg_skill_level = cursor.fetchone()[0] or 0
            
            return {
                'achievements': {
                    'total': total_achievements,
                    'completed': completed_achievements,
                    'total_xp': total_xp
                },
                'projects': {
                    'total': total_projects,
                    'active': active_projects
                },
                'skills': {
                    'total': total_skills,
                    'average_level': round(avg_skill_level, 1)
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to get resume stats: {e}")
            return {}

    def close(self):
        """Close the database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

def main():
    """Main entry point for the Resume Tracker."""
    try:
        tracker = ResumeTracker()
        
        # Example usage
        logger.info("Resume Tracker initialized successfully")
        
        # Get stats
        stats = tracker.get_resume_stats()
        logger.info(f"Resume Stats: {stats}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
