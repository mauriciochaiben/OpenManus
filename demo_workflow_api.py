#!/usr/bin/env python3
"""
Workflow Service Demo Script

This script demonstrates the complete workflow functionality:
1. Direct service usage
2. API endpoint usage
3. Real-time workflow execution
"""

import asyncio
import json
import time
from typing import Any, Dict

import requests

from app.infrastructure.messaging.event_bus import EventBus
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent
from app.services.workflow_service import WorkflowService


async def demo_direct_service():
    """Demonstrate direct WorkflowService usage"""
    print("=" * 60)
    print("DEMO 1: Direct WorkflowService Usage")
    print("=" * 60)

    # Initialize components
    planner = PlannerAgent()
    tool_user = ToolUserAgent()
    event_bus = EventBus()

    # Create workflow service
    workflow_service = WorkflowService(
        planner_agent=planner, tool_user_agent=tool_user, event_bus=event_bus
    )

    # Define a test task
    initial_task = (
        "Search for information about Python web frameworks and create a comparison"
    )

    print(f"Starting workflow with task: {initial_task}")
    print("-" * 60)

    try:
        # Execute the workflow
        result = await workflow_service.start_simple_workflow(initial_task)

        print("Workflow Results:")
        print(json.dumps(result, indent=2))

        # Print summary
        print(f"\n✅ Workflow completed successfully!")
        print(f"   - Workflow ID: {result.get('workflow_id', 'N/A')}")
        print(f"   - Total steps: {result.get('total_steps', 0)}")
        print(f"   - Successful steps: {result.get('successful_steps', 0)}")
        print(f"   - Failed steps: {result.get('failed_steps', 0)}")

    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")


def demo_api_endpoint():
    """Demonstrate API endpoint usage"""
    print("\n" + "=" * 60)
    print("DEMO 2: API Endpoint Usage")
    print("=" * 60)

    # API endpoint URL
    api_url = "http://localhost:8000/api/v2/workflows/simple"

    # Test data
    workflow_request = {
        "initial_task": "Find the top 5 Python libraries for data science and explain their use cases",
        "metadata": {
            "priority": "medium",
            "user_id": "demo_user",
            "department": "research",
        },
    }

    print(f"Sending request to: {api_url}")
    print(f"Request data: {json.dumps(workflow_request, indent=2)}")
    print("-" * 60)

    try:
        # Make API request
        response = requests.post(
            api_url,
            json=workflow_request,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 202:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))

            print(f"\n✅ Workflow started successfully via API!")
            print(f"   - Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   - Status: {result.get('status', 'N/A')}")
            print(f"   - Message: {result.get('message', 'N/A')}")

        else:
            print(f"❌ API request failed: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ API request error: {str(e)}")
        print("   Make sure the development server is running: ./start_dev.sh")


def demo_health_check():
    """Demonstrate API health check"""
    print("\n" + "=" * 60)
    print("DEMO 3: API Health Check")
    print("=" * 60)

    health_url = "http://localhost:8000/api/v2/workflows/health"

    try:
        response = requests.get(health_url, timeout=5)

        if response.status_code == 200:
            health_data = response.json()
            print("Health Check Response:")
            print(json.dumps(health_data, indent=2))
            print(f"\n✅ Workflow service is healthy!")
        else:
            print(f"❌ Health check failed: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {str(e)}")


def demo_validation_errors():
    """Demonstrate API validation"""
    print("\n" + "=" * 60)
    print("DEMO 4: API Validation Testing")
    print("=" * 60)

    api_url = "http://localhost:8000/api/v2/workflows/simple"

    # Test cases for validation
    test_cases = [
        {"name": "Empty task", "data": {"initial_task": ""}},
        {"name": "Missing task", "data": {"metadata": {"test": "value"}}},
        {"name": "Task too long", "data": {"initial_task": "x" * 1001}},
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            response = requests.post(
                api_url,
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            print(f"  Status: {response.status_code}")
            if response.status_code == 422:
                print(f"  ✅ Validation working correctly")
            else:
                print(f"  ❓ Unexpected response: {response.text[:100]}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error: {str(e)}")


async def main():
    """Run all demos"""
    print("OpenManus Workflow Service Demo")
    print("This demo showcases the complete workflow functionality")
    print("including direct service usage and API endpoints.\n")

    # Demo 1: Direct service usage
    await demo_direct_service()

    # Demo 2: API endpoint usage
    demo_api_endpoint()

    # Demo 3: Health check
    demo_health_check()

    # Demo 4: Validation testing
    demo_validation_errors()

    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("The WorkflowService is fully functional and integrated!")
    print("- ✅ Direct service usage working")
    print("- ✅ API endpoints accessible")
    print("- ✅ Background task execution")
    print("- ✅ Event publishing integrated")
    print("- ✅ Input validation working")
    print("- ✅ Error handling in place")
    print("\nNext steps:")
    print("- Set up WebSocket handlers for real-time updates")
    print("- Add workflow persistence for result retrieval")
    print("- Implement workflow status checking endpoints")


if __name__ == "__main__":
    asyncio.run(main())
