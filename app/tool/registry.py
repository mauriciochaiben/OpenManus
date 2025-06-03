"""Tool registry for managing and organizing tools in the OpenManus system."""

from typing import Optional

from app.logger import logger
from app.tool.base import BaseTool


class ToolRegistry:
    """
    A singleton registry for managing tool instances in the OpenManus system.

    This registry provides a centralized way to register, retrieve, and list tools,
    making it easier to manage tool dependencies and discovery across the application.
    """

    _instance: Optional["ToolRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "ToolRegistry":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the tool registry."""
        if not self._initialized:
            self._tools: dict[str, BaseTool] = {}
            self._initialized = True
            logger.info("Tool registry initialized")

    def register_tool(self, tool_name: str, tool_instance: BaseTool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool_name (str): The name to register the tool under
            tool_instance (BaseTool): The tool instance to register

        Raises:
            ValueError: If tool_name is empty or tool_instance is not a BaseTool
            TypeError: If tool_instance is not an instance of BaseTool
        """
        if not tool_name or not isinstance(tool_name, str):
            raise ValueError("Tool name must be a non-empty string")

        if not isinstance(tool_instance, BaseTool):
            raise TypeError("Tool instance must be an instance of BaseTool")

        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' is already registered. Overwriting existing registration.")

        self._tools[tool_name] = tool_instance
        logger.info(f"Tool '{tool_name}' registered successfully")

    def get_tool(self, tool_name: str) -> BaseTool | None:
        """
        Retrieve a tool from the registry by name.

        Args:
            tool_name (str): The name of the tool to retrieve

        Returns:
            Optional[BaseTool]: The tool instance if found, None otherwise
        """
        if not tool_name or not isinstance(tool_name, str):
            logger.warning("Tool name must be a non-empty string")
            return None

        tool = self._tools.get(tool_name)
        if tool is None:
            logger.debug(f"Tool '{tool_name}' not found in registry")

        return tool

    def list_tools(self) -> list[str]:
        """
        Get a list of all registered tool names.

        Returns:
            List[str]: A list of all registered tool names, sorted alphabetically
        """
        return sorted(self._tools.keys())

    def unregister_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            tool_name (str): The name of the tool to remove

        Returns:
            bool: True if the tool was removed, False if it wasn't found
        """
        if not tool_name or not isinstance(tool_name, str):
            logger.warning("Tool name must be a non-empty string")
            return False

        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Tool '{tool_name}' unregistered successfully")
            return True
        logger.warning(f"Cannot unregister tool '{tool_name}': not found in registry")
        return False

    def is_registered(self, tool_name: str) -> bool:
        """
        Check if a tool is registered in the registry.

        Args:
            tool_name (str): The name of the tool to check

        Returns:
            bool: True if the tool is registered, False otherwise
        """
        return tool_name in self._tools

    def clear(self) -> None:
        """
        Clear all tools from the registry.

        This method should be used carefully as it removes all registered tools.
        """
        tool_count = len(self._tools)
        self._tools.clear()
        logger.info(f"Tool registry cleared. Removed {tool_count} tools.")

    def get_tool_count(self) -> int:
        """
        Get the number of registered tools.

        Returns:
            int: The number of registered tools
        """
        return len(self._tools)

    def get_tools_by_type(self, tool_type: type[BaseTool]) -> list[BaseTool]:
        """
        Get all tools of a specific type.

        Args:
            tool_type (Type[BaseTool]): The type of tools to retrieve

        Returns:
            List[BaseTool]: A list of tools that are instances of the specified type
        """
        return [tool for tool in self._tools.values() if isinstance(tool, tool_type)]

    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool name is in the registry."""
        return tool_name in self._tools

    def __iter__(self):
        """Iterate over tool names."""
        return iter(self._tools.keys())

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"ToolRegistry({len(self._tools)} tools: {list(self._tools.keys())})"


# Global registry instance for convenience
tool_registry = ToolRegistry()


def initialize_basic_tools() -> None:
    """
    Initialize and register basic tools in the registry.

    This function sets up the basic tools that are commonly used
    throughout the OpenManus system.
    """
    # Import here to avoid circular imports
    from app.tool.basic_tools import WebSearchTool

    # Register the WebSearchTool
    web_search_tool = WebSearchTool()
    tool_registry.register_tool("web_search", web_search_tool)

    logger.info("Basic tools initialized and registered")


# Initialize basic tools when the module is imported
initialize_basic_tools()
