#!/usr/bin/env python3
"""
Dreamscape Processor
===================

Handles the processing of dreamscape prompts and memory continuity.
Manages the MMORPG storyline progression and memory transfer between conversations.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from core.dreamscape_memory import DreamscapeMemory
from core.template_engine import render_template
from core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class DreamscapeProcessor:
    """
    Processes dreamscape prompts and manages memory continuity.
    Handles the MMORPG storyline progression across conversations.
    """
    
    def __init__(self):
        self.dreamscape_memory = DreamscapeMemory()
        self.memory_manager = MemoryManager()
        
    def process_conversation_for_dreamscape(self, conversation_id: str, conversation_content: str) -> Dict[str, Any]:
        """
        Process a conversation and extract dreamscape-relevant information.
        
        Args:
            conversation_id: ID of the conversation
            conversation_content: Full conversation content
            
        Returns:
            Dictionary containing dreamscape analysis and memory updates
        """
        try:
            # Get current memory state
            current_state = self.dreamscape_memory.get_current_memory_state()
            
            # Create context for dreamscape template
            context = {
                "CURRENT_MEMORY_STATE": json.dumps(current_state, indent=2),
                "conversation_content": conversation_content,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Render the dreamscape template
            dreamscape_prompt = render_template("dreamscape.j2", context)
            
            # For now, we'll simulate the AI response
            # In a real implementation, this would be sent to ChatGPT
            simulated_response = self._simulate_dreamscape_response(conversation_content, current_state)
            
            # Extract memory updates from the response
            memory_updates = self._extract_memory_updates(simulated_response)
            
            # Update dreamscape memory
            if memory_updates:
                self.dreamscape_memory.update_memory_state(
                    conversation_id, 
                    memory_updates, 
                    simulated_response.get('narrative', '')
                )
            
            return {
                "success": True,
                "dreamscape_prompt": dreamscape_prompt,
                "ai_response": simulated_response,
                "memory_updates": memory_updates,
                "current_state": current_state
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process conversation for dreamscape: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_conversations_chronological(self, limit: int = None) -> Dict:
        """
        Process conversations in chronological order (oldest first).
        
        Args:
            limit: Maximum number of conversations to process (None for all)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Get all conversations in chronological order
            conversations = self.memory_manager.get_conversations_chronological(limit=limit)
            total_conversations = self.memory_manager.get_conversations_count()
            
            if not conversations:
                return {
                    "success": True,
                    "processed_count": 0,
                    "total_conversations": total_conversations,
                    "message": "No conversations to process"
                }
            
            logger.info(f"[PROCESSING] Processing {len(conversations)} conversations in chronological order")
            
            processed_count = 0
            errors = []
            
            for i, conversation in enumerate(conversations, 1):
                try:
                    logger.info(f"[PROCESSING] Processing conversation {i}/{len(conversations)}: {conversation.get('title', 'Untitled')}")
                    
                    # Process the conversation
                    result = self.process_conversation_for_dreamscape(
                        conversation['id'],
                        conversation.get('content', '')
                    )
                    
                    if result.get('success'):
                        processed_count += 1
                        logger.info(f"[OK] Successfully processed: {conversation.get('title', 'Untitled')}")
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        errors.append(f"Conversation {conversation.get('title', 'Untitled')}: {error_msg}")
                        logger.error(f"[ERROR] Failed to process: {conversation.get('title', 'Untitled')} - {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Exception processing conversation: {e}"
                    errors.append(f"Conversation {conversation.get('title', 'Untitled')}: {error_msg}")
                    logger.error(f"[ERROR] {error_msg}")
            
            logger.info(f"[COMPLETED] Completed processing {processed_count}/{len(conversations)} conversations")
            
            return {
                "success": True,
                "processed_count": processed_count,
                "total_conversations": total_conversations,
                "conversations_processed": len(conversations),
                "errors": errors,
                "message": f"Processed {processed_count} out of {len(conversations)} conversations"
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to process conversations chronologically: {e}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "total_conversations": 0
            }
    
    def _simulate_dreamscape_response(self, conversation_content: str, current_state: Dict) -> Dict[str, Any]:
        """
        Simulate an AI response to the dreamscape prompt.
        In a real implementation, this would be sent to ChatGPT.
        """
        # Analyze conversation content for dreamscape elements
        content_lower = conversation_content.lower()
        
        # Extract potential quests, skills, and domains
        quests = self._extract_quests_from_content(content_lower)
        skills = self._extract_skills_from_content(content_lower)
        domains = self._extract_domains_from_content(content_lower)
        
        # Generate narrative
        narrative = self._generate_narrative(conversation_content, quests, skills, domains)
        
        # Emit DSUpdate event for storyline chunk
        try:
            from core.models import DSUpdate
            from core.discord_bridge import DiscordBridge

            # Lazy, singleton-ish bridge (reuse across calls)
            if not hasattr(self, "_bridge"):
                self._bridge = DiscordBridge()
            update = DSUpdate(kind="story", msg=narrative)
            # Non-blocking dispatch (safe if Discord inactive)
            self._bridge.handle_sync(update)
        except Exception as _e:
            # Soft-fail: never break processing if bridge not available
            logger.debug(f"DSUpdate emit skipped: {_e}")
        
        # Generate memory updates
        memory_updates = {
            "skill_level_advancements": skills,
            "newly_stabilized_domains": domains,
            "newly_unlocked_protocols": [],
            "quest_completions": [],
            "new_quests_accepted": quests,
            "architect_tier_progression": {
                "current_tier": current_state.get("architect_tier", "Tier 1 - Novice"),
                "progress_to_next_tier": min(current_state.get("tier_progress", 0.0) + 5.0, 100.0)
            }
        }
        
        return {
            "narrative": narrative,
            "memory_updates": memory_updates
        }
    
    def _extract_quests_from_content(self, content: str) -> List[str]:
        """Extract potential quests from conversation content."""
        quests = []
        
        # Look for quest-like patterns
        quest_patterns = [
            r"build(?:ing)?\s+(\w+)",
            r"create(?:ing)?\s+(\w+)",
            r"implement(?:ing)?\s+(\w+)",
            r"fix(?:ing)?\s+(\w+)",
            r"optimize(?:ing)?\s+(\w+)",
            r"test(?:ing)?\s+(\w+)",
            r"deploy(?:ing)?\s+(\w+)",
            r"integrate(?:ing)?\s+(\w+)"
        ]
        
        for pattern in quest_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                quest_name = f"{match.title()} Implementation"
                if quest_name not in quests:
                    quests.append(quest_name)
        
        return quests[:3]  # Limit to 3 quests
    
    def _extract_skills_from_content(self, content: str) -> Dict[str, str]:
        """Extract skill advancements from conversation content."""
        skills = {}
        
        # Look for skill-related content
        skill_keywords = {
            "System Convergence": ["system", "architecture", "design", "convergence"],
            "Execution Velocity": ["speed", "performance", "optimization", "velocity"],
            "Strategic Intelligence": ["strategy", "planning", "intelligence", "analysis"]
        }
        
        for skill_name, keywords in skill_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    # Simulate skill advancement
                    current_level = 1
                    if skill_name in skills:
                        current_level = int(skills[skill_name].split('/')[0]) + 1
                    skills[skill_name] = f"{current_level}/100"
                    break
        
        return skills
    
    def _extract_domains_from_content(self, content: str) -> List[str]:
        """Extract stabilized domains from conversation content."""
        domains = []
        
        # Look for domain-related content
        domain_keywords = [
            "database", "api", "gui", "scraping", "memory", "template",
            "discord", "automation", "testing", "deployment"
        ]
        
        for keyword in domain_keywords:
            if keyword in content:
                domain_name = f"{keyword.title()} Domain"
                if domain_name not in domains:
                    domains.append(domain_name)
        
        return domains[:2]  # Limit to 2 domains
    
    def _generate_narrative(self, content: str, quests: List[str], skills: Dict[str, str], domains: List[str]) -> str:
        """Generate a narrative based on the conversation content."""
        narrative_parts = []
        
        if quests:
            narrative_parts.append(f"Victor embarked on new quests: {', '.join(quests)}")
        
        if skills:
            skill_text = ", ".join([f"{skill} to level {level.split('/')[0]}" for skill, level in skills.items()])
            narrative_parts.append(f"Skills advanced: {skill_text}")
        
        if domains:
            narrative_parts.append(f"New domains stabilized: {', '.join(domains)}")
        
        if not narrative_parts:
            narrative_parts.append("Victor continued his journey through The Dreamscape")
        
        narrative = ". ".join(narrative_parts) + "."
        narrative += " The Architect's Edge pulses, resonant with Victor's will, whispering a challenge: 'Beyond clarity lies true mastery... are you prepared to ascend?'"
        
        return narrative
    
    def _extract_memory_updates(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract memory updates from the AI response."""
        try:
            # Look for JSON block in the response
            narrative = response.get('narrative', '')
            
            # Try to find JSON in the narrative
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', narrative, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # If no JSON found, use the memory_updates from the response
            return response.get('memory_updates')
            
        except Exception as e:
            logger.error(f"❌ Failed to extract memory updates: {e}")
            return None
    
    def get_storyline_progression(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the storyline progression in chronological order."""
        return self.dreamscape_memory.get_storyline_progression(limit)
    
    def get_current_memory_state(self) -> Dict[str, Any]:
        """Get the current memory state."""
        return self.dreamscape_memory.get_current_memory_state()
    
    def generate_dreamscape_prompt(self, conversation_content: str) -> str:
        """Generate a dreamscape prompt for a conversation."""
        try:
            current_state = self.dreamscape_memory.get_current_memory_state()
            
            context = {
                "CURRENT_MEMORY_STATE": json.dumps(current_state, indent=2),
                "conversation_content": conversation_content
            }
            
            return render_template("dreamscape.j2", context)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate dreamscape prompt: {e}")
            return ""
    
    def close(self):
        """Close database connections."""
        self.dreamscape_memory.close()
        self.memory_manager.close()

def main():
    """Test the dreamscape processor."""
    processor = DreamscapeProcessor()
    
    # Test conversation processing
    test_conversation = """
    I'm working on implementing a memory manager for the Dream.OS system.
    The system needs to handle conversation storage and retrieval efficiently.
    I'm also optimizing the GUI performance and fixing some import issues.
    The database schema looks good and the API is working well.
    """
    
    result = processor.process_conversation_for_dreamscape("test_conv_1", test_conversation)
    
    print("Dreamscape Processing Result:")
    print(json.dumps(result, indent=2))
    
    # Test storyline progression
    progression = processor.get_storyline_progression(5)
    print(f"\nStoryline Progression ({len(progression)} entries):")
    for entry in progression:
        print(f"- {entry.get('title', 'N/A')} ({entry.get('architect_tier', 'N/A')})")
    
    processor.close()

if __name__ == "__main__":
    main() 