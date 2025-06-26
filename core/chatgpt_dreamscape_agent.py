"""
ChatGPT Dreamscape Agent
=======================

Integrates ChatGPT with the Dreamscape system for AI-driven narrative and memory processing.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.dreamscape_processor import DreamscapeProcessor
from core.dreamscape_memory import DreamscapeMemory
from core.template_engine import render_template
from scrapers.chatgpt_scraper import ChatGPTScraper
from scrapers.prompt_interactor import PromptInteractor

logger = logging.getLogger(__name__)

class ChatGPTDreamscapeAgent:
    """Handles ChatGPT integration with the Dreamscape system."""
    
    def __init__(self):
        """Initialize the ChatGPT Dreamscape agent."""
        self.dreamscape_processor = DreamscapeProcessor()
        self.dreamscape_memory = DreamscapeMemory()
        self.prompt_interactor = PromptInteractor()
        
        # Initialize scraper with undetected mode
        self.scraper = ChatGPTScraper(
            headless=False,
            use_undetected=True
        )
    
    def process_conversation_with_ai(self, conversation_id: str, conversation_content: str) -> Dict[str, Any]:
        """
        Process a conversation using ChatGPT for narrative generation and memory updates.
        
        Args:
            conversation_id: ID of the conversation
            conversation_content: Full conversation content
            
        Returns:
            Dictionary containing AI analysis and memory updates
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
            
            # Send to ChatGPT and get response
            with self.scraper:
                if not self.scraper.create_new_conversation():
                    raise Exception("Failed to create new conversation")
                
                if not self.prompt_interactor.send_prompt(
                    self.scraper.driver,
                    dreamscape_prompt,
                    wait_for_response=True
                ):
                    raise Exception("Failed to send prompt")
                
                # Get the response
                ai_response = self.prompt_interactor.get_last_response(self.scraper.driver)
                
                if not ai_response:
                    raise Exception("No response received from ChatGPT")
                
                # Extract memory updates from the response
                memory_updates = self._extract_memory_updates(ai_response)
                
                # Update dreamscape memory
                if memory_updates:
                    self.dreamscape_memory.update_memory_state(
                        conversation_id,
                        memory_updates,
                        ai_response
                    )
                
                return {
                    "success": True,
                    "dreamscape_prompt": dreamscape_prompt,
                    "ai_response": ai_response,
                    "memory_updates": memory_updates,
                    "current_state": current_state
                }
                
        except Exception as e:
            logger.error(f"Failed to process conversation with AI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query_dreamscape_ai(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a direct query to the Dreamscape AI.
        
        Args:
            query: The query to send
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary containing the AI response and any memory updates
        """
        try:
            # Get current memory state
            current_state = self.dreamscape_memory.get_current_memory_state()
            
            # Create context
            context = {
                "CURRENT_MEMORY_STATE": json.dumps(current_state, indent=2),
                "query": query,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Render query template
            query_prompt = render_template("dreamscape_query.j2", context)
            
            # Send to ChatGPT
            with self.scraper:
                if not self.scraper.create_new_conversation():
                    raise Exception("Failed to create new conversation")
                
                if not self.prompt_interactor.send_prompt(
                    self.scraper.driver,
                    query_prompt,
                    wait_for_response=True
                ):
                    raise Exception("Failed to send query")
                
                # Get the response
                ai_response = self.prompt_interactor.get_last_response(self.scraper.driver)
                
                if not ai_response:
                    raise Exception("No response received from ChatGPT")
                
                # Extract memory updates
                memory_updates = self._extract_memory_updates(ai_response)
                
                # Update memory if needed
                if memory_updates and conversation_id:
                    self.dreamscape_memory.update_memory_state(
                        conversation_id,
                        memory_updates,
                        ai_response
                    )
                
                return {
                    "success": True,
                    "query": query,
                    "ai_response": ai_response,
                    "memory_updates": memory_updates,
                    "current_state": current_state
                }
                
        except Exception as e:
            logger.error(f"Failed to query Dreamscape AI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_memory_updates(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract memory updates from the AI response."""
        try:
            # Look for JSON block in the response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find a MEMORY_UPDATE section
            memory_section = re.search(r'MEMORY_UPDATE\s*(\{.*?\})', response, re.DOTALL)
            if memory_section:
                return json.loads(memory_section.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract memory updates: {e}")
            return None
    
    def close(self):
        """Close connections and cleanup."""
        self.dreamscape_memory.close()
        self.dreamscape_processor.close()
        if self.scraper:
            self.scraper.close()