from abc import ABC, abstractmethod
from enum import Enum


class ToolCategory(str, Enum):
    """Categories for tools to help with security and sandboxing."""

    DEVELOPMENT = "development"
    SYSTEM = "system"
    ANALYSIS = "analysis"


class ToolResult:
    """Result of a tool execution."""

    pass


class BaseTool(ABC):
    """Base class for all tools."""

    # Safety classification
    is_safe: bool = True  # Override to False for unsafe tools
    requires_sandbox: bool = (
        False  # Override to True for tools that should always be sandboxed
    )
    category = ToolCategory.SYSTEM  # Default category, should be overridden

    @abstractmethod
    async def execute(self, **kwargs):
        """Execute the tool with given parameters."""
        pass
