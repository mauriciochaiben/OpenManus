from abc import ABC


class BaseTool(ABC):
    """Base class for all tools."""

    # Safety classification
    is_safe: bool = True  # Override to False for unsafe tools
    requires_sandbox: bool = (
        False  # Override to True for tools that should always be sandboxed
    )

    # ...existing code...
