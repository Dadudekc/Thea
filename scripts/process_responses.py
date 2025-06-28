#!/usr/bin/env python3
"""
scripts/process_responses.py

Process saved ChatGPT responses and integrate them with MMORPG and devlog systems.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mmorpg_engine import MMORPGEngine
from core.discord_manager import DiscordManager

class ResponseProcessor:
    """Process saved responses and integrate with various systems."""
    
    def __init__(self):
        self.mmorpg_engine = MMORPGEngine()
        self.discord_manager = DiscordManager()
    
    def load_responses(self, response_dir: str = "outputs/responses") -> Dict[str, List[Dict]]:
        """Load all response files from the specified directory."""
        responses = {}
        
        if not os.path.exists(response_dir):
            print(f"❌ Response directory not found: {response_dir}")
            return responses
        
        for file in os.listdir(response_dir):
            if file.endswith('.json') and 'responses_' in file:
                filepath = os.path.join(response_dir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        response_type = data.get('type', 'unknown')
                        responses[response_type] = data.get('responses', [])
                    print(f"📂 Loaded {len(data.get('responses', []))} {response_type} responses from {file}")
                except Exception as e:
                    print(f"❌ Error loading {file}: {e}")
        
        return responses
    
    def process_mmorpg_responses(self, responses: Dict[str, List[Dict]]):
        """Process responses for MMORPG integration."""
        print("⚔️ Processing MMORPG responses...")
        
        # Process dreamscape responses for quest generation
        dreamscape_responses = responses.get('dreamscape', [])
        for resp in dreamscape_responses:
            try:
                # Extract conversation ID and generate quest
                conv_id = resp.get('conversation_id', 'unknown')
                narrative = resp.get('response', '')
                
                # Generate quest from the narrative
                quest = self.mmorpg_engine.generate_quest_from_conversation(
                    conv_id, narrative
                )
                
                if quest:
                    print(f"🗡️ Generated quest: {quest.title}")
                    
                    # Send Discord notification
                    try:
                        msg = f"🎯 New quest available: **{quest.title}**\n{quest.description[:200]}..."
                        self.discord_manager.send_message_sync(msg)
                    except Exception as e:
                        print(f"⚠️ Discord notification failed: {e}")
                
            except Exception as e:
                print(f"❌ Error processing dreamscape response: {e}")
        
        # Process conversation analyzer for skill advancement
        analyzer_responses = responses.get('conversation_analyzer', [])
        for resp in analyzer_responses:
            try:
                analysis = resp.get('response', '')
                conv_id = resp.get('conversation_id', 'unknown')
                
                # Award XP based on analysis complexity
                xp_award = min(50, len(analysis) // 10)  # 1 XP per 10 characters, max 50
                
                if xp_award > 0:
                    from mmorpg.xp_dispatcher import XPDispatcher
                    XPDispatcher(self.mmorpg_engine).dispatch(
                        xp_award,
                        source="conversation_analysis"
                    )
                    print(f"💎 Awarded {xp_award} XP for conversation analysis")
                
            except Exception as e:
                print(f"❌ Error processing analyzer response: {e}")
    
    def process_devlog_responses(self, responses: Dict[str, List[Dict]]):
        """Process responses for devlog generation."""
        print("📝 Processing devlog responses...")
        
        devlog_entries = []
        
        # Process project summaries
        summary_responses = responses.get('project_summary', [])
        for resp in summary_responses:
            try:
                summary = resp.get('response', '')
                conv_id = resp.get('conversation_id', 'unknown')
                
                devlog_entries.append({
                    'type': 'project_update',
                    'conversation_id': conv_id,
                    'content': summary,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error processing project summary: {e}")
        
        # Process code reviews
        review_responses = responses.get('code_review', [])
        for resp in review_responses:
            try:
                review = resp.get('response', '')
                conv_id = resp.get('conversation_id', 'unknown')
                
                devlog_entries.append({
                    'type': 'code_review',
                    'conversation_id': conv_id,
                    'content': review,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error processing code review: {e}")
        
        # Save devlog entries
        if devlog_entries:
            devlog_file = f"outputs/devlog_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(devlog_file, 'w', encoding='utf-8') as f:
                json.dump(devlog_entries, f, indent=2, ensure_ascii=False)
            print(f"📄 Devlog entries saved to {devlog_file}")
            
            # Send Discord notification
            try:
                msg = f"📝 Generated {len(devlog_entries)} devlog entries from AI responses"
                self.discord_manager.send_message_sync(msg)
            except Exception as e:
                print(f"⚠️ Discord notification failed: {e}")
    
    def generate_summary_report(self, responses: Dict[str, List[Dict]]):
        """Generate a summary report of all processed responses."""
        print("📊 Generating summary report...")
        
        total_responses = sum(len(resps) for resps in responses.values())
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_responses': total_responses,
            'response_types': {
                response_type: len(resps) for response_type, resps in responses.items()
            },
            'processing_summary': {
                'mmorpg_quests_generated': len(responses.get('dreamscape', [])),
                'skill_advancements': len(responses.get('conversation_analyzer', [])),
                'devlog_entries': len(responses.get('project_summary', [])) + len(responses.get('code_review', [])),
            }
        }
        
        # Save report
        report_file = f"outputs/processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Processing report saved to {report_file}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total responses processed: {total_responses}")
        print(f"MMORPG quests generated: {report['processing_summary']['mmorpg_quests_generated']}")
        print(f"Skill advancements: {report['processing_summary']['skill_advancements']}")
        print(f"Devlog entries: {report['processing_summary']['devlog_entries']}")
        print(f"{'='*60}")

def main():
    """Main processing function."""
    print("🚀 Starting response processing...")
    
    processor = ResponseProcessor()
    
    # Load responses
    responses = processor.load_responses()
    
    if not responses:
        print("❌ No responses found to process")
        return
    
    # Process MMORPG responses
    processor.process_mmorpg_responses(responses)
    
    # Process devlog responses
    processor.process_devlog_responses(responses)
    
    # Generate summary report
    processor.generate_summary_report(responses)
    
    print("✅ Response processing complete!")

if __name__ == "__main__":
    main() 