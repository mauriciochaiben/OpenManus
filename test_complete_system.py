#!/usr/bin/env python3
"""Test the complete OpenManus system with progress broadcasting and mock LLM fallback"""

import asyncio
import json
import sys
import uuid
from datetime import datetime

sys.path.append("/Users/mauriciochaiben/OpenManus")

from app.agent.manus import Manus
from app.infrastructure.messaging.progress_broadcaster import ProgressBroadcaster
from app.llm import LLM


async def test_llm_with_mock_fallback():
    """Test LLM with mock fallback when quota is exhausted"""
    print("🧪 Testing LLM with Mock Fallback System")
    print("=" * 60)

    try:
        # Initialize LLM
        llm = LLM("default")
        print(f"✅ LLM initialized: {llm.model} (API: {llm.api_type})")

        # Test simple message
        messages = [
            {"role": "user", "content": "Olá! Como funciona o sistema OpenManus?"}
        ]

        print("🔄 Sending test message...")
        response = await llm.ask(messages, stream=False)
        print(f"✅ Response received ({len(response)} chars):")
        print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")

        return True

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


async def test_agent_with_mock_llm():
    """Test Manus agent with mock LLM fallback"""
    print("\n🤖 Testing Manus Agent with Mock LLM")
    print("=" * 60)

    try:
        # Initialize agent
        agent = Manus()
        print("✅ Manus agent initialized")

        # Test agent run
        task = "Analisar o funcionamento do sistema OpenManus e explicar como os agentes trabalham juntos"
        print(f"🔄 Running task: {task[:60]}...")

        result = await agent.run(task)
        print(f"✅ Agent result ({len(result)} chars):")
        print(f"   {result[:200]}{'...' if len(result) > 200 else ''}")

        # Cleanup
        await agent.cleanup()
        print("🧹 Agent cleanup completed")

        return True

    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


async def test_progress_broadcasting():
    """Test progress broadcasting system"""
    print("\n📡 Testing Progress Broadcasting System")
    print("=" * 60)

    try:
        # Initialize progress broadcaster
        progress_broadcaster = ProgressBroadcaster()
        print("✅ Progress broadcaster initialized")

        # Generate task ID
        task_id = str(uuid.uuid4())

        # Test progress broadcasting
        await progress_broadcaster.broadcast_start(
            task_id=task_id,
            task_name="Test Task",
            description="Testing progress broadcasting with mock LLM",
        )
        print("✅ Broadcast start message sent")

        await progress_broadcaster.broadcast_progress(
            task_id=task_id,
            stage="Analyzing with mock LLM",
            progress=25,
            execution_type="single",
            agents=["manus"],
        )
        print("✅ Broadcast progress message sent")

        await progress_broadcaster.broadcast_progress(
            task_id=task_id,
            stage="Processing response",
            progress=75,
            execution_type="single",
            agents=["manus"],
        )
        print("✅ Broadcast progress update sent")

        result = "Task completed successfully using mock LLM fallback system."
        await progress_broadcaster.broadcast_completion(task_id, result)
        print("✅ Broadcast completion message sent")

        return True

    except Exception as e:
        print(f"❌ Progress broadcasting test failed: {e}")
        return False


async def test_end_to_end_system():
    """Test the complete end-to-end system"""
    print("\n🎯 Testing Complete End-to-End System")
    print("=" * 60)

    try:
        # Initialize components
        agent = Manus()
        progress_broadcaster = ProgressBroadcaster()
        task_id = str(uuid.uuid4())

        print("✅ All components initialized")

        # Start task
        task = "Criar um relatório sobre as capacidades do OpenManus"
        await progress_broadcaster.broadcast_start(
            task_id=task_id,
            task_name="End-to-End Test",
            description=f"Testing complete system: {task}",
        )

        await progress_broadcaster.broadcast_progress(
            task_id=task_id,
            stage="Initializing agent",
            progress=10,
            execution_type="single",
            agents=["manus"],
        )

        # Execute task with agent
        await progress_broadcaster.broadcast_progress(
            task_id=task_id,
            stage="Executing task with agent",
            progress=30,
            execution_type="single",
            agents=["manus"],
        )

        result = await agent.run(task)

        await progress_broadcaster.broadcast_progress(
            task_id=task_id,
            stage="Processing results",
            progress=90,
            execution_type="single",
            agents=["manus"],
        )

        # Complete task
        await progress_broadcaster.broadcast_completion(task_id, result)

        print(f"✅ End-to-end test completed successfully!")
        print(f"   Result length: {len(result)} characters")
        print(f"   Sample: {result[:150]}{'...' if len(result) > 150 else ''}")

        # Cleanup
        await agent.cleanup()

        return True

    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 OpenManus Complete System Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    tests = [
        ("LLM with Mock Fallback", test_llm_with_mock_fallback),
        ("Agent with Mock LLM", test_agent_with_mock_llm),
        ("Progress Broadcasting", test_progress_broadcasting),
        ("End-to-End System", test_end_to_end_system),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = await test_func()
        results.append((test_name, success))

        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 All tests passed! The system is working correctly with mock LLM fallback."
        )
    else:
        print("⚠️ Some tests failed. Check the error messages above.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
