#!/usr/bin/env python3
"""
Task Router for Dream.OS
Handles task routing to appropriate models based on requirements.
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class TaskRouter:
    """Routes tasks to appropriate models based on requirements."""
    
    def __init__(self, model_manager):
        """
        Initialize the task router.
        
        Args:
            model_manager: Model configuration manager
        """
        self.model_manager = model_manager
    
    def route_task(self, task_description: str, requirements: Dict[str, int] = None) -> Tuple[str, str]:
        """
        Route a task to the best available model based on requirements.
        
        Args:
            task_description: Description of the task
            requirements: Dictionary of requirements (speed, reasoning, cost)
            
        Returns:
            Tuple of (model_id, conversation_id) for the best match
        """
        if requirements is None:
            requirements = {'reasoning': 5, 'speed': 5, 'cost': 5}
        
        best_score = -1
        best_model = None
        
        for model_id, model in self.model_manager.models.items():
            score = 0
            
            # Calculate score based on requirements
            if 'speed' in requirements:
                score += (10 - abs(model.speed_rating - requirements['speed'])) * 2
            if 'reasoning' in requirements:
                score += (10 - abs(model.reasoning_rating - requirements['reasoning'])) * 2
            if 'cost' in requirements:
                score += (10 - abs(model.cost_rating - requirements['cost']))
            
            # Bonus for matching capabilities
            task_lower = task_description.lower()
            for capability in model.capabilities:
                if capability.lower() in task_lower:
                    score += 5
            
            if score > best_score:
                best_score = score
                best_model = model_id
        
        # Find an available conversation for this model
        conversation_id = self._get_available_conversation(best_model)
        
        return best_model, conversation_id
    
    def _get_available_conversation(self, model: str) -> str:
        """
        Get an available conversation ID for a model.
        For now, returns empty string - this would be enhanced with conversation management.
        """
        # TODO: Implement conversation pool management
        return "" 