"""Task service - Business logic layer"""

from datetime import datetime
from typing import Any

from app.domain.entities import Task, TaskComplexity, TaskMode, TaskStatus
from app.infrastructure.messaging.event_bus import (
    EventBus,
    TaskCreatedEvent,
    TaskUpdatedEvent,
)
from app.repositories.interfaces import TaskRepository


class ComplexityAnalysisService:
    """Service for analyzing task complexity"""

    def analyze(self, description: str) -> dict[str, Any]:
        """Analyze task complexity based on description"""
        description_lower = description.lower()

        indicators = {
            "length": len(description) > 100,
            "keywords": any(
                keyword in description_lower
                for keyword in [
                    "multiple",
                    "several",
                    "many",
                    "complex",
                    "analyze",
                    "research",
                    "coordinate",
                    "integrate",
                    "comprehensive",
                ]
            ),
            "multipleDomains": any(
                domain in description_lower
                for domain in [
                    "file",
                    "web",
                    "database",
                    "api",
                    "document",
                    "image",
                    "data",
                    "report",
                    "chart",
                ]
            ),
            "timeConsuming": any(
                phrase in description_lower for phrase in ["detailed", "thorough", "extensive", "complete", "full"]
            ),
        }

        score = sum(indicators.values()) / len(indicators)
        is_complex = score > 0.5

        if score > 0.7:
            complexity = TaskComplexity.COMPLEX
            recommendation = TaskMode.MULTI
        elif score > 0.3:
            complexity = TaskComplexity.MEDIUM
            recommendation = TaskMode.AUTO
        else:
            complexity = TaskComplexity.SIMPLE
            recommendation = TaskMode.SINGLE

        return {
            "score": score,
            "isComplex": is_complex,
            "complexity": complexity,
            "indicators": indicators,
            "recommendation": recommendation,
        }


class TaskService:
    """Service for task management business logic"""

    def __init__(self, task_repository: TaskRepository, event_bus: EventBus):
        self.task_repository = task_repository
        self.event_bus = event_bus
        self.complexity_service = ComplexityAnalysisService()

    async def create_task(
        self,
        title: str,
        description: str,
        mode: str | None = None,
        priority: str = "medium",
        tags: list[str] | None = None,
        document_ids: list[str] | None = None,
        config: dict | None = None,
    ) -> Task:
        """Create a new task with complexity analysis"""
        # Analyze complexity
        analysis = self.complexity_service.analyze(description)
        complexity = analysis["complexity"]

        # Determine mode
        task_mode = TaskMode(mode) if mode else analysis["recommendation"]

        # Create task entity
        task = Task.create(
            title=title,
            description=description,
            complexity=complexity,
            mode=task_mode,
            priority=priority,
            tags=tags or [],
            document_ids=document_ids or [],
            config=config or {},
        )

        # Save to repository
        created_task = await self.task_repository.create(task)

        # Publish event
        await self.event_bus.publish(TaskCreatedEvent(created_task.id, created_task))

        return created_task

    async def get_task(self, task_id: str) -> Task | None:
        """Get task by ID"""
        return await self.task_repository.find_by_id(task_id)

    async def get_all_tasks(self) -> list[Task]:
        """Get all tasks"""
        return await self.task_repository.find_all()

    async def update_task_status(self, task_id: str, status: TaskStatus) -> Task | None:
        """Update task status"""
        task = await self.task_repository.find_by_id(task_id)
        if not task:
            return None

        old_status = task.status
        task.status = status
        task.updated_at = datetime.utcnow()

        if status == TaskStatus.COMPLETED:
            task.complete()
        elif status == TaskStatus.ERROR:
            task.fail()
        elif status == TaskStatus.CANCELLED:
            task.cancel()

        updated_task = await self.task_repository.update(task)

        # Publish event
        await self.event_bus.publish(TaskUpdatedEvent(task_id, updated_task, old_status, status))

        return updated_task

    async def update_task_progress(self, task_id: str, progress: float) -> Task | None:
        """Update task progress"""
        task = await self.task_repository.find_by_id(task_id)
        if not task:
            return None

        task.update_progress(progress)
        return await self.task_repository.update(task)

    async def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        task = await self.task_repository.find_by_id(task_id)
        if not task:
            return False

        return await self.task_repository.delete(task_id)

    async def get_dashboard_stats(self) -> dict[str, Any]:
        """Get dashboard statistics"""
        tasks = await self.task_repository.find_all()

        if not tasks:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "running_tasks": 0,
                "pending_tasks": 0,
                "error_tasks": 0,
                "completion_percentage": 0,
                "recent_activity": [],
            }

        # Count by status
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        running_tasks = len([t for t in tasks if t.status == TaskStatus.RUNNING])
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
        error_tasks = len([t for t in tasks if t.status == TaskStatus.ERROR])

        completion_percentage = (completed_tasks / len(tasks) * 100) if tasks else 0

        # Recent activity (last 10 tasks)
        recent_tasks = sorted(tasks, key=lambda x: x.created_at, reverse=True)[:10]
        recent_activity = []

        for task in recent_tasks:
            activity = {
                "task_id": task.id,
                "task_title": task.title,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            if task.completed_at:
                activity["completed_at"] = task.completed_at.isoformat()
            recent_activity.append(activity)

        return {
            "total_tasks": len(tasks),
            "completed_tasks": completed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "error_tasks": error_tasks,
            "completion_percentage": round(completion_percentage, 1),
            "recent_activity": recent_activity,
        }
