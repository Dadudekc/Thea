#!/usr/bin/env python3
"""
Database Schema Manager for Memory Storage
Handles database initialization and schema creation.
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

class DatabaseSchemaManager:
    """Handles database schema creation and initialization."""
    
    def __init__(self):
        """Initialize the schema manager."""
        pass
    
    def create_schema(self, connection: sqlite3.Connection):
        """Create the database schema."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            timestamp TEXT,
            captured_at TEXT,
            model TEXT DEFAULT 'gpt-4o',
            tags TEXT DEFAULT '',
            summary TEXT,
            content TEXT,
            url TEXT,
            message_count INTEGER DEFAULT 0,
            word_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            prompt_text TEXT NOT NULL,
            prompt_type TEXT DEFAULT 'user',  -- 'user', 'system', 'template'
            prompt_category TEXT DEFAULT 'general',
            prompt_effectiveness INTEGER DEFAULT 0,  -- 0-10 rating
            extracted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );
        
        CREATE TABLE IF NOT EXISTS memory_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            content_hash TEXT,
            content_type TEXT,  -- 'title', 'summary', 'content', 'tags', 'prompt'
            content_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT,
            message_index INTEGER,
            word_count INTEGER,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
        CREATE INDEX IF NOT EXISTS idx_conversations_model ON conversations(model);
        CREATE INDEX IF NOT EXISTS idx_conversations_tags ON conversations(tags);
        CREATE INDEX IF NOT EXISTS idx_prompts_conversation_id ON prompts(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(prompt_category);
        CREATE INDEX IF NOT EXISTS idx_prompts_type ON prompts(prompt_type);
        CREATE INDEX IF NOT EXISTS idx_memory_index_content ON memory_index(content_text);
        CREATE INDEX IF NOT EXISTS idx_memory_index_hash ON memory_index(content_hash);
        """
        
        cursor = connection.cursor()
        cursor.executescript(schema_sql)
        connection.commit()
        logger.info("[OK] Database schema created/verified")
    
    def init_database(self, db_path: str) -> sqlite3.Connection:
        """
        Initialize the SQLite database with schema.
        
        Args:
            db_path: Path to SQLite database file
            
        Returns:
            SQLite connection object
        """
        try:
            # Allow same connection object across threads – LiveProcessor spawns worker threads.
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create tables if they don't exist
            self.create_schema(conn)
            logger.info(f"[OK] Memory database initialized: {db_path}")
            
            return conn
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory database: {e}")
            raise 