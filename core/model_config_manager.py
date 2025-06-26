#!/usr/bin/env python3
"""
Model Configuration Manager for Dream.OS
Handles model definitions and configuration management.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a ChatGPT model."""
    id: str
    name: str
    description: str
    capabilities: List[str]
    speed_rating: int  # 1-10
    reasoning_rating: int  # 1-10
    cost_rating: int  # 1-10 (1 = cheapest)
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class ModelConfigManager:
    """Manages model configurations and definitions."""
    
    def __init__(self):
        """Initialize the model configuration manager."""
        self.models: Dict[str, ModelConfig] = {}
        self._init_default_models()
    
    def _init_default_models(self):
        """Initialize default ChatGPT model configurations."""
        self.models = {
            "gpt-4o": ModelConfig(
                id="gpt-4o",
                name="GPT-4 Omni",
                description="Most capable model for complex reasoning and analysis",
                capabilities=["reasoning", "analysis", "coding", "creative", "multimodal"],
                speed_rating=8,
                reasoning_rating=10,
                cost_rating=3
            ),
            "o4-mini": ModelConfig(
                id="o4-mini",
                name="GPT-4o Mini",
                description="Fast and efficient for quick tasks and responses",
                capabilities=["speed", "efficiency", "basic_reasoning", "coding"],
                speed_rating=10,
                reasoning_rating=7,
                cost_rating=1
            ),
            "gpt-4-1": ModelConfig(
                id="gpt-4-1",
                name="GPT-4 (Legacy)",
                description="Legacy model for compatibility and specific use cases",
                capabilities=["legacy_compatibility", "reasoning", "coding"],
                speed_rating=6,
                reasoning_rating=9,
                cost_rating=2
            ),
            "gpt-3.5-turbo": ModelConfig(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Cost-effective for simple tasks and basic interactions",
                capabilities=["cost_effective", "basic_tasks", "simple_coding"],
                speed_rating=9,
                reasoning_rating=5,
                cost_rating=1
            )
        }
    
    def get_model(self, model_id: str) -> ModelConfig:
        """Get a model configuration by ID."""
        return self.models.get(model_id)
    
    def list_models(self) -> List[Dict]:
        """List all available models with their capabilities."""
        models_list = []
        for model_id, model in self.models.items():
            model_info = {
                'id': model_id,
                'name': model.name,
                'description': model.description,
                'capabilities': model.capabilities,
                'speed_rating': model.speed_rating,
                'reasoning_rating': model.reasoning_rating,
                'cost_rating': model.cost_rating
            }
            models_list.append(model_info)
        return models_list
    
    def add_model(self, model_config: ModelConfig):
        """Add a new model configuration."""
        self.models[model_config.id] = model_config
        logger.info(f"Added model: {model_config.name}")
    
    def get_model_url(self, conversation_id: str, model: str) -> str:
        """
        Generate a model-specific ChatGPT URL.
        
        Args:
            conversation_id: The conversation ID
            model: The model ID (e.g., 'gpt-4o', 'o4-mini')
            
        Returns:
            The complete ChatGPT URL with model parameter
        """
        base_url = "https://chat.openai.com"
        return f"{base_url}/c/{conversation_id}?model={model}" 