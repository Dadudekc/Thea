#!/usr/bin/env python3
"""
Live Processor - Continuous conversation processing pipeline
Handles real-time conversation monitoring and dreamscape processing.
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from core.chatgpt_api_client import ChatGPTAPIClient, ConversationMonitor
from core.memory_manager import MemoryManager
from core.dreamscape_processor import DreamscapeProcessor
from core.mmorpg_engine import MMORPGEngine
from core.discord_manager import DiscordManager

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status enumeration."""
    IDLE = "idle"
    MONITORING = "monitoring"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class ProcessingStats:
    """Statistics for the live processing system."""
    total_conversations_processed: int = 0
    conversations_processed_today: int = 0
    last_processing_time: Optional[datetime] = None
    average_processing_time: float = 0.0
    errors_count: int = 0
    start_time: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.IDLE

class LiveProcessor:
    """Main live processing system for Dream.OS."""
    
    def __init__(self, 
                 memory_manager: MemoryManager,
                 dreamscape_processor: DreamscapeProcessor,
                 mmorpg_engine: MMORPGEngine,
                 discord_manager: Optional[DiscordManager] = None):
        
        self.memory_manager = memory_manager
        self.dreamscape_processor = dreamscape_processor
        self.mmorpg_engine = mmorpg_engine
        self.discord_manager = discord_manager
        
        # Initialize API client and monitor
        self.api_client = ChatGPTAPIClient()
        self.conversation_monitor = ConversationMonitor(
            self.api_client, 
            self.memory_manager, 
            self.dreamscape_processor
        )
        
        # Processing state
        self.is_running = False
        self.processing_thread = None
        self.stats = ProcessingStats()
        
        # Callbacks for status updates
        self.status_callbacks: List[Callable] = []
        self.progress_callbacks: List[Callable] = []
        
        # Configuration
        self.monitor_interval = 300  # 5 minutes
        self.batch_size = 10
        self.max_processing_time = 300  # 5 minutes per batch
    
    def start(self) -> bool:
        """Start the live processing system."""
        if self.is_running:
            logger.warning("Live processor is already running")
            return False
        
        if not self.api_client.is_configured():
            logger.error("Cannot start live processor: ChatGPT API not configured")
            return False
        
        try:
            self.is_running = True
            self.stats.status = ProcessingStatus.MONITORING
            self.stats.start_time = datetime.now()
            
            # Start processing in a separate thread
            self.processing_thread = threading.Thread(
                target=self._run_processing_loop,
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info("Live processor started successfully")
            self._notify_status_change()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start live processor: {e}")
            self.is_running = False
            self.stats.status = ProcessingStatus.ERROR
            return False
    
    def stop(self):
        """Stop the live processing system."""
        if not self.is_running:
            return
        
        logger.info("Stopping live processor...")
        self.is_running = False
        self.stats.status = ProcessingStatus.STOPPED
        self._notify_status_change()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=10)
        
        logger.info("Live processor stopped")
    
    def _run_processing_loop(self):
        """Main processing loop running in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._processing_loop())
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
            self.stats.status = ProcessingStatus.ERROR
            self._notify_status_change()
        finally:
            loop.close()
    
    async def _processing_loop(self):
        """Async processing loop."""
        while self.is_running:
            try:
                await self._process_batch()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                self.stats.errors_count += 1
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_batch(self):
        """Process a batch of new conversations."""
        start_time = time.time()
        self.stats.status = ProcessingStatus.PROCESSING
        self._notify_status_change()
        
        try:
            # Get new conversations
            conversations = await self.api_client.get_conversations(limit=self.batch_size)
            
            if not conversations:
                logger.debug("No new conversations found")
                return
            
            logger.info(f"Processing batch of {len(conversations)} conversations")
            
            # Process each conversation
            processed_count = 0
            for conversation in conversations:
                if not self.is_running:
                    break
                
                try:
                    await self._process_single_conversation(conversation)
                    processed_count += 1
                    
                    # Update progress
                    self._notify_progress(processed_count, len(conversations))
                    
                except Exception as e:
                    logger.error(f"Error processing conversation {conversation.get('id')}: {e}")
                    self.stats.errors_count += 1
            
            # Update statistics
            processing_time = time.time() - start_time
            self.stats.total_conversations_processed += processed_count
            self.stats.conversations_processed_today += processed_count
            self.stats.last_processing_time = datetime.now()
            
            # Update average processing time
            if self.stats.average_processing_time == 0:
                self.stats.average_processing_time = processing_time
            else:
                self.stats.average_processing_time = (
                    self.stats.average_processing_time + processing_time
                ) / 2
            
            logger.info(f"Batch processing completed: {processed_count} conversations in {processing_time:.2f}s")
            
            # Send Discord notification if configured
            if self.discord_manager and processed_count > 0:
                await self._send_discord_update(processed_count)
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            self.stats.errors_count += 1
        finally:
            self.stats.status = ProcessingStatus.MONITORING
            self._notify_status_change()
    
    async def _process_single_conversation(self, conversation: Dict):
        """Process a single conversation."""
        try:
            # Store in memory
            conversation_id = self.memory_manager.store_conversation(conversation)
            
            # Process through dreamscape
            result = self.dreamscape_processor.process_single_conversation(conversation_id)
            
            if result.get('success'):
                logger.debug(f"Processed conversation: {conversation.get('title', 'Untitled')}")
                
                # Update MMORPG state
                self.mmorpg_engine.update_from_conversation(conversation_id)
                
            else:
                logger.error(f"Failed to process conversation: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            raise
    
    async def _send_discord_update(self, processed_count: int):
        """Send Discord notification about processing results."""
        try:
            if not self.discord_manager:
                return
            
            # Get current MMORPG stats
            player = self.mmorpg_engine.get_player()
            skills = self.mmorpg_engine.get_skills()
            
            message = (
                f"🔄 **Live Processing Update**\n"
                f"Processed {processed_count} new conversations\n"
                f"Player: {player.name} ({player.architect_tier})\n"
                f"XP: {player.xp} / {player.get_next_level_xp()}\n"
                f"Active Skills: {len(skills)}"
            )
            
            await self.discord_manager.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send Discord update: {e}")
    
    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics."""
        return self.stats
    
    def get_status(self) -> ProcessingStatus:
        """Get current processing status."""
        return self.stats.status
    
    def is_configured(self) -> bool:
        """Check if the live processor is properly configured."""
        return self.api_client.is_configured()
    
    def add_status_callback(self, callback: Callable):
        """Add a callback for status changes."""
        self.status_callbacks.append(callback)
    
    def add_progress_callback(self, callback: Callable):
        """Add a callback for progress updates."""
        self.progress_callbacks.append(callback)
    
    def _notify_status_change(self):
        """Notify status change callbacks."""
        for callback in self.status_callbacks:
            try:
                callback(self.stats.status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _notify_progress(self, current: int, total: int):
        """Notify progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(current, total)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def reset_daily_stats(self):
        """Reset daily statistics (call this daily)."""
        self.stats.conversations_processed_today = 0
    
    def get_uptime(self) -> Optional[timedelta]:
        """Get system uptime."""
        if self.stats.start_time:
            return datetime.now() - self.stats.start_time
        return None

# Global live processor instance
live_processor = None

def initialize_live_processor(memory_manager: MemoryManager,
                            dreamscape_processor: DreamscapeProcessor,
                            mmorpg_engine: MMORPGEngine,
                            discord_manager: Optional[DiscordManager] = None) -> LiveProcessor:
    """Initialize the global live processor instance."""
    global live_processor
    live_processor = LiveProcessor(
        memory_manager=memory_manager,
        dreamscape_processor=dreamscape_processor,
        mmorpg_engine=mmorpg_engine,
        discord_manager=discord_manager
    )
    return live_processor

def get_live_processor() -> Optional[LiveProcessor]:
    """Get the global live processor instance."""
    return live_processor 