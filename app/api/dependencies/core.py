"""Dependency injection for FastAPI"""

from fastapi import Depends

from app.infrastructure.messaging import event_bus
from app.infrastructure.messaging.event_bus import EventBus
from app.repositories import (
    DocumentRepository,
    InMemoryDocumentRepository,
    InMemoryTaskRepository,
    TaskRepository,
)
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent
from app.services.task_service import TaskService
from app.services.workflow_service import WorkflowService

# Repository instances (singleton for in-memory)
_task_repository = InMemoryTaskRepository()
_document_repository = InMemoryDocumentRepository()


def get_task_repository() -> TaskRepository:
    """Get task repository dependency"""
    return _task_repository


def get_document_repository() -> DocumentRepository:
    """Get document repository dependency"""
    return _document_repository


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    """Get task service dependency"""
    return TaskService(task_repo, event_bus)


def get_event_bus() -> EventBus:
    """Get event bus dependency"""
    return event_bus


def get_planner_agent() -> PlannerAgent:
    """Get planner agent dependency"""
    return PlannerAgent()


def get_tool_user_agent() -> ToolUserAgent:
    """Get tool user agent dependency"""
    return ToolUserAgent()


def get_workflow_service(
    planner_agent: PlannerAgent = Depends(get_planner_agent),
    tool_user_agent: ToolUserAgent = Depends(get_tool_user_agent),
    event_bus: EventBus = Depends(get_event_bus),
) -> WorkflowService:
    """Get workflow service dependency"""
    return WorkflowService(
        planner_agent=planner_agent,
        tool_user_agent=tool_user_agent,
        event_bus=event_bus,
    )
