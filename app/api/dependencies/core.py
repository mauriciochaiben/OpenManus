"""Dependency injection for FastAPI"""

from fastapi import Depends

from app.infrastructure.messaging import event_bus
from app.repositories import (
    DocumentRepository,
    InMemoryDocumentRepository,
    InMemoryTaskRepository,
    TaskRepository,
)
from app.services.task_service import TaskService

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
