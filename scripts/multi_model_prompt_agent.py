#!/usr/bin/env python3
"""
Multi-Model Prompt Injection Agent for Dream.OS

This agent automates prompt testing across multiple ChatGPT conversations and models
by navigating to conversation URLs with model-specific routing and injecting prompt templates.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.prompt_agent_core import PromptAgentCore
from core.template_engine import render_template
from utils.chat_navigation import robust_navigate_to_convo

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_prompt_batch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiModelPromptAgent:
    """
    Agent for injecting prompt templates into multiple ChatGPT conversations across different models.
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.core = PromptAgentCore(headless=headless)
        
        # Default models to test
        self.models = ["gpt-4o", "gpt-4-1", "o4-mini", "o4-mini-high"]
        
        # Create model directories
        for model in self.models:
            (self.core.output_dir / model).mkdir(exist_ok=True)
    
    def run_batch(self, conversations: List[Dict], prompt_templates: Dict[str, str], 
                  delay_between_runs: int = 5, max_conversations: Optional[int] = None) -> bool:
        """
        Run batch processing of conversations with prompt templates across multiple models.
        
        Args:
            conversations: List of conversation dictionaries
            prompt_templates: Dictionary of prompt templates
            delay_between_runs: Delay between processing each conversation
            max_conversations: Maximum number of conversations to process (for testing)
            
        Returns:
            True if batch processing completed successfully
        """
        try:
            # Initialize scraper
            if not self.core.initialize_scraper():
                logger.error("Failed to initialize scraper")
                return False
            
            # Limit conversations if specified
            if max_conversations:
                conversations = conversations[:max_conversations]
                logger.info(f"Limited to {max_conversations} conversations for testing")
            
            total_conversations = len(conversations)
            total_prompts = len(prompt_templates)
            total_models = len(self.models)
            total_operations = total_conversations * total_prompts * total_models
            
            logger.info(f"Starting batch processing:")
            logger.info(f"  - Conversations: {total_conversations}")
            logger.info(f"  - Prompt templates: {total_prompts}")
            logger.info(f"  - Models: {total_models}")
            logger.info(f"  - Total operations: {total_operations}")
            
            successful_operations = 0
            failed_operations = 0
            
            # Process each conversation
            for conv_idx, conversation in enumerate(conversations, 1):
                conversation_id = conversation.get('id', f"conv_{conv_idx}")
                conversation_url = conversation.get('url', '')
                
                logger.info(f"\n--- Processing Conversation {conv_idx}/{total_conversations}: {conversation_id} ---")
                
                # Process each model
                for model_idx, model in enumerate(self.models, 1):
                    logger.info(f"  Model {model_idx}/{total_models}: {model}")
                    
                    # Process each prompt template
                    for prompt_idx, (prompt_id, prompt_template) in enumerate(prompt_templates.items(), 1):
                        logger.info(f"    Prompt {prompt_idx}/{total_prompts}: {prompt_id}")
                        
                        try:
                            # Navigate to conversation with model
                            model_url = f"{conversation_url}?model={model}"
                            if not robust_navigate_to_convo(self.core.scraper.driver, model_url):
                                logger.warning(f"    ⚠️ Failed to navigate to {model_url}")
                                failed_operations += 1
                                continue
                            
                            # Wait for chat to be ready
                            if not self.core.wait_for_chat_ready(timeout=30):
                                logger.warning(f"    ⚠️ Chat not ready for {model}")
                                failed_operations += 1
                                continue
                            
                            # Get conversation content for template rendering
                            conversation_content = self.core.get_conversation_content(conversation_id)
                            
                            # Render prompt template
                            try:
                                rendered_prompt = render_template(prompt_template, {
                                    'conversation_content': conversation_content or "No content available"
                                })
                            except Exception as e:
                                logger.warning(f"    ⚠️ Failed to render template: {e}")
                                rendered_prompt = prompt_template
                            
                            # Send prompt
                            if not self.core.send_prompt(rendered_prompt):
                                logger.warning(f"    ⚠️ Failed to send prompt to {model}")
                                failed_operations += 1
                                continue
                            
                            # Capture response
                            response = self.core.capture_response(timeout=60)
                            if not response:
                                logger.warning(f"    ⚠️ Failed to capture response from {model}")
                                failed_operations += 1
                                continue
                            
                            # Save output
                            if self.core.save_output(model, conversation_id, prompt_id, response):
                                logger.info(f"    ✅ Successfully processed {prompt_id} with {model}")
                                successful_operations += 1
                            else:
                                logger.warning(f"    ⚠️ Failed to save output for {prompt_id} with {model}")
                                failed_operations += 1
                            
                            # Small delay between prompts
                            time.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"    ❌ Error processing {prompt_id} with {model}: {e}")
                            failed_operations += 1
                    
                    # Delay between models
                    if model_idx < total_models:
                        time.sleep(3)
                
                # Delay between conversations
                if conv_idx < total_conversations:
                    logger.info(f"Waiting {delay_between_runs} seconds before next conversation...")
                    time.sleep(delay_between_runs)
            
            # Summary
            logger.info(f"\n--- Batch Processing Complete ---")
            logger.info(f"Successful operations: {successful_operations}")
            logger.info(f"Failed operations: {failed_operations}")
            logger.info(f"Success rate: {(successful_operations / total_operations * 100):.1f}%")
            
            return successful_operations > 0
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return False
        
        finally:
            self.core.close()
    
    def run_single_test(self, conversation_id: str, prompt_id: str, model: str = "gpt-4o") -> bool:
        """
        Run a single test with one conversation, one prompt, and one model.
        
        Args:
            conversation_id: ID of the conversation to test
            prompt_id: ID of the prompt template to use
            model: Model to test with
            
        Returns:
            True if test completed successfully
        """
        try:
            # Load prompt templates
            prompt_templates = self.core.load_prompt_templates()
            if prompt_id not in prompt_templates:
                logger.error(f"Prompt template '{prompt_id}' not found")
                return False
            
            # Create test conversation
            test_conversation = {
                'id': conversation_id,
                'url': f"https://chat.openai.com/c/{conversation_id}"
            }
            
            # Run single test
            return self.run_batch(
                conversations=[test_conversation],
                prompt_templates={prompt_id: prompt_templates[prompt_id]},
                delay_between_runs=0,
                max_conversations=1
            )
            
        except Exception as e:
            logger.error(f"Single test failed: {e}")
            return False

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Model Prompt Injection Agent")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--conversations", default="conversations.json", help="Conversations file")
    parser.add_argument("--max-conversations", type=int, help="Maximum conversations to process")
    parser.add_argument("--delay", type=int, default=5, help="Delay between conversations")
    parser.add_argument("--test-single", help="Test single conversation ID")
    parser.add_argument("--prompt", help="Prompt ID for single test")
    parser.add_argument("--model", default="gpt-4o", help="Model for single test")
    
    args = parser.parse_args()
    
    # Create agent
    agent = MultiModelPromptAgent(headless=args.headless)
    
    if args.test_single:
        # Single test mode
        if not args.prompt:
            logger.error("--prompt required for single test mode")
            return
        
        success = agent.run_single_test(args.test_single, args.prompt, args.model)
        if success:
            logger.info("✅ Single test completed successfully")
        else:
            logger.error("❌ Single test failed")
    else:
        # Batch mode
        # Load conversations
        conversations = agent.core.load_conversations(args.conversations)
        if not conversations:
            logger.error("No conversations loaded")
            return
        
        # Load prompt templates
        prompt_templates = agent.core.load_prompt_templates()
        if not prompt_templates:
            logger.error("No prompt templates loaded")
            return
        
        # Run batch processing
        success = agent.run_batch(
            conversations=conversations,
            prompt_templates=prompt_templates,
            delay_between_runs=args.delay,
            max_conversations=args.max_conversations
        )
        
        if success:
            logger.info("✅ Batch processing completed successfully")
        else:
            logger.error("❌ Batch processing failed")

if __name__ == "__main__":
    main() 