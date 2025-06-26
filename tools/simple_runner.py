#!/usr/bin/env python3
"""
Simple script to run tools from the universal toolbelt database.
"""

import os
import sys
import sqlite3
import tempfile
import importlib.util

# Database setup
DB_PATH = os.path.expanduser("~/.dreamscape/toolbelt.db")

def get_tool_code(name):
    """Get tool code from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    tool = c.execute("SELECT code FROM tools WHERE name = ?", (name,)).fetchone()
    conn.close()
    
    if tool:
        return tool['code']
    return None

def run_tool(name, args):
    """Run a tool directly from the database."""
    code = get_tool_code(name)
    if not code:
        print(f"Tool '{name}' not found.")
        return False
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(name, temp_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        
        # Save original sys.argv and replace with our args
        orig_argv = sys.argv
        sys.argv = [name] + args
        
        try:
            if hasattr(module, 'main'):
                module.main()
            else:
                print("Warning: No main() function found in tool")
        finally:
            sys.argv = orig_argv
        
        return True
    
    except Exception as e:
        print(f"Error running tool: {str(e)}")
        return False
    
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: simple_runner.py <tool_name> [args...]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    tool_args = sys.argv[2:]
    
    if not run_tool(tool_name, tool_args):
        sys.exit(1)

if __name__ == '__main__':
    main() 