"""
Tool User Agent for executing tools through the OpenManus tool registry.

This module implements the ToolUserAgent, responsible for executing tools
registered in the system's ToolRegistry based on task details provided.
"""

import json
from typing import Any, Dict, List, Optional

from app.agent.base_agent import BaseAgent
from app.logger import logger
from app.tool.registry import ToolRegistry


class ToolUserAgent(BaseAgent):
    """Agent specialized in executing tools through the tool registry.

    The ToolUserAgent receives task details that specify which tool to execute
    and with what arguments, then uses the ToolRegistry to locate and execute
    the appropriate tool instance.

    Attributes:
        tool_registry: The ToolRegistry instance for tool management and execution.
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize the ToolUserAgent with a ToolRegistry instance.

        Args:
            config: Dictionary containing optional configuration for the agent.
                   Can include tool-specific settings or execution parameters.

        Note:
            The ToolRegistry is injected as a dependency to enable tool
            discovery and execution capabilities.
        """
        self.tool_registry = ToolRegistry()
        self.config = config or {}
        logger.info("ToolUserAgent initialized with tool registry")

    async def run(self, task_details: Dict) -> Dict:
        """Execute a tool based on the provided task details.

        Args:
            task_details: Dictionary containing task execution details. Expected format:
                         {
                             "tool_name": str,  # Name of the tool to execute
                             "arguments": Dict,  # Arguments to pass to the tool
                             "timeout": Optional[int],  # Execution timeout in seconds
                             "context": Optional[Dict]  # Additional context data
                         }

        Returns:
            Dict: Execution result containing:
                 - success: Boolean indicating execution success/failure
                 - result: Tool execution output or error details
                 - message: Descriptive message about the execution
                 - metadata: Additional metadata (execution time, tool info, etc.)

        Raises:
            ValueError: When required task details are missing or invalid
            Exception: When tool execution fails unexpectedly
        """
        try:
            # Validate required task details
            if not isinstance(task_details, dict):
                raise ValueError("task_details must be a dictionary")

            tool_name = task_details.get("tool_name")
            if not tool_name:
                raise ValueError("tool_name is required in task_details")

            arguments = task_details.get("arguments", {})
            if not isinstance(arguments, dict):
                raise ValueError("arguments must be a dictionary")

            # Get the tool from registry
            tool_instance = self.tool_registry.get_tool(tool_name)
            if tool_instance is None:
                available_tools = self.tool_registry.list_tools()
                return {
                    "success": False,
                    "result": None,
                    "message": f"Tool '{tool_name}' not found in registry",
                    "metadata": {
                        "available_tools": available_tools,
                        "requested_tool": tool_name,
                        "execution_time": 0,
                    },
                }

            logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")

            # Execute the tool
            import time

            start_time = time.time()

            try:
                tool_result = await tool_instance.execute(**arguments)
                execution_time = time.time() - start_time

                return {
                    "success": True,
                    "result": tool_result,
                    "message": f"Tool '{tool_name}' executed successfully",
                    "metadata": {
                        "tool_name": tool_name,
                        "execution_time": execution_time,
                        "arguments_provided": list(arguments.keys()),
                    },
                }

            except Exception as tool_error:
                execution_time = time.time() - start_time
                logger.error(f"Tool '{tool_name}' execution failed: {str(tool_error)}")

                return {
                    "success": False,
                    "result": None,
                    "message": f"Tool '{tool_name}' execution failed: {str(tool_error)}",
                    "metadata": {
                        "tool_name": tool_name,
                        "execution_time": execution_time,
                        "error_type": type(tool_error).__name__,
                        "arguments_provided": list(arguments.keys()),
                    },
                }

        except ValueError as ve:
            logger.error(f"Invalid task details for ToolUserAgent: {str(ve)}")
            return {
                "success": False,
                "result": None,
                "message": f"Invalid task details: {str(ve)}",
                "metadata": {"error_type": "ValueError", "execution_time": 0},
            }

        except Exception as e:
            logger.error(f"Unexpected error in ToolUserAgent.run: {str(e)}")
            return {
                "success": False,
                "result": None,
                "message": f"Unexpected error during tool execution: {str(e)}",
                "metadata": {"error_type": type(e).__name__, "execution_time": 0},
            }

    def get_capabilities(self) -> List[str]:
        """Return the capabilities of the ToolUserAgent.

        Returns:
            List[str]: List containing the agent's capabilities.
                      Returns ["tool_execution"] to indicate this agent
                      can execute tools from the tool registry.

        Note:
            This capability identifier is used by the task routing system
            to determine when this agent should be selected for execution.
        """
        return ["tool_execution"]

    def get_available_tools(self) -> List[str]:
        """Get a list of all available tools in the registry.

        Returns:
            List[str]: List of tool names currently registered in the tool registry.

        Note:
            This is a convenience method for inspecting which tools
            are available for execution.
        """
        return self.tool_registry.list_tools()

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a specific tool is available in the registry.

        Args:
            tool_name: The name of the tool to check for availability.

        Returns:
            bool: True if the tool is registered and available, False otherwise.
        """
        return self.tool_registry.is_registered(tool_name)
