#!/usr/bin/env python3
"""
Initialize Database Script
=========================

Creates and initializes the database with the proper schema.
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the database with the proper schema."""
    db_path = "dreamos_memory.db"
    
    print(f"🔧 Initializing database: {db_path}")
    
    # Read the schema file
    schema_file = Path("core/database_schema.sql")
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Connect to database (this will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        
        # Execute the schema
        print("📋 Creating database schema...")
        conn.executescript(schema_sql)
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database initialized successfully!")
        print(f"📊 Created tables: {', '.join(tables)}")
        
        # Check if messages table exists
        if 'messages' in tables:
            print("✅ Messages table created successfully")
        else:
            print("❌ Messages table not found")
            return False
        
        # Check if conversations table exists
        if 'conversations' in tables:
            print("✅ Conversations table created successfully")
        else:
            print("❌ Conversations table not found")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def main():
    """Main function."""
    print("🗄️ Database Initialization")
    print("=" * 40)
    
    success = init_database()
    
    if success:
        print("\n✅ Database initialization completed successfully!")
        print("💡 You can now run the conversation statistics updater.")
    else:
        print("\n❌ Database initialization failed!")

if __name__ == "__main__":
    main() 