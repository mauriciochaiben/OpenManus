#!/usr/bin/env python3
"""
Simple agent creation test
"""

import asyncio
import sys

sys.path.append("/Users/mauriciochaiben/OpenManus")

from app.agent.manus import Manus
from app.logger import logger


async def test_simple_agent():
    """Test basic agent creation"""
    print("🧪 Testing Simple Agent Creation")
    print("=" * 40)

    try:
        print("🔄 Creating agent...")
        agent = Manus()
        print(f"✅ Agent created: {agent.name}")
        print(f"   LLM config: {agent.llm.config_name}")
        print(f"   Model: {agent.llm.model}")

        # Try a very simple operation
        print("\n🔄 Testing agent memory...")
        agent.memory.add_message({"role": "user", "content": "test"})
        print(f"   Memory has {len(agent.memory.messages)} messages")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_simple_agent())
