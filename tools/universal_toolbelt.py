#!/usr/bin/env python3
"""
Universal Toolbelt - A CLI tool for managing and accessing Python utilities across projects.
"""

import sqlite3
import click
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
import json
import importlib.util
from typing import Optional, Dict, List
import tempfile

# Database setup
DB_PATH = os.path.expanduser("~/.dreamscape/toolbelt.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize the database with necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tools table stores the actual Python files
    c.execute('''CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        code TEXT NOT NULL,
        hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tags TEXT,  -- JSON array of tags
        metadata TEXT,  -- JSON object for additional metadata
        dependencies TEXT  -- JSON array of required packages
    )''')
    
    # Categories for organizing tools
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tool-Category relationships
    c.execute('''CREATE TABLE IF NOT EXISTS tool_categories (
        tool_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (tool_id, category_id),
        FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    )''')
    
    conn.commit()
    conn.close()

def get_file_hash(content: str) -> str:
    """Generate a hash for the file content."""
    return hashlib.sha256(content.encode()).hexdigest()

class ToolbeltManager:
    def __init__(self):
        init_db()
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._temp_files = []
    
    def close(self):
        """Close the database connection and cleanup temp files."""
        self.conn.close()
        for temp_file in self._temp_files:
            try:
                if Path(temp_file).exists():
                    os.remove(temp_file)
            except:
                pass
    
    def add_tool(self, name: str, file_path: str, description: str = "", tags: List[str] = None, 
                 category: str = None) -> bool:
        """Add a new tool to the database."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            code = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        code = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if code is None:
                click.echo(f"Error: Could not read file with any supported encoding", err=True)
                return False
            
            file_hash = get_file_hash(code)
            c = self.conn.cursor()
            
            # Check if tool already exists
            existing = c.execute("SELECT id, hash FROM tools WHERE name = ?", (name,)).fetchone()
            
            if existing:
                if existing['hash'] == file_hash:
                    click.echo(f"Tool '{name}' already exists with same content.")
                    return False
                else:
                    # Update existing tool
                    c.execute("""
                        UPDATE tools 
                        SET code = ?, hash = ?, description = ?, tags = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE name = ?
                    """, (code, file_hash, description, json.dumps(tags or []), name))
                    click.echo(f"Updated existing tool '{name}'")
            else:
                # Add new tool
                c.execute("""
                    INSERT INTO tools (name, code, hash, description, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (name, code, file_hash, description, json.dumps(tags or [])))
                click.echo(f"Added new tool '{name}'")
            
            self.conn.commit()
            return True
            
        except Exception as e:
            click.echo(f"Error adding tool: {str(e)}", err=True)
            return False
    
    def get_tool(self, name: str) -> Optional[Dict]:
        """Retrieve a tool by name."""
        c = self.conn.cursor()
        tool = c.execute("SELECT * FROM tools WHERE name = ?", (name,)).fetchone()
        if tool:
            return dict(tool)
        return None
    
    def list_tools(self, category: str = None, tag: str = None) -> List[Dict]:
        """List all tools, optionally filtered by category or tag."""
        c = self.conn.cursor()
        query = "SELECT name, description, tags FROM tools"
        params = []
        
        if category:
            query += """ 
                JOIN tool_categories tc ON tools.id = tc.tool_id 
                JOIN categories c ON tc.category_id = c.id 
                WHERE c.name = ?
            """
            params.append(category)
        elif tag:
            query += " WHERE tags LIKE ?"
            params.append(f"%{tag}%")
        
        tools = c.execute(query, params).fetchall()
        return [dict(tool) for tool in tools]
    
    def delete_tool(self, name: str) -> bool:
        """Delete a tool by name."""
        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM tools WHERE name = ?", (name,))
            self.conn.commit()
            return c.rowcount > 0
        except Exception as e:
            click.echo(f"Error deleting tool: {str(e)}", err=True)
            return False
    
    def run_tool(self, name: str, args: tuple = ()) -> bool:
        """Run a tool directly from the database with optional arguments."""
        try:
            # Get the tool code
            tool = self.get_tool(name)
            if not tool:
                click.echo(f"Tool '{name}' not found.", err=True)
                return False
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
                f.write(tool['code'])
                temp_path = f.name
                self._temp_files.append(temp_path)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(name, temp_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # Save original sys.argv and replace with our args
            orig_argv = sys.argv
            sys.argv = [name] + list(args)
            
            try:
                # Look for main function or cli
                if hasattr(module, 'main'):
                    module.main()
                elif hasattr(module, 'cli'):
                    module.cli()
                else:
                    click.echo("Warning: No main() or cli() function found in tool", err=True)
            finally:
                # Restore original sys.argv
                sys.argv = orig_argv
            
            return True
            
        except Exception as e:
            click.echo(f"Error running tool: {str(e)}", err=True)
            return False

# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """Universal Toolbelt - Manage your Python utilities across projects."""
    ctx.ensure_object(dict)

@cli.command()
@click.argument('name')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--description', '-d', help='Tool description', default="")
@click.option('--tag', '-t', multiple=True, help='Tags for categorizing the tool')
@click.option('--category', '-c', help='Category for the tool', default=None)
def add(name, file_path, description, tag, category):
    """Add a new tool to the toolbelt."""
    manager = ToolbeltManager()
    success = manager.add_tool(name, file_path, description, list(tag), category)
    manager.close()
    if not success:
        sys.exit(1)

@cli.command()
@click.argument('name')
def get(name):
    """Retrieve a tool by name."""
    manager = ToolbeltManager()
    tool = manager.get_tool(name)
    manager.close()
    
    if tool:
        click.echo(f"Name: {tool['name']}")
        click.echo(f"Description: {tool['description']}")
        click.echo(f"Tags: {tool['tags']}")
        click.echo("\nCode:")
        click.echo(tool['code'])
    else:
        click.echo(f"Tool '{name}' not found.", err=True)
        sys.exit(1)

@cli.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--tag', '-t', help='Filter by tag')
def list(category, tag):
    """List all available tools."""
    manager = ToolbeltManager()
    tools = manager.list_tools(category, tag)
    manager.close()
    
    if not tools:
        click.echo("No tools found.")
        return
    
    for tool in tools:
        click.echo(f"\n{tool['name']}")
        if tool['description']:
            click.echo(f"  Description: {tool['description']}")
        if tool['tags']:
            tags = json.loads(tool['tags'])
            if tags:
                click.echo(f"  Tags: {', '.join(tags)}")

@cli.command()
@click.argument('name')
def delete(name):
    """Delete a tool by name."""
    manager = ToolbeltManager()
    if manager.delete_tool(name):
        click.echo(f"Tool '{name}' deleted successfully.")
    else:
        click.echo(f"Failed to delete tool '{name}'.", err=True)
        sys.exit(1)
    manager.close()

@cli.command()
@click.argument('name')
@click.argument('output_path', type=click.Path())
def export(name, output_path):
    """Export a tool to a Python file."""
    manager = ToolbeltManager()
    tool = manager.get_tool(name)
    manager.close()
    
    if not tool:
        click.echo(f"Tool '{name}' not found.", err=True)
        sys.exit(1)
    
    try:
        with open(output_path, 'w') as f:
            f.write(tool['code'])
        click.echo(f"Tool exported to {output_path}")
    except Exception as e:
        click.echo(f"Error exporting tool: {str(e)}", err=True)
        sys.exit(1)

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('name')
@click.pass_context
def run(ctx, name):
    """Run a tool directly from the database with optional arguments."""
    manager = ToolbeltManager()
    success = manager.run_tool(name, ctx.args)
    manager.close()
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    cli()