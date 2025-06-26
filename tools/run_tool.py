#!/usr/bin/env python3
"""
Simple script to run tools from the universal toolbelt database.
"""

import os
import sys

# Add the tools directory to the Python path
tools_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tools_dir)

from universal_toolbelt import ToolbeltManager

def main():
    if len(sys.argv) < 2:
        print("Usage: run_tool.py <tool_name> [args...]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    tool_args = sys.argv[2:]
    
    manager = ToolbeltManager()
    success = manager.run_tool(tool_name, tool_args)
    manager.close()
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 