#!/usr/bin/env python3
"""
Dream.OS Model Router - Handles model-specific conversation routing and agent assignment.
Enables distributed agent execution across different ChatGPT models.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from .model_config_manager import ModelConfigManager, ModelConfig
from .agent_config_manager import AgentConfigManager, AgentConfig
from .task_router import TaskRouter

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Routes tasks and agents to appropriate ChatGPT models based on requirements.
    """
    
    def __init__(self, config_file: str = "config/agents.yaml"):
        self.model_manager = ModelConfigManager()
        self.agent_manager = AgentConfigManager(config_file)
        self.task_router = TaskRouter(self.model_manager)
        self.conversation_cache: Dict[str, Dict] = {}
    
    def get_model_url(self, conversation_id: str, model: str) -> str:
        """Generate a model-specific ChatGPT URL."""
        return self.model_manager.get_model_url(conversation_id, model)
    
    def get_agent_url(self, agent_name: str) -> Optional[str]:
        """Get the ChatGPT URL for a specific agent."""
        return self.agent_manager.get_agent_url(agent_name, self.model_manager)
    
    def route_task(self, task_description: str, requirements: Dict[str, int] = None) -> Tuple[str, str]:
        """Route a task to the best available model based on requirements."""
        return self.task_router.route_task(task_description, requirements)
    
    def list_agents(self) -> List[Dict]:
        """List all configured agents with their details."""
        return self.agent_manager.list_agents(self.model_manager)
    
    def list_models(self) -> List[Dict]:
        """List all available models with their capabilities."""
        return self.model_manager.list_models()
    
    def add_agent(self, agent_config: AgentConfig):
        """Add a new agent to the configuration."""
        self.agent_manager.add_agent(agent_config)
    
    def update_agent_conversation(self, agent_name: str, conversation_id: str):
        """Update an agent's conversation ID."""
        self.agent_manager.update_agent_conversation(agent_name, conversation_id)

def main():
    """CLI interface for the Model Router."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dream.OS Model Router")
    parser.add_argument('--list-agents', action='store_true', help='List all agents')
    parser.add_argument('--list-models', action='store_true', help='List all models')
    parser.add_argument('--route-task', type=str, help='Route a task to best model')
    parser.add_argument('--agent-url', type=str, help='Get URL for specific agent')
    parser.add_argument('--add-agent', type=str, help='Add new agent (JSON config)')
    
    args = parser.parse_args()
    
    router = ModelRouter()
    
    if args.list_agents:
        agents = router.list_agents()
        print("\n🤖 Dream.OS Agents:")
        for agent in agents:
            print(f"  {agent['name']}: {agent['model_name']} - {agent['description']}")
            if agent['url']:
                print(f"    URL: {agent['url']}")
    
    elif args.list_models:
        models = router.list_models()
        print("\n🧠 Available Models:")
        for model in models:
            print(f"  {model['id']}: {model['name']}")
            print(f"    Speed: {model['speed_rating']}/10, Reasoning: {model['reasoning_rating']}/10, Cost: {model['cost_rating']}/10")
            print(f"    Capabilities: {', '.join(model['capabilities'])}")
    
    elif args.route_task:
        model, conv_id = router.route_task(args.route_task)
        print(f"\n🎯 Task Routing:")
        print(f"  Task: {args.route_task}")
        print(f"  Recommended Model: {model}")
        print(f"  URL: {router.get_model_url(conv_id, model) if conv_id else 'No conversation available'}")
    
    elif args.agent_url:
        url = router.get_agent_url(args.agent_url)
        if url:
            print(f"\n🔗 Agent URL: {url}")
        else:
            print(f"\n❌ Agent '{args.agent_url}' not found or not configured")
    
    elif args.add_agent:
        try:
            agent_data = json.loads(args.add_agent)
            agent = AgentConfig(**agent_data)
            router.add_agent(agent)
            print(f"✅ Added agent: {agent.name}")
        except Exception as e:
            print(f"❌ Error adding agent: {e}")

if __name__ == "__main__":
    main() 