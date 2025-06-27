#!/usr/bin/env python3
"""
Prompt Deployer - Core functionality for deploying prompts to ChatGPT conversations.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.model_router import ModelRouter, AgentConfig
from scrapers.chatgpt_scraper import ChatGPTScraper
from core.memory_manager import MemoryManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PromptDeployer:
    """
    Deploy prompt files to ChatGPT conversations with model-specific routing.
    """
    
    def __init__(self, config_file: str = "config/prompts.yaml"):
        self.config_file = Path(config_file)
        self.router = ModelRouter()
        self.scraper = None
        self.prompts_config = {}
        
        # Load prompt configuration
        self.load_prompt_config()
    
    def load_prompt_config(self):
        """Load prompt deployment configuration."""
        if not self.config_file.exists():
            logger.info(f"Prompt config file {self.config_file} not found, creating default...")
            self._create_default_prompt_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.prompts_config = yaml.safe_load(f)
            logger.info(f"Loaded prompt configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading prompt config: {e}")
            self._create_default_prompt_config()
    
    def _create_default_prompt_config(self):
        """Create default prompt configuration."""
        default_config = {
            'prompts': [
                {
                    'name': 'agent_resume',
                    'description': 'Resume agent conversation with context',
                    'prompt_file': 'templates/prompts/agent_resume.prompt.md',
                    'target_agent': 'thea',
                    'inject_mode': 'paste_and_wait',
                    'auto_deploy': True
                },
                {
                    'name': 'code_review',
                    'description': 'Code review prompt for Codex agent',
                    'prompt_file': 'templates/prompts/codex_validator.prompt.md',
                    'target_agent': 'codex',
                    'inject_mode': 'paste_and_wait',
                    'auto_deploy': False
                },
                {
                    'name': 'memory_analysis',
                    'description': 'Memory analysis prompt for Memory Agent',
                    'prompt_file': 'templates/prompts/memory_summarizer.prompt.md',
                    'target_agent': 'memory_agent',
                    'inject_mode': 'paste_and_wait',
                    'auto_deploy': False
                }
            ],
            'settings': {
                'default_wait_time': 2,
                'max_retries': 3,
                'retry_delay': 1
            }
        }
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created default prompt config at {self.config_file}")
    
    def initialize_scraper(self):
        """Initialize the ChatGPT scraper for deployment."""
        try:
            # Get credentials from environment
            username = os.getenv('CHATGPT_USERNAME')
            password = os.getenv('CHATGPT_PASSWORD')
            
            if not username or not password:
                logger.error("ChatGPT credentials not found in environment")
                return False
            
            self.scraper = ChatGPTScraper(
                headless=False,  # Show browser for deployment
                timeout=30,
                use_undetected=True,
                username=username,
                password=password
            )
            
            if not self.scraper.start_driver():
                logger.error("Failed to start browser driver")
                return False
            
            if not self.scraper.navigate_to_chatgpt():
                logger.error("Failed to navigate to ChatGPT")
                return False
            
            if not self.scraper.ensure_login_modern():
                logger.error("Failed to log into ChatGPT")
                return False
            
            logger.info("✅ Scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing scraper: {e}")
            return False
    
    def deploy_prompt(self, prompt_name: str, target_agent: str = None, conversation_id: str = None) -> bool:
        """
        Deploy a prompt to a specific agent or conversation.
        
        Args:
            prompt_name: Name of the prompt to deploy
            target_agent: Target agent name (optional)
            conversation_id: Specific conversation ID (optional)
            
        Returns:
            True if deployment successful, False otherwise
        """
        if not self.scraper:
            if not self.initialize_scraper():
                return False
        
        try:
            # Find the prompt configuration
            prompt_config = None
            for prompt in self.prompts_config.get('prompts', []):
                if prompt['name'] == prompt_name:
                    prompt_config = prompt
                    break
            
            if not prompt_config:
                logger.error(f"Prompt '{prompt_name}' not found in configuration")
                return False
            
            # Determine target
            if target_agent:
                agent_name = target_agent
            else:
                agent_name = prompt_config.get('target_agent')
            
            if not agent_name:
                logger.error("No target agent specified")
                return False
            
            # Get agent URL
            if conversation_id:
                # Use specific conversation ID
                agent = self.router.agents.get(agent_name)
                if not agent:
                    logger.error(f"Agent '{agent_name}' not found")
                    return False
                url = self.router.get_model_url(conversation_id, agent.model)
            else:
                # Use agent's configured conversation
                url = self.router.get_agent_url(agent_name)
            
            if not url:
                logger.error(f"No conversation URL available for agent '{agent_name}'")
                return False
            
            # Load prompt content
            prompt_file = Path(prompt_config['prompt_file'])
            if not prompt_file.exists():
                logger.error(f"Prompt file not found: {prompt_file}")
                return False
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            # Deploy to the agent
            return self.deploy_to_agent(agent_name, prompt_content)
            
        except Exception as e:
            logger.error(f"Error deploying prompt: {e}")
            return False
    
    def deploy_to_agent(self, agent_name: str, prompt_content: str) -> bool:
        """Deploy prompt to an agent, then archive the resulting conversation."""
        try:
            # Resolve the target conversation URL for the agent
            agent_url = self.router.get_agent_url(agent_name)
            if not agent_url:
                logger.error(f"No URL available for agent '{agent_name}'")
                return False

            # Step 1 ─ Navigate / enter conversation
            if not self.scraper.enter_conversation(agent_url):
                logger.error(f"Failed to load conversation page for '{agent_name}' -> {agent_url}")
                return False

            # Step 2 ─ Send the prompt and wait for the model to respond
            if not self.scraper.send_prompt(prompt_content, wait_for_response=True):
                logger.error("Prompt send/response cycle failed")
                return False

            # Step 3 ─ Extract full, updated conversation content
            convo = self.scraper.get_conversation_content()
            if not convo or not convo.get("content"):
                logger.warning("No content extracted after prompt deployment; skipping archive")
                return True  # prompt delivered, but nothing to archive

            # Step 4 ─ Archive into Dreamscape memory DB
            try:
                memory = MemoryManager()

                # Build storage payload expecting MemoryStorage columns
                from datetime import datetime
                import hashlib

                # Derive a reproducible ID from the ChatGPT URL when possible
                url_id_segment = convo.get("url", "").rstrip("/").split("/")[-1]
                convo_id = url_id_segment or hashlib.md5(convo["content"].encode()).hexdigest()[:12]

                word_count = len(convo["content"].split())

                stored = memory.store_conversation({
                    "id": convo_id,
                    "title": convo.get("title", "Untitled"),
                    "timestamp": convo.get("timestamp") or datetime.utcnow().isoformat(),
                    "model": convo.get("model", "unknown"),
                    "content": convo["content"],
                    "url": convo.get("url", ""),
                    "message_count": convo.get("message_count", len(convo.get("messages", []))),
                    "word_count": word_count,
                })

                if stored:
                    logger.info(f"📚 Archived conversation '{convo.get('title')}' (ID: {convo_id})")
                else:
                    logger.warning("Failed to archive conversation to memory DB")
            except Exception as arch_err:
                logger.error(f"Archive error: {arch_err}")

            logger.info(f"✅ Prompt deployed & conversation archived for {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Error during prompt deployment to agent '{agent_name}': {e}")
            return False
    
    def list_prompts(self) -> list:
        """List all available prompts."""
        return [prompt['name'] for prompt in self.prompts_config.get('prompts', [])]
    
    def add_prompt(self, name: str, prompt_file: str, target_agent: str, description: str = ""):
        """Add a new prompt to the configuration."""
        new_prompt = {
            'name': name,
            'description': description,
            'prompt_file': prompt_file,
            'target_agent': target_agent,
            'inject_mode': 'paste_and_wait',
            'auto_deploy': False
        }
        
        self.prompts_config['prompts'].append(new_prompt)
        self._save_prompt_config()
        logger.info(f"Added prompt: {name}")
    
    def _save_prompt_config(self):
        """Save the prompt configuration."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.prompts_config, f, default_flow_style=False, indent=2)
    
    def close(self):
        """Clean up resources."""
        if self.scraper:
            self.scraper.close()
            logger.info("✅ Scraper closed") 