"""Event system for decoupled communication"""

import asyncio
import contextlib
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from app.domain.entities import Task, TaskStatus


class Event(ABC):
    """Base event class"""

    @abstractmethod
    def get_event_type(self) -> str:
        """Return the type of event"""
        pass


@dataclass
class TaskCreatedEvent(Event):
    """Event fired when a task is created"""

    task_id: str
    task: Task

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "task_created"


@dataclass
class TaskUpdatedEvent(Event):
    """Event fired when a task is updated"""

    task_id: str
    task: Task
    old_status: TaskStatus
    new_status: TaskStatus

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "task_updated"


@dataclass
class TaskProgressEvent(Event):
    """Event fired when task progress is updated"""

    task_id: str
    progress: float

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "task_progress"


class EventBus:
    """Event bus for publishing and subscribing to events"""

    def __init__(self):
        self._handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._handlers:
            with contextlib.suppress(ValueError):
                self._handlers[event_type].remove(handler)

    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        event_type = type(event)
        if event_type in self._handlers:
            # Execute all handlers concurrently
            tasks = []
            for handler in self._handlers[event_type]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Wrap sync function in async
                    tasks.append(asyncio.create_task(self._run_sync_handler(handler, event)))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_sync_handler(self, handler: Callable, event: Event):
        """Run synchronous handler in async context"""
        try:
            handler(event)
        except Exception as e:
            # Log error but don't raise to prevent breaking other handlers
            print(f"Error in event handler: {e}")


# Global event bus instance
event_bus = EventBus()
