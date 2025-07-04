"""
Task Schema Module

This module provides task validation and management functionality.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class TaskHistory(BaseModel):
    """Schema for task history entries."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str = Field(..., description="ID of the agent that performed the action")
    action: str = Field(..., description="Action performed (CLAIMED, UPDATED, COMPLETED, etc.)")
    details: Optional[str] = Field(None, description="Additional details about the action")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Task(BaseModel):
    """Schema for tasks in the system."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Short name/identifier for the task")
    description: str = Field(..., description="Detailed description of the task")
    priority: str = Field(..., description="Task priority (CRITICAL, HIGH, MEDIUM, LOW)")
    status: str = Field(default="PENDING", description="Current status of the task")
    assigned_to: Optional[str] = Field(None, description="ID of the agent assigned to the task")
    task_type: str = Field(..., description="Type of task (e.g., REFACTOR, IMPLEMENTATION, TESTING)")
    created_by: str = Field(..., description="ID of the agent that created the task")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the task")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks this task depends on")
    estimated_duration: Optional[str] = Field(None, description="Estimated time to complete")
    deadline: Optional[datetime] = Field(None, description="Task deadline if applicable")
    history: List[TaskHistory] = Field(default_factory=list, description="History of task actions")
    critical: bool = Field(default=False, description="Whether this is a critical task")
    parent_task_id: Optional[str] = Field(None, description="ID of parent task if this is a subtask")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def create_task(
    name: str,
    description: str,
    priority: str,
    task_type: str,
    created_by: str,
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None,
    estimated_duration: Optional[str] = None,
    deadline: Optional[datetime] = None,
    critical: bool = False,
    parent_task_id: Optional[str] = None
) -> Task:
    """Helper function to create a new task."""
    return Task(
        name=name,
        description=description,
        priority=priority,
        task_type=task_type,
        created_by=created_by,
        tags=tags or [],
        dependencies=dependencies or [],
        estimated_duration=estimated_duration,
        deadline=deadline,
        critical=critical,
        parent_task_id=parent_task_id
    )

# Task status constants
TASK_STATUS = {
    "PENDING": "PENDING",
    "IN_PROGRESS": "IN_PROGRESS",
    "COMPLETED": "COMPLETED",
    "FAILED": "FAILED",
    "BLOCKED": "BLOCKED"
}

# Task priority levels
TASK_PRIORITY = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW"
}

# Task types
TASK_TYPES = {
    "REFACTOR": "REFACTOR",
    "IMPLEMENTATION": "IMPLEMENTATION",
    "TESTING": "TESTING",
    "DOCUMENTATION": "DOCUMENTATION",
    "BUGFIX": "BUGFIX",
    "FEATURE": "FEATURE",
    "MAINTENANCE": "MAINTENANCE",
    "ANALYSIS": "ANALYSIS",
    "PLANNING": "PLANNING",
    "REVIEW": "REVIEW"
}

def update_task_status(task: Task, new_status: str, agent_id: str, details: Optional[str] = None) -> Task:
    """Update a task's status and add to history."""
    task.status = new_status
    task.history.append(TaskHistory(
        agent=agent_id,
        action="UPDATE",
        details=f"Status changed to {new_status}. {details or ''}"
    ))
    return task

def claim_task(task: Task, agent_id: str) -> Task:
    """Claim a task for an agent."""
    task.assigned_to = agent_id
    task.status = TASK_STATUS["IN_PROGRESS"]
    task.history.append(TaskHistory(
        agent=agent_id,
        action="CLAIMED",
        details=f"Task claimed by {agent_id}"
    ))
    return task

def complete_task(task: Task, agent_id: str, details: Optional[str] = None) -> Task:
    """Mark a task as complete."""
    task.status = TASK_STATUS["COMPLETED"]
    task.history.append(TaskHistory(
        agent=agent_id,
        action="COMPLETED",
        details=details or "Task completed successfully"
    ))
    return task

def fail_task(task: Task, agent_id: str, error_details: str) -> Task:
    """Mark a task as failed."""
    task.status = TASK_STATUS["FAILED"]
    task.history.append(TaskHistory(
        agent=agent_id,
        action="FAILED",
        details=f"Task failed: {error_details}"
    ))
    return task

def block_task(task: Task, agent_id: str, blocker_details: str) -> Task:
    """Mark a task as blocked."""
    task.status = TASK_STATUS["BLOCKED"]
    task.history.append(TaskHistory(
        agent=agent_id,
        action="BLOCKED",
        details=f"Task blocked: {blocker_details}"
    ))
    return task

class TaskSchema:
    """Task schema for validation and management."""
    
    def __init__(self):
        """Initialize task schema."""
        self.logger = logging.getLogger(__name__)
        
    def validate_task(self, task_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate task against schema using Pydantic models.
        
        Args:
            task_data: Task dictionary to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        errors = []
        try:
            # Convert task data to Task model
            task = Task(**task_data)
            
            # Validate task ID format
            if not task.task_id or not isinstance(task.task_id, str):
                errors.append("Invalid task_id format")
                
            # Validate name
            if not task.name or not isinstance(task.name, str):
                errors.append("Invalid name format")
                
            # Validate description
            if not task.description or not isinstance(task.description, str):
                errors.append("Invalid description format")
                
            # Validate priority
            if task.priority not in TASK_PRIORITY.values():
                errors.append(f"Invalid priority: {task.priority}")
                
            # Validate status
            if task.status not in TASK_STATUS.values():
                errors.append(f"Invalid status: {task.status}")
                
            # Validate task type
            if task.task_type not in TASK_TYPES.values():
                errors.append(f"Invalid task type: {task.task_type}")
                
            # Validate created_by
            if not task.created_by or not isinstance(task.created_by, str):
                errors.append("Invalid created_by format")
                
            # Validate created_at
            if not isinstance(task.created_at, datetime):
                errors.append("Invalid created_at format")
                
            # Validate tags
            if not isinstance(task.tags, list) or not all(isinstance(tag, str) for tag in task.tags):
                errors.append("Invalid tags format")
                
            # Validate dependencies
            if not isinstance(task.dependencies, list) or not all(isinstance(dep, str) for dep in task.dependencies):
                errors.append("Invalid dependencies format")
                
            # Validate estimated_duration
            if task.estimated_duration is not None and not isinstance(task.estimated_duration, str):
                errors.append("Invalid estimated_duration format")
                
            # Validate deadline
            if task.deadline is not None and not isinstance(task.deadline, datetime):
                errors.append("Invalid deadline format")
                
            # Validate history
            if not isinstance(task.history, list):
                errors.append("Invalid history format")
            else:
                for entry in task.history:
                    if not isinstance(entry, TaskHistory):
                        errors.append("Invalid history entry format")
                        
            # Validate critical flag
            if not isinstance(task.critical, bool):
                errors.append("Invalid critical flag format")
                
            # Validate parent_task_id
            if task.parent_task_id is not None and not isinstance(task.parent_task_id, str):
                errors.append("Invalid parent_task_id format")
                
            # Validate assigned_to
            if task.assigned_to is not None and not isinstance(task.assigned_to, str):
                errors.append("Invalid assigned_to format")
                
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Error validating task: {e}")
            errors.append(f"Validation error: {str(e)}")
            return False, errors
            
    def validate_task_transition(self, current_status: str, new_status: str) -> Tuple[bool, List[str]]:
        """Validate task status transition.
        
        Args:
            current_status: Current task status
            new_status: New task status
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        errors = []
        
        # Validate current status
        if current_status not in TASK_STATUS.values():
            errors.append(f"Invalid current status: {current_status}")
            
        # Validate new status
        if new_status not in TASK_STATUS.values():
            errors.append(f"Invalid new status: {new_status}")
            
        # Validate transition rules
        valid_transitions = {
            TASK_STATUS["PENDING"]: [TASK_STATUS["IN_PROGRESS"], TASK_STATUS["BLOCKED"]],
            TASK_STATUS["IN_PROGRESS"]: [TASK_STATUS["COMPLETED"], TASK_STATUS["FAILED"], TASK_STATUS["BLOCKED"]],
            TASK_STATUS["BLOCKED"]: [TASK_STATUS["PENDING"], TASK_STATUS["IN_PROGRESS"]],
            TASK_STATUS["COMPLETED"]: [],
            TASK_STATUS["FAILED"]: [TASK_STATUS["PENDING"]]
        }
        
        if current_status in valid_transitions:
            if new_status not in valid_transitions[current_status]:
                errors.append(f"Invalid status transition from {current_status} to {new_status}")
        else:
            errors.append(f"Invalid current status: {current_status}")
            
        return len(errors) == 0, errors
        
    def validate_task_dependencies(self, task: Task, all_tasks: List[Task]) -> Tuple[bool, List[str]]:
        """Validate task dependencies.
        
        Args:
            task: Task to validate
            all_tasks: List of all tasks in the system
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        errors = []
        
        # Check for circular dependencies
        visited = set()
        path = []
        
        def check_circular_dep(task_id: str) -> bool:
            if task_id in path:
                return True
            if task_id in visited:
                return False
                
            visited.add(task_id)
            path.append(task_id)
            
            # Find task
            current_task = next((t for t in all_tasks if t.task_id == task_id), None)
            if current_task:
                for dep_id in current_task.dependencies:
                    if check_circular_dep(dep_id):
                        return True
                        
            path.pop()
            return False
            
        if check_circular_dep(task.task_id):
            errors.append("Circular dependency detected")
            
        # Check for missing dependencies
        task_ids = {t.task_id for t in all_tasks}
        missing_deps = [dep_id for dep_id in task.dependencies if dep_id not in task_ids]
        if missing_deps:
            errors.append(f"Missing dependencies: {', '.join(missing_deps)}")
            
        # Check for invalid parent task
        if task.parent_task_id and task.parent_task_id not in task_ids:
            errors.append(f"Invalid parent task: {task.parent_task_id}")
            
        return len(errors) == 0, errors

    def update_task_status(self, task_id: str, status: str, notes: str = "") -> bool:
        """Update task status in working tasks file.
        
        Args:
            task_id: ID of task to update
            status: New status
            notes: Optional completion notes
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Load working tasks
            tasks_path = Path("runtime/agent_comms/agent_mailboxes/working_tasks.json")
            if not tasks_path.exists():
                self.logger.error("Working tasks file not found")
                return False
                
            with open(tasks_path, 'r') as f:
                tasks = json.load(f)
                
            # Find task in claimed tasks
            for agent_id, agent_tasks in tasks.get('claimed_tasks', {}).items():
                for task in agent_tasks:
                    if task['task_id'] == task_id:
                        # Update status
                        task['status'] = status
                        if status == 'completed':
                            task['completed_at'] = datetime.utcnow().isoformat()
                            task['completion_notes'] = notes
                        return True
                        
            self.logger.error(f"Task {task_id} not found in working tasks")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            return False
            
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID.
        
        Args:
            task_id: ID of task to get
            
        Returns:
            Optional[Dict]: Task if found, None otherwise
        """
        try:
            # Load working tasks
            tasks_path = Path("runtime/agent_comms/agent_mailboxes/working_tasks.json")
            if not tasks_path.exists():
                self.logger.error("Working tasks file not found")
                return None
                
            with open(tasks_path, 'r') as f:
                tasks = json.load(f)
                
            # Find task in claimed tasks
            for agent_id, agent_tasks in tasks.get('claimed_tasks', {}).items():
                for task in agent_tasks:
                    if task['task_id'] == task_id:
                        return task
                        
            self.logger.error(f"Task {task_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting task: {e}")
            return None 