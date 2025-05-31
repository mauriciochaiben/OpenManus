"""Abstract repository interfaces"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import Document, Task


class TaskRepository(ABC):
    """Abstract interface for task repository"""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        pass

    @abstractmethod
    async def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find task by ID"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Task]:
        """Get all tasks"""
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update existing task"""
        pass

    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        """Delete task by ID"""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> List[Task]:
        """Find tasks by status"""
        pass


class DocumentRepository(ABC):
    """Abstract interface for document repository"""

    @abstractmethod
    async def create(self, document: Document) -> Document:
        """Create a new document"""
        pass

    @abstractmethod
    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """Find document by ID"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Document]:
        """Get all documents"""
        pass

    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Update existing document"""
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        pass
