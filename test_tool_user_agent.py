#!/usr/bin/env python3
"""
Test script for ToolUserAgent implementation.
"""

import asyncio

from app.roles.tool_user_agent import ToolUserAgent


async def main():
    """Main test function."""
    print("🚀 Starting ToolUserAgent tests...\n")

    # Initialize the agent
    agent = ToolUserAgent()
    print("✅ ToolUserAgent initialized successfully")
    print(f"📋 Capabilities: {agent.get_capabilities()}")
    print(f"🔧 Available tools: {agent.get_available_tools()}")
    print(f"🔍 Web search available: {agent.is_tool_available('web_search')}\n")

    # Test 1: Successful tool execution
    print("📝 Test 1: Successful tool execution")
    task_details = {
        "tool_name": "web_search",
        "arguments": {"query": "OpenManus AI assistant framework"},
    }

    result = await agent.run(task_details)
    print(f"   ✅ Success: {result['success']}")
    print(f"   💬 Message: {result['message']}")
    if result["success"] and result["result"]:
        output_preview = (
            result["result"].output[:100] + "..."
            if len(result["result"].output) > 100
            else result["result"].output
        )
        print(f"   📄 Result preview: {output_preview}")
    print(f"   ⏱️  Execution time: {result['metadata'].get('execution_time', 0):.3f}s\n")

    # Test 2: Missing required arguments
    print("📝 Test 2: Missing required arguments")
    task_details_invalid = {
        "tool_name": "web_search",
        "arguments": {},  # Missing 'query'
    }

    result2 = await agent.run(task_details_invalid)
    print(f"   ❌ Success: {result2['success']}")
    print(f"   💬 Message: {result2['message']}\n")

    # Test 3: Invalid tool name
    print("📝 Test 3: Invalid tool name")
    task_details_bad_tool = {
        "tool_name": "nonexistent_tool",
        "arguments": {"query": "test"},
    }

    result3 = await agent.run(task_details_bad_tool)
    print(f"   ❌ Success: {result3['success']}")
    print(f"   💬 Message: {result3['message']}")
    print(f"   🔧 Available tools: {result3['metadata'].get('available_tools')}\n")

    # Test 4: Invalid task details format
    print("📝 Test 4: Invalid task details format")
    result4 = await agent.run("invalid_string")  # Should be dict
    print(f"   ❌ Success: {result4['success']}")
    print(f"   💬 Message: {result4['message']}\n")

    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
