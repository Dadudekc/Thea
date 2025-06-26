#!/usr/bin/env python3
"""
Test script for the original ChatGPT scraper
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.chatgpt_scraper import ChatGPTScraper

def main():
    print("🚀 Testing Original ChatGPT Scraper...")
    
    try:
        # Run scraper with non-headless mode
        with ChatGPTScraper(headless=False, timeout=30) as scraper:
            success = scraper.run_scraper(
                model="", 
                output_file="data/conversations/original_scraper_test.json"
            )
            
            if success:
                print("✅ Original scraper completed successfully!")
            else:
                print("❌ Original scraper failed")
                return 1
                
    except Exception as e:
        print(f"❌ Error running scraper: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 