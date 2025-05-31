"""
Progress Broadcasting System for Multi-Agent Execution

This module provides utilities to broadcast real-time progress updates
via WebSocket during multi-agent execution.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from app.logger import logger


@dataclass
class ProgressUpdate:
    """Represents a progress update message"""

    stage: str
    progress: float  # 0-100
    execution_type: str  # 'single', 'multi', 'mcp'
    agents: List[str] = None
    task_name: Optional[str] = None
    step_number: Optional[int] = None
    total_steps: Optional[int] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ProgressBroadcaster:
    """Handles broadcasting progress updates via WebSocket"""

    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager
        self.active_tasks: Dict[str, ProgressUpdate] = {}

    def set_connection_manager(self, manager):
        """Set the WebSocket connection manager"""
        self.connection_manager = manager

    async def broadcast_progress(
        self,
        task_id: str,
        stage: str,
        progress: float,
        execution_type: str,
        agents: List[str] = None,
        task_name: str = None,
        step_number: int = None,
        total_steps: int = None,
        description: str = None,
    ):
        """Broadcast a progress update to all connected clients"""

        # Create progress update
        progress_update = ProgressUpdate(
            stage=stage,
            progress=max(0, min(100, progress)),  # Ensure 0-100 range
            execution_type=execution_type,
            agents=agents or [],
            task_name=task_name,
            step_number=step_number,
            total_steps=total_steps,
            description=description,
        )

        # Store current progress
        self.active_tasks[task_id] = progress_update

        # Create WebSocket message
        message = {
            "type": "task_progress",
            "data": {
                "task_id": task_id,
                "stage": progress_update.stage,
                "progress": progress_update.progress,
                "execution_type": progress_update.execution_type,
                "agents": progress_update.agents,
                "task_name": progress_update.task_name,
                "step_number": progress_update.step_number,
                "total_steps": progress_update.total_steps,
                "description": progress_update.description,
                "timestamp": progress_update.timestamp,
            },
        }

        # Broadcast via WebSocket if connection manager is available
        if self.connection_manager:
            try:
                await self.connection_manager.broadcast(json.dumps(message))
                logger.info(
                    f"Broadcasted progress: {stage} ({progress:.1f}%) for task {task_id}"
                )
            except Exception as e:
                logger.error(f"Failed to broadcast progress update: {e}")
        else:
            logger.warning("No connection manager available for progress broadcasting")

    async def broadcast_completion(self, task_id: str, result: str):
        """Broadcast task completion"""
        message = {
            "type": "task_completed",
            "data": {
                "task_id": task_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            },
        }

        if self.connection_manager:
            try:
                await self.connection_manager.broadcast(json.dumps(message))
                logger.info(f"Broadcasted completion for task {task_id}")
            except Exception as e:
                logger.error(f"Failed to broadcast completion: {e}")

        # Clean up active task
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

    async def broadcast_failure(self, task_id: str, error: str):
        """Broadcast task failure"""
        message = {
            "type": "task_failed",
            "data": {
                "task_id": task_id,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            },
        }

        if self.connection_manager:
            try:
                await self.connection_manager.broadcast(json.dumps(message))
                logger.info(f"Broadcasted failure for task {task_id}: {error}")
            except Exception as e:
                logger.error(f"Failed to broadcast failure: {e}")

        # Clean up active task
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

    def get_current_progress(self, task_id: str) -> Optional[ProgressUpdate]:
        """Get current progress for a task"""
        return self.active_tasks.get(task_id)

    def get_all_active_tasks(self) -> Dict[str, ProgressUpdate]:
        """Get all active tasks and their progress"""
        return self.active_tasks.copy()


# Global progress broadcaster instance
progress_broadcaster = ProgressBroadcaster()
