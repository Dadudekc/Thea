#!/usr/bin/env python3
"""
ChatGPT API Client - Live conversation integration for Dream.OS
Handles real-time conversation fetching and processing.
"""

import os
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import aiohttp
import json

logger = logging.getLogger(__name__)

class ChatGPTAPIClient:
    """Client for interacting with ChatGPT API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.rate_limit_delay = 1.0  # Delay between requests
        self.max_retries = 3
        self.session = None
        
        if not self.api_key:
            logger.warning("No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_conversations(self, limit: int = 50, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch recent conversations from ChatGPT.
        
        Args:
            limit: Maximum number of conversations to fetch
            since: Only fetch conversations since this datetime
            
        Returns:
            List of conversation dictionaries
        """
        if not self.api_key:
            logger.error("Cannot fetch conversations: No API key configured")
            return []
        
        try:
            # Note: This is a placeholder implementation
            # The actual ChatGPT API doesn't provide direct access to conversation history
            # This would need to be implemented through web scraping or other methods
            
            logger.info(f"Fetching up to {limit} conversations from ChatGPT")
            
            # Simulate API call with rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # Return mock data for now
            # In production, this would integrate with actual ChatGPT data
            conversations = []
            for i in range(min(limit, 10)):
                conversations.append({
                    "id": f"conv_{int(time.time())}_{i}",
                    "title": f"Mock Conversation {i+1}",
                    "created_at": datetime.now() - timedelta(hours=i),
                    "updated_at": datetime.now() - timedelta(minutes=i*30),
                    "message_count": 10 + i,
                    "content": f"This is mock conversation content {i+1} for testing purposes."
                })
            
            logger.info(f"Successfully fetched {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to fetch conversations: {e}")
            return []
    
    async def get_conversation_details(self, conversation_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            Conversation details or None if not found
        """
        if not self.api_key:
            logger.error("Cannot fetch conversation details: No API key configured")
            return None
        
        try:
            logger.info(f"Fetching details for conversation: {conversation_id}")
            
            # Simulate API call
            await asyncio.sleep(self.rate_limit_delay)
            
            # Return mock conversation details
            return {
                "id": conversation_id,
                "title": f"Detailed Conversation: {conversation_id}",
                "created_at": datetime.now() - timedelta(hours=1),
                "updated_at": datetime.now(),
                "message_count": 15,
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
                    {"role": "user", "content": "Can you help me with a project?"},
                    {"role": "assistant", "content": "Of course! I'd be happy to help with your project."}
                ],
                "content": "This is a detailed conversation about a project that needs assistance."
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch conversation details: {e}")
            return None
    
    async def send_message(self, conversation_id: str, message: str) -> Optional[Dict]:
        """
        Send a message to a ChatGPT conversation.
        
        Args:
            conversation_id: The conversation ID
            message: The message to send
            
        Returns:
            Response from ChatGPT or None if failed
        """
        if not self.api_key:
            logger.error("Cannot send message: No API key configured")
            return None
        
        try:
            logger.info(f"Sending message to conversation: {conversation_id}")
            
            # Prepare the request payload
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make the API request
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Message sent successfully")
                    return data
                else:
                    logger.error(f"Failed to send message: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Check if the API client is properly configured."""
        return bool(self.api_key)
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information."""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 150000,
            "current_delay": self.rate_limit_delay
        }

class ConversationMonitor:
    """Monitors for new conversations and triggers processing."""
    
    def __init__(self, api_client: ChatGPTAPIClient, memory_manager, dreamscape_processor):
        self.api_client = api_client
        self.memory_manager = memory_manager
        self.dreamscape_processor = dreamscape_processor
        self.is_monitoring = False
        self.monitor_interval = 300  # 5 minutes
        self.last_check = None
    
    async def start_monitoring(self):
        """Start monitoring for new conversations."""
        if not self.api_client.is_configured():
            logger.error("Cannot start monitoring: API client not configured")
            return
        
        self.is_monitoring = True
        logger.info("Starting conversation monitoring...")
        
        while self.is_monitoring:
            try:
                await self.check_for_new_conversations()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in conversation monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_monitoring(self):
        """Stop monitoring for new conversations."""
        self.is_monitoring = False
        logger.info("Stopped conversation monitoring")
    
    async def check_for_new_conversations(self):
        """Check for new conversations and process them."""
        try:
            # Get recent conversations
            conversations = await self.api_client.get_conversations(limit=20)
            
            if not conversations:
                return
            
            # Filter for new conversations (since last check)
            new_conversations = []
            for conv in conversations:
                if not self.last_check or conv['updated_at'] > self.last_check:
                    new_conversations.append(conv)
            
            if new_conversations:
                logger.info(f"Found {len(new_conversations)} new conversations")
                
                # Process new conversations
                for conv in new_conversations:
                    await self.process_conversation(conv)
                
                # Update last check time
                self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking for new conversations: {e}")
    
    async def process_conversation(self, conversation: Dict):
        """Process a single conversation through the dreamscape system."""
        try:
            logger.info(f"Processing conversation: {conversation.get('title', 'Untitled')}")
            
            # Store conversation in memory
            conversation_id = self.memory_manager.store_conversation(conversation)
            
            # Process through dreamscape
            result = self.dreamscape_processor.process_single_conversation(conversation_id)
            
            if result.get('success'):
                logger.info(f"Successfully processed conversation: {conversation.get('title')}")
            else:
                logger.error(f"Failed to process conversation: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")

# Global API client instance
chatgpt_client = ChatGPTAPIClient() 