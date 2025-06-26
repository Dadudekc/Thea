#!/usr/bin/env python3
"""
Agent Configuration Manager for Dream.OS
Handles agent configuration and management operations.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for a Dream.OS agent."""
    name: str
    model: str
    conversation_id: str
    description: str = ""
    capabilities: List[str] = None
    prompt_template: str = ""
    auto_deploy: bool = False
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class AgentConfigManager:
    """Manages agent configurations and operations."""
    
    def __init__(self, config_file: str = "config/agents.yaml"):
        """
        Initialize the agent configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.agents: Dict[str, AgentConfig] = {}
        self.load_config()
    
    def load_config(self):
        """Load agent configuration from YAML file."""
        if not self.config_file.exists():
            logger.info(f"Config file {self.config_file} not found, creating default...")
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Load agents
            if 'agents' in config:
                for agent_data in config['agents']:
                    agent = AgentConfig(**agent_data)
                    self.agents[agent.name] = agent
            
            logger.info(f"Loaded {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default agent configuration."""
        default_config = {
            'agents': [
                {
                    'name': 'thea',
                    'model': 'gpt-4o',
                    'conversation_id': '',
                    'description': 'Main Dream.OS assistant for complex reasoning and analysis',
                    'capabilities': ['reasoning', 'analysis', 'planning'],
                    'prompt_template': 'You are Thea, the Dream.OS assistant. Help with complex tasks and analysis.',
                    'auto_deploy': True
                },
                {
                    'name': 'codex',
                    'model': 'o4-mini',
                    'conversation_id': '',
                    'description': 'Fast code reviewer and developer assistant',
                    'capabilities': ['coding', 'review', 'speed'],
                    'prompt_template': 'You are Codex, a fast and efficient code reviewer. Provide quick, actionable feedback.',
                    'auto_deploy': True
                },
                {
                    'name': 'memory_agent',
                    'model': 'gpt-4-1',
                    'conversation_id': '',
                    'description': 'Memory management and conversation analysis',
                    'capabilities': ['memory', 'analysis', 'summarization'],
                    'prompt_template': 'You are the Memory Agent. Analyze and summarize conversations for storage.',
                    'auto_deploy': False
                }
            ]
        }
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created default config at {self.config_file}")
    
    def get_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Get an agent configuration by name."""
        return self.agents.get(agent_name)
    
    def list_agents(self, model_manager) -> List[Dict]:
        """List all configured agents with their details."""
        agents_list = []
        for name, agent in self.agents.items():
            model = model_manager.get_model(agent.model)
            agent_info = {
                'name': name,
                'model': agent.model,
                'model_name': model.name if model else 'Unknown',
                'conversation_id': agent.conversation_id,
                'description': agent.description,
                'capabilities': agent.capabilities,
                'url': model_manager.get_model_url(agent.conversation_id, agent.model) if agent.conversation_id else None
            }
            agents_list.append(agent_info)
        return agents_list
    
    def add_agent(self, agent_config: AgentConfig):
        """Add a new agent to the configuration."""
        self.agents[agent_config.name] = agent_config
        self._save_config()
        logger.info(f"Added agent: {agent_config.name}")
    
    def update_agent_conversation(self, agent_name: str, conversation_id: str):
        """Update an agent's conversation ID."""
        if agent_name in self.agents:
            self.agents[agent_name].conversation_id = conversation_id
            self._save_config()
            logger.info(f"Updated {agent_name} conversation ID: {conversation_id}")
        else:
            logger.warning(f"Agent '{agent_name}' not found")
    
    def get_agent_url(self, agent_name: str, model_manager) -> Optional[str]:
        """
        Get the ChatGPT URL for a specific agent.
        
        Args:
            agent_name: Name of the agent
            model_manager: Model configuration manager
            
        Returns:
            The agent's ChatGPT URL or None if not configured
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent '{agent_name}' not found")
            return None
        
        agent = self.agents[agent_name]
        if not agent.conversation_id:
            logger.warning(f"Agent '{agent_name}' has no conversation ID configured")
            return None
        
        return model_manager.get_model_url(agent.conversation_id, agent.model)
    
    def _save_config(self):
        """Save current configuration to file."""
        config = {
            'agents': [
                {
                    'name': agent.name,
                    'model': agent.model,
                    'conversation_id': agent.conversation_id,
                    'description': agent.description,
                    'capabilities': agent.capabilities,
                    'prompt_template': agent.prompt_template,
                    'auto_deploy': agent.auto_deploy
                }
                for agent in self.agents.values()
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2) 