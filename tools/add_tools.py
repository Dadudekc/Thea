#!/usr/bin/env python3
"""
Helper script to add tools to the universal toolbelt.
"""

import os
import sys
from universal_toolbelt import ToolbeltManager

def add_tool(name, file_path, description, tags, category):
    manager = ToolbeltManager()
    success = manager.add_tool(name, file_path, description, tags, category)
    manager.close()
    return success

# Add our core tools
tools_to_add = [
    # Core Infrastructure
    {
        "name": "universal_toolbelt",
        "file_path": "tools/universal_toolbelt.py",
        "description": "Central tool management system for storing and running Python utilities",
        "tags": ["core", "management", "database"],
        "category": "core"
    },
    {
        "name": "dreamos_cli",
        "file_path": "tools/dreamos_cli.py",
        "description": "Main CLI interface for Dream.OS operations",
        "tags": ["core", "cli"],
        "category": "core"
    },
    
    # CLI Tools
    {
        "name": "scraper_cli",
        "file_path": "tools/scraper_cli.py",
        "description": "Advanced CLI for scraping operations",
        "tags": ["scraping", "cli"],
        "category": "cli"
    },
    {
        "name": "simple_scraper_cli",
        "file_path": "tools/simple_scraper_cli.py",
        "description": "Simplified scraping interface",
        "tags": ["scraping", "cli"],
        "category": "cli"
    },
    {
        "name": "run_tool",
        "file_path": "tools/run_tool.py",
        "description": "Tool runner for database-stored utilities",
        "tags": ["utility", "runner"],
        "category": "cli"
    },
    {
        "name": "simple_runner",
        "file_path": "tools/simple_runner.py",
        "description": "Simplified tool runner",
        "tags": ["utility", "runner"],
        "category": "cli"
    },
    
    # Setup & Configuration
    {
        "name": "discord_wizard",
        "file_path": "tools/discord_wizard.py",
        "description": "Interactive Discord bot setup and configuration",
        "tags": ["discord", "setup"],
        "category": "setup"
    },
    
    # Development Tools
    {
        "name": "module_generator",
        "file_path": "tools/module_generator.py",
        "description": "Generates new modules with proper structure and boilerplate",
        "tags": ["generator", "utility"],
        "category": "development"
    },
    {
        "name": "add_tools",
        "file_path": "tools/add_tools.py",
        "description": "Tool for adding utilities to the toolbelt database",
        "tags": ["utility", "database"],
        "category": "development"
    },
    
    # Utility Tools
    {
        "name": "hello_tool",
        "file_path": "tools/hello_tool.py",
        "description": "Example tool demonstrating toolbelt functionality",
        "tags": ["demo", "example"],
        "category": "utility"
    }
]

def main():
    success_count = 0
    for tool in tools_to_add:
        if os.path.exists(tool["file_path"]):
            if add_tool(
                tool["name"],
                tool["file_path"],
                tool["description"],
                tool["tags"],
                tool["category"]
            ):
                success_count += 1
                print(f"Successfully added {tool['name']}")
        else:
            print(f"Warning: File not found - {tool['file_path']}")
    
    print(f"\nAdded {success_count} out of {len(tools_to_add)} tools")

if __name__ == "__main__":
    main() 