#!/usr/bin/env python3
"""
Script to create conversations.json from extracted conversation files.
This will be used by the Multi-Model Prompt Agent.
"""

import json
import os
from pathlib import Path

def create_conversations_json():
    """Create conversations.json from extracted conversation files."""
    
    conversations_dir = Path("data/conversations")
    conversations = []
    
    # Find all conversation JSON files (excluding summary files)
    for conv_file in conversations_dir.glob("*.json"):
        if "extraction_summary" in conv_file.name:
            continue
            
        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                
            # Extract conversation ID from filename
            # Format: Title_ConversationID.json
            filename = conv_file.stem
            if "_" in filename:
                # Find the last underscore which should be before the conversation ID
                parts = filename.split("_")
                if len(parts) >= 2:
                    # The last part should be the conversation ID
                    conv_id = parts[-1]
                    title = "_".join(parts[:-1])  # Everything before the last underscore
                else:
                    conv_id = filename
                    title = filename
            else:
                conv_id = filename
                title = filename
            
            # Create conversation entry
            conversation = {
                "id": conv_id,
                "title": title,
                "url": f"https://chat.openai.com/c/{conv_id}",
                "timestamp": conv_data.get("timestamp", ""),
                "captured_at": conv_data.get("captured_at", ""),
                "file_path": str(conv_file)
            }
            
            conversations.append(conversation)
            print(f"✅ Added: {title} (ID: {conv_id})")
            
        except Exception as e:
            print(f"❌ Error processing {conv_file.name}: {e}")
    
    # Save to conversations.json
    with open("conversations.json", 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Created conversations.json with {len(conversations)} conversations")
    print("📁 File saved: conversations.json")
    
    return conversations

if __name__ == "__main__":
    create_conversations_json() 