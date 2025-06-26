#!/usr/bin/env python3
import sqlite3

def check_database():
    conn = sqlite3.connect('data/dreamos_memory.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check conversation count
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cursor.fetchone()[0]
    print(f"\nConversations in database: {conv_count}")
    
    # Check if messages table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM messages")
        msg_count = cursor.fetchone()[0]
        print(f"Messages in database: {msg_count}")
    else:
        print("Messages table does not exist")
    
    conn.close()

if __name__ == "__main__":
    check_database() 