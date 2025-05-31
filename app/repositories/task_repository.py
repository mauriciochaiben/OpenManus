"""In-memory task repository implementation"""

import uuid
from typing import Dict, List, Optional

from app.domain.entities import Task
from app.repositories.interfaces import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation of task repository"""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def create(self, task: Task) -> Task:
        """Create a new task"""
        if not task.id:
            task.id = str(uuid.uuid4())
        self._tasks[task.id] = task
        return task

    async def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find task by ID"""
        return self._tasks.get(task_id)

    async def find_all(self) -> List[Task]:
        """Get all tasks"""
        return list(self._tasks.values())

    async def update(self, task: Task) -> Task:
        """Update existing task"""
        if task.id not in self._tasks:
            raise ValueError(f"Task with ID {task.id} not found")
        self._tasks[task.id] = task
        return task

    async def delete(self, task_id: str) -> bool:
        """Delete task by ID"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    async def find_by_status(self, status: str) -> List[Task]:
        """Find tasks by status"""
        return [task for task in self._tasks.values() if task.status.value == status]
