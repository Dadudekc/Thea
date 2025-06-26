#!/usr/bin/env python3
"""
A simple test tool to demonstrate running from the toolbelt database.
"""

import sys

def main():
    """Simple test tool that says hello."""
    name = "World"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    
    print(f"Hello, {name}!")
    print("This tool is running directly from the toolbelt database!")
    print(f"Arguments received: {sys.argv[1:]}")

if __name__ == '__main__':
    main()