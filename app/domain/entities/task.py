"""Task domain entity"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class TaskMode(Enum):
    AUTO = "auto"
    SINGLE = "single"
    MULTI = "multi"


@dataclass
class TaskStep:
    id: str
    step_number: int
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    agent_name: str | None = None
    output: str | None = None
    error_message: str | None = None


@dataclass
class Task:
    id: str
    title: str
    description: str
    complexity: TaskComplexity
    mode: TaskMode
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    progress: float = 0.0
    completed_at: datetime | None = None
    priority: str = "medium"
    tags: list[str] = None
    document_ids: list[str] = None
    steps: list[TaskStep] = None
    config: dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.document_ids is None:
            self.document_ids = []
        if self.steps is None:
            self.steps = []
        if self.config is None:
            self.config = {}

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        complexity: TaskComplexity,
        mode: TaskMode = TaskMode.AUTO,
        **kwargs,
    ):
        """Factory method to create a new task"""
        now = datetime.utcnow()
        return cls(
            id=kwargs.get("id", ""),  # Will be set by repository
            title=title,
            description=description,
            complexity=complexity,
            mode=mode,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            **kwargs,
        )

    def start_execution(self):
        """Start task execution"""
        self.status = TaskStatus.RUNNING
        self.updated_at = datetime.utcnow()

    def complete(self):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def fail(self, error_message: str = None):  # noqa: ARG002
        """Mark task as failed"""
        self.status = TaskStatus.ERROR
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel task execution"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def update_progress(self, progress: float):
        """Update task progress"""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.utcnow()

    def add_step(self, step: TaskStep):
        """Add a new step to the task"""
        self.steps.append(step)
        self.updated_at = datetime.utcnow()
