#!/usr/bin/env python3
"""
Dream.OS Resume Generator
=========================

Resume generation in multiple formats (Markdown, HTML, JSON).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from dataclasses import asdict

from .resume_models import Skill, Project, Achievement

logger = logging.getLogger(__name__)

class ResumeGenerator:
    """Generate resumes in multiple formats."""
    
    def __init__(self):
        """Initialize the resume generator."""
        pass
    
    def generate_resume(self, skills: List[Skill], projects: List[Project], 
                       achievements: List[Achievement], format_type: str = 'markdown') -> str:
        """
        Generate a resume from the provided data.
        
        Args:
            skills: List of skills
            projects: List of projects
            achievements: List of achievements
            format_type: Output format ('markdown', 'html', 'json')
            
        Returns:
            Generated resume content
        """
        try:
            if format_type == 'markdown':
                return self._generate_markdown_resume(skills, projects, achievements)
            elif format_type == 'html':
                return self._generate_html_resume(skills, projects, achievements)
            elif format_type == 'json':
                return self._generate_json_resume(skills, projects, achievements)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to generate resume: {e}")
            return f"Error generating resume: {e}"
    
    def _generate_markdown_resume(self, skills: List[Skill], projects: List[Project], 
                                achievements: List[Achievement]) -> str:
        """Generate Markdown format resume."""
        resume = []
        
        # Header
        resume.append("# Thea Player - Software Architect & AI Specialist")
        resume.append("")
        resume.append("*Building autonomous systems and AI-driven solutions*")
        resume.append("")
        
        # Skills Section
        resume.append("## Skills")
        resume.append("")
        
        # Group skills by category
        skill_categories = {}
        for skill in skills:
            if skill.category not in skill_categories:
                skill_categories[skill.category] = []
            skill_categories[skill.category].append(skill)
        
        for category, category_skills in skill_categories.items():
            resume.append(f"### {category.title()}")
            for skill in category_skills:
                progress = (skill.current_xp / skill.next_level_xp) * 100 if skill.next_level_xp > 0 else 0
                resume.append(f"- **{skill.name}**: Level {skill.current_level} ({progress:.1f}% to next level)")
            resume.append("")
        
        # Experience/Projects Section
        if projects:
            resume.append("## Experience")
            resume.append("")
            
            for project in projects:
                resume.append(f"### {project.name}")
                resume.append(f"*{project.start_date} - {project.end_date or 'Present'}*")
                resume.append("")
                resume.append(project.description)
                resume.append("")
                
                if project.technologies:
                    resume.append(f"**Technologies**: {', '.join(project.technologies)}")
                    resume.append("")
                
                if project.impact_description:
                    resume.append(f"**Impact**: {project.impact_description}")
                    resume.append("")
        
        # Achievements Section
        if achievements:
            resume.append("## Key Achievements")
            resume.append("")
            
            # Group by category
            achievement_categories = {}
            for achievement in achievements:
                if achievement.category not in achievement_categories:
                    achievement_categories[achievement.category] = []
                achievement_categories[achievement.category].append(achievement)
            
            for category, category_achievements in achievement_categories.items():
                resume.append(f"### {category.title()}")
                for achievement in category_achievements:
                    resume.append(f"- **{achievement.name}**: {achievement.description}")
                resume.append("")
        
        return "\n".join(resume)
    
    def _generate_html_resume(self, skills: List[Skill], projects: List[Project], 
                            achievements: List[Achievement]) -> str:
        """Generate HTML format resume."""
        html = []
        
        # HTML header
        html.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Thea Player - Resume</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                .skill { margin: 10px 0; }
                .project { margin: 20px 0; padding: 15px; background: #f8f9fa; }
                .achievement { margin: 10px 0; }
            </style>
        </head>
        <body>
        """)
        
        # Header
        html.append("<h1>Thea Player - Software Architect & AI Specialist</h1>")
        html.append("<p><em>Building autonomous systems and AI-driven solutions</em></p>")
        
        # Skills
        html.append("<h2>Skills</h2>")
        skill_categories = {}
        for skill in skills:
            if skill.category not in skill_categories:
                skill_categories[skill.category] = []
            skill_categories[skill.category].append(skill)
        
        for category, category_skills in skill_categories.items():
            html.append(f"<h3>{category.title()}</h3>")
            for skill in category_skills:
                progress = (skill.current_xp / skill.next_level_xp) * 100 if skill.next_level_xp > 0 else 0
                html.append(f'<div class="skill"><strong>{skill.name}</strong>: Level {skill.current_level} ({progress:.1f}% to next level)</div>')
        
        # Projects
        if projects:
            html.append("<h2>Experience</h2>")
            for project in projects:
                html.append(f'<div class="project">')
                html.append(f"<h3>{project.name}</h3>")
                html.append(f"<p><em>{project.start_date} - {project.end_date or 'Present'}</em></p>")
                html.append(f"<p>{project.description}</p>")
                if project.technologies:
                    html.append(f"<p><strong>Technologies:</strong> {', '.join(project.technologies)}</p>")
                if project.impact_description:
                    html.append(f"<p><strong>Impact:</strong> {project.impact_description}</p>")
                html.append("</div>")
        
        # Achievements
        if achievements:
            html.append("<h2>Key Achievements</h2>")
            achievement_categories = {}
            for achievement in achievements:
                if achievement.category not in achievement_categories:
                    achievement_categories[achievement.category] = []
                achievement_categories[achievement.category].append(achievement)
            
            for category, category_achievements in achievement_categories.items():
                html.append(f"<h3>{category.title()}</h3>")
                for achievement in category_achievements:
                    html.append(f'<div class="achievement"><strong>{achievement.name}</strong>: {achievement.description}</div>')
        
        html.append("</body></html>")
        return "\n".join(html)
    
    def _generate_json_resume(self, skills: List[Skill], projects: List[Project], 
                            achievements: List[Achievement]) -> str:
        """Generate JSON format resume."""
        resume_data = {
            "header": {
                "name": "Thea Player",
                "title": "Software Architect & AI Specialist",
                "tagline": "Building autonomous systems and AI-driven solutions"
            },
            "skills": [asdict(skill) for skill in skills],
            "projects": [asdict(project) for project in projects],
            "achievements": [asdict(achievement) for achievement in achievements],
            "generated_at": datetime.now().isoformat()
        }
        
        return json.dumps(resume_data, indent=2)
    
    def export_resume(self, content: str, output_path: str) -> bool:
        """
        Export resume content to file.
        
        Args:
            content: Resume content to export
            output_path: Path to save the resume file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Resume exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export resume: {e}")
            return False 