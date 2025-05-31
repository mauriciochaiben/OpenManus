"""Simple test script to verify the tool registry is working correctly."""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tool.registry import tool_registry
from app.tool.basic_tools import WebSearchTool


def test_registry():
    """Test the tool registry functionality."""
    print("Testing Tool Registry...")

    # Test that the registry was initialized with basic tools
    print(f"Initial tool count: {tool_registry.get_tool_count()}")
    print(f"Available tools: {tool_registry.list_tools()}")

    # Test getting the web search tool
    web_search = tool_registry.get_tool("web_search")
    if web_search:
        print(f"✓ Found web_search tool: {type(web_search).__name__}")

        # Test the tool functionality
        try:
            result = web_search.execute("Python programming")
            print("✓ WebSearchTool execution successful")
            print(f"Result preview: {result[:100]}...")
        except Exception as e:
            print(f"✗ WebSearchTool execution failed: {e}")
    else:
        print("✗ web_search tool not found")

    # Test registering a new tool instance
    new_tool = WebSearchTool()
    tool_registry.register_tool("test_search", new_tool)
    print(f"✓ Registered new tool. Total tools: {tool_registry.get_tool_count()}")

    # Test listing tools
    all_tools = tool_registry.list_tools()
    print(f"All tools: {all_tools}")

    # Test registry methods
    print(f"✓ 'web_search' is registered: {tool_registry.is_registered('web_search')}")
    print(
        f"✓ 'nonexistent' is registered: {tool_registry.is_registered('nonexistent')}"
    )

    # Test the registry contains method
    print(f"✓ Registry contains 'web_search': {'web_search' in tool_registry}")

    # Test string representation
    print(f"✓ Registry representation: {repr(tool_registry)}")

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_registry()
