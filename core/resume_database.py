#!/usr/bin/env python3
"""
Dream.OS Resume Database
========================

Database operations for the resume tracking system.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResumeDatabase:
    """Database manager for resume tracking system."""
    
    def __init__(self, db_path: str = "dreamos_resume.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with resume tracking schema."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self._create_schema()
            logger.info(f"✅ Resume database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize resume database: {e}")
            raise
    
    def _create_schema(self):
        """Create the resume tracking database schema."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            xp_reward INTEGER DEFAULT 0,
            completed_at TEXT NOT NULL,
            evidence TEXT,
            tags TEXT DEFAULT '[]',
            impact_score INTEGER DEFAULT 5,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS skills (
            name TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            current_level INTEGER DEFAULT 1,
            max_level INTEGER DEFAULT 100,
            current_xp INTEGER DEFAULT 0,
            next_level_xp INTEGER DEFAULT 100,
            description TEXT,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            achievements TEXT DEFAULT '[]'
        );
        
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            technologies TEXT DEFAULT '[]',
            achievements TEXT DEFAULT '[]',
            impact_description TEXT,
            team_size INTEGER DEFAULT 1,
            role TEXT DEFAULT 'Developer',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category);
        CREATE INDEX IF NOT EXISTS idx_achievements_completed_at ON achievements(completed_at);
        CREATE INDEX IF NOT EXISTS idx_achievements_impact ON achievements(impact_score);
        CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
        CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
        CREATE INDEX IF NOT EXISTS idx_projects_start_date ON projects(start_date);
        """
        
        cursor = self.conn.cursor()
        cursor.executescript(schema_sql)
        self.conn.commit()
        logger.info("✅ Resume database schema created/verified")
    
    def get_connection(self):
        """Get the database connection."""
        return self.conn
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 