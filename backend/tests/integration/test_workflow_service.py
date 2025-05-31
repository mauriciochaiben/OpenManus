import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.features.agents.models.agent import Agent, AgentType
from app.features.workflows.models.workflow import (
    Workflow,
    WorkflowStatus,
    WorkflowStep,
)
from app.features.workflows.models.workflow_request import WorkflowRequest
from app.features.workflows.services.workflow_service import WorkflowService
from app.shared.events.event_bus import EventBus
from app.shared.events.workflow_events import (
    WorkflowCompletedEvent,
    WorkflowFailedEvent,
    WorkflowStartedEvent,
    WorkflowStepCompletedEvent,
    WorkflowStepStartedEvent,
)


@pytest.fixture
async def mock_event_bus():
    """Mock EventBus for testing."""
    event_bus = Mock(spec=EventBus)
    event_bus.publish = AsyncMock()
    event_bus.subscribe = Mock()
    return event_bus


@pytest.fixture
async def mock_planner_agent():
    """Mock PlannerAgent for testing."""
    agent = Mock(spec=Agent)
    agent.id = "planner-agent-1"
    agent.name = "Test Planner"
    agent.type = AgentType.PLANNER
    agent.execute = AsyncMock()
    return agent


@pytest.fixture
async def mock_tool_user_agent():
    """Mock ToolUserAgent for testing."""
    agent = Mock(spec=Agent)
    agent.id = "tool-user-agent-1"
    agent.name = "Test Tool User"
    agent.type = AgentType.TOOL_USER
    agent.execute = AsyncMock()
    return agent


@pytest.fixture
async def workflow_request():
    """Sample workflow request for testing."""
    return WorkflowRequest(
        title="Test Integration Workflow",
        description="Testing workflow service integration",
        steps=[
            {
                "name": "plan_task",
                "agent_type": "planner",
                "config": {"objective": "Create a test plan"},
            },
            {
                "name": "execute_plan",
                "agent_type": "tool_user",
                "config": {"tools": ["file_manager", "code_editor"]},
            },
        ],
    )


@pytest.fixture
async def workflow_service(mock_event_bus, mock_planner_agent, mock_tool_user_agent):
    """WorkflowService with mocked dependencies."""
    with patch(
        "app.features.workflows.services.workflow_service.EventBus"
    ) as mock_bus_class:
        mock_bus_class.return_value = mock_event_bus

        with patch(
            "app.features.agents.services.agent_service.AgentService"
        ) as mock_agent_service:
            mock_agent_service.return_value.get_agent.side_effect = lambda agent_type: {
                AgentType.PLANNER: mock_planner_agent,
                AgentType.TOOL_USER: mock_tool_user_agent,
            }.get(agent_type)

            service = WorkflowService()
            yield service


class TestWorkflowServiceIntegration:
    """Integration tests for WorkflowService."""

    @pytest.mark.asyncio
    async def test_start_simple_workflow_success(
        self,
        workflow_service: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
    ):
        """Test successful execution of a simple workflow."""
        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created successfully",
            "data": {"plan": "Test plan content"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed successfully",
            "data": {"output": "Execution complete"},
        }

        # Execute workflow
        workflow = await workflow_service.start_simple_workflow(workflow_request)

        # Verify workflow creation
        assert workflow is not None
        assert workflow.title == workflow_request.title
        assert workflow.description == workflow_request.description
        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.steps) == 2

        # Verify agent execution calls
        assert mock_planner_agent.execute.call_count == 1
        assert mock_tool_user_agent.execute.call_count == 1

        # Get the call arguments for agent executions
        planner_call_args = mock_planner_agent.execute.call_args[0]
        tool_user_call_args = mock_tool_user_agent.execute.call_args[0]

        assert planner_call_args[0]["objective"] == "Create a test plan"
        assert tool_user_call_args[0]["tools"] == ["file_manager", "code_editor"]

        # Verify event publishing sequence
        published_events = [
            call.args[0] for call in mock_event_bus.publish.call_args_list
        ]

        # Should have: WorkflowStarted, StepStarted, StepCompleted (x2), WorkflowCompleted
        assert len(published_events) == 5

        assert isinstance(published_events[0], WorkflowStartedEvent)
        assert published_events[0].workflow_id == workflow.id

        assert isinstance(published_events[1], WorkflowStepStartedEvent)
        assert published_events[1].step_name == "plan_task"

        assert isinstance(published_events[2], WorkflowStepCompletedEvent)
        assert published_events[2].step_name == "plan_task"
        assert published_events[2].status == "success"

        assert isinstance(published_events[3], WorkflowStepStartedEvent)
        assert published_events[3].step_name == "execute_plan"

        assert isinstance(published_events[4], WorkflowStepCompletedEvent)
        assert published_events[4].step_name == "execute_plan"
        assert published_events[4].status == "success"

    @pytest.mark.asyncio
    async def test_start_simple_workflow_agent_failure(
        self,
        workflow_service: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
    ):
        """Test workflow handling when an agent fails."""
        # Configure planner to succeed
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created successfully",
            "data": {"plan": "Test plan content"},
        }

        # Configure tool user to fail
        mock_tool_user_agent.execute.return_value = {
            "status": "error",
            "result": "Tool execution failed",
            "error": "Missing required tool",
        }

        # Execute workflow
        workflow = await workflow_service.start_simple_workflow(workflow_request)

        # Verify workflow failure handling
        assert workflow.status == WorkflowStatus.FAILED
        assert len(workflow.steps) == 2
        assert workflow.steps[0].status == "completed"
        assert workflow.steps[1].status == "failed"

        # Verify both agents were called
        assert mock_planner_agent.execute.call_count == 1
        assert mock_tool_user_agent.execute.call_count == 1

        # Verify event sequence includes failure
        published_events = [
            call.args[0] for call in mock_event_bus.publish.call_args_list
        ]

        # Should have: WorkflowStarted, StepStarted, StepCompleted, StepStarted, StepCompleted(failed), WorkflowFailed
        assert len(published_events) == 6

        assert isinstance(published_events[-1], WorkflowFailedEvent)
        assert published_events[-1].workflow_id == workflow.id
        assert "Tool execution failed" in published_events[-1].error

    @pytest.mark.asyncio
    async def test_start_simple_workflow_exception_handling(
        self,
        workflow_service: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
    ):
        """Test workflow handling when an agent raises an exception."""
        # Configure planner to raise exception
        mock_planner_agent.execute.side_effect = Exception("Agent crashed")

        # Execute workflow
        workflow = await workflow_service.start_simple_workflow(workflow_request)

        # Verify workflow failure handling
        assert workflow.status == WorkflowStatus.FAILED
        assert len(workflow.steps) == 2
        assert workflow.steps[0].status == "failed"
        assert workflow.steps[1].status == "pending"  # Never executed

        # Verify only planner was called
        assert mock_planner_agent.execute.call_count == 1
        assert mock_tool_user_agent.execute.call_count == 0

        # Verify failure event was published
        published_events = [
            call.args[0] for call in mock_event_bus.publish.call_args_list
        ]

        assert any(isinstance(event, WorkflowFailedEvent) for event in published_events)
        failure_event = next(
            event
            for event in published_events
            if isinstance(event, WorkflowFailedEvent)
        )
        assert "Agent crashed" in failure_event.error

    @pytest.mark.asyncio
    async def test_workflow_step_data_passing(
        self,
        workflow_service: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
    ):
        """Test that data is correctly passed between workflow steps."""
        # Configure planner to return data
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created",
            "data": {"plan": "Detailed plan", "priority": "high"},
        }

        # Configure tool user to succeed
        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed",
            "data": {"output": "Execution complete"},
        }

        # Execute workflow
        workflow = await workflow_service.start_simple_workflow(workflow_request)

        # Verify workflow completed successfully
        assert workflow.status == WorkflowStatus.COMPLETED

        # Verify that tool user received data from planner
        tool_user_call_args = mock_tool_user_agent.execute.call_args[0][0]

        # The tool user should receive previous step data
        assert "previous_step_data" in tool_user_call_args
        assert tool_user_call_args["previous_step_data"]["plan"] == "Detailed plan"
        assert tool_user_call_args["previous_step_data"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(
        self,
        workflow_service: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
    ):
        """Test that multiple workflows can be executed concurrently."""

        # Configure agents to succeed with delay
        async def delayed_execute(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate processing time
            return {
                "status": "success",
                "result": "Operation completed",
                "data": {"processed": True},
            }

        mock_planner_agent.execute.side_effect = delayed_execute
        mock_tool_user_agent.execute.side_effect = delayed_execute

        # Create multiple workflow requests
        requests = [
            WorkflowRequest(
                title=f"Workflow {i}",
                description=f"Test workflow {i}",
                steps=workflow_request.steps,
            )
            for i in range(3)
        ]

        # Execute workflows concurrently
        workflows = await asyncio.gather(
            *[workflow_service.start_simple_workflow(req) for req in requests]
        )

        # Verify all workflows completed
        assert len(workflows) == 3
        for workflow in workflows:
            assert workflow.status == WorkflowStatus.COMPLETED
            assert len(workflow.steps) == 2

        # Verify agents were called for each workflow
        assert mock_planner_agent.execute.call_count == 3
        assert mock_tool_user_agent.execute.call_count == 3

        # Verify events were published for all workflows
        published_events = [
            call.args[0] for call in mock_event_bus.publish.call_args_list
        ]

        # Should have events for all 3 workflows
        workflow_started_events = [
            e for e in published_events if isinstance(e, WorkflowStartedEvent)
        ]
        assert len(workflow_started_events) == 3

        workflow_completed_events = [
            e for e in published_events if isinstance(e, WorkflowCompletedEvent)
        ]
        assert len(workflow_completed_events) == 3

    @pytest.mark.asyncio
    async def test_workflow_with_empty_steps(
        self, workflow_service: WorkflowService, mock_event_bus: Mock
    ):
        """Test workflow creation with empty steps."""
        empty_request = WorkflowRequest(
            title="Empty Workflow", description="Workflow with no steps", steps=[]
        )

        # Execute workflow
        workflow = await workflow_service.start_simple_workflow(empty_request)

        # Verify workflow completed immediately
        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.steps) == 0

        # Verify events were published
        published_events = [
            call.args[0] for call in mock_event_bus.publish.call_args_list
        ]

        assert len(published_events) == 2  # Started and Completed
        assert isinstance(published_events[0], WorkflowStartedEvent)
        assert isinstance(published_events[1], WorkflowCompletedEvent)
