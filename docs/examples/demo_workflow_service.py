#!/usr/bin/env python3
"""
Demo script to showcase WorkflowService functionality with both tool and generic steps.
"""

import asyncio
import json
import sys

from app.infrastructure.messaging.event_bus import event_bus
from app.services.workflow_service import (
    WorkflowCompletedEvent,
    WorkflowService,
    WorkflowStartedEvent,
)

sys.path.append(".")


class WorkflowEventSubscriber:
    """Simple event subscriber to demonstrate workflow event handling."""

    def __init__(self):
        self.events_received = []

    async def on_workflow_started(self, event: WorkflowStartedEvent):
        """Handle workflow started events."""
        print(f"🚀 EVENT: Workflow {event.workflow_id} started")
        print(f"   Initial task: {event.initial_task}")
        self.events_received.append(("started", event))

    async def on_workflow_completed(self, event: WorkflowCompletedEvent):
        """Handle workflow completed events."""
        status = "✅ SUCCESS" if event.success else "❌ FAILED"
        print(f"🏁 EVENT: Workflow {event.workflow_id} completed - {status}")
        print(f"   Steps: {event.completed_steps}/{event.total_steps}")
        if event.error:
            print(f"   Error: {event.error}")
        self.events_received.append(("completed", event))


async def test_comprehensive_workflow():
    """Test WorkflowService with a comprehensive workflow example."""
    print("=" * 80)
    print("🔧 OPENMANUS WORKFLOW SERVICE DEMONSTRATION")
    print("=" * 80)

    # Setup event subscriber
    subscriber = WorkflowEventSubscriber()
    event_bus.subscribe(WorkflowStartedEvent, subscriber.on_workflow_started)
    event_bus.subscribe(WorkflowCompletedEvent, subscriber.on_workflow_completed)

    # Create WorkflowService with event bus
    service = WorkflowService(event_bus=event_bus)

    print("\n1️⃣  Testing Basic Workflow (Generic Steps)")
    print("-" * 50)

    result1 = await service.start_simple_workflow("Create a project documentation")

    print(f"Workflow ID: {result1['workflow_id']}")
    print(f"Status: {result1['status']}")
    print(f"Success Rate: {result1['steps_executed']}/{result1['total_steps']}")

    print("\n2️⃣  Testing Mixed Workflow (Tool + Generic Steps)")
    print("-" * 50)

    # Create a custom workflow simulation to demonstrate tool detection
    # Since PlannerAgent generates Portuguese generic steps, we'll simulate
    # a workflow with mixed step types

    print("Simulating workflow with mixed step types...")

    # Test step classification
    mixed_steps = [
        "Search for latest Python frameworks",  # tool
        "Analyze project requirements",  # generic
        "Download documentation files",  # tool
        "Review code structure",  # generic
        "Query database for user data",  # tool
        "Create final report",  # generic
    ]

    print("\nStep Classification Results:")
    for i, step in enumerate(mixed_steps, 1):
        step_type = service._classify_step(step)
        tool_icon = "🔧" if step_type == "tool" else "📝"
        print(f"  {i}. {tool_icon} {step} [{step_type}]")

    print("\n3️⃣  Testing Error Handling")
    print("-" * 50)

    # Test workflow with an empty task
    try:
        result3 = await service.start_simple_workflow("")
        print(f"Empty task result: {result3['status']}")
    except Exception as e:
        print(f"Exception handled: {e}")

    print("\n4️⃣  Event Summary")
    print("-" * 50)
    print(f"Total events received: {len(subscriber.events_received)}")
    for event_type, event in subscriber.events_received:
        print(f"  - {event_type}: {event.workflow_id}")

    print("\n5️⃣  Service Configuration")
    print("-" * 50)
    print(f"Tool Keywords: {len(service.TOOL_KEYWORDS)} configured")
    print(f"Sample keywords: {list(service.TOOL_KEYWORDS)[:10]}")

    print("\n6️⃣  Final Workflow Results Analysis")
    print("-" * 50)

    if result1.get("final_result"):
        summary = result1["final_result"]["workflow_summary"]
        print("Workflow 1 Summary:")
        print(f"  - Total Steps: {summary['total_steps']}")
        print(f"  - Success Rate: {summary['success_rate']:.2%}")
        print(f"  - Status: {summary['overall_status']}")

    print("\n" + "=" * 80)
    print("✅ WORKFLOW SERVICE DEMONSTRATION COMPLETED")
    print("=" * 80)


async def test_tool_extraction():
    """Test the tool information extraction logic."""
    print("\n🔍 Tool Extraction Test")
    print("-" * 30)

    service = WorkflowService()

    test_cases = [
        "Search for Python documentation",
        "Download the latest version",
        "Read configuration file",
        "Send notification email",
        "Query user database",
    ]

    for case in test_cases:
        tool_info = service._extract_tool_info(case)
        print(f"\nStep: '{case}'")
        print(f"  Tool: {tool_info['tool_name']}")
        print(f"  Args: {json.dumps(tool_info['arguments'], indent=8)}")


if __name__ == "__main__":
    print("Starting WorkflowService comprehensive test...")

    # Run main workflow test
    asyncio.run(test_comprehensive_workflow())

    print("\n" + "=" * 50)

    # Run tool extraction test
    asyncio.run(test_tool_extraction())
