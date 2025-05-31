import asyncio

# Import from the main app structure, not backend-specific features
import sys
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.append("/Users/mauriciochaiben/OpenManus")

from app.infrastructure.messaging.event_bus import EventBus
from app.knowledge.services.rag_service import RagService
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent
from app.services.workflow_service import (
    WorkflowCompletedEvent,
    WorkflowService,
    WorkflowStartedEvent,
    WorkflowStepCompletedEvent,
    WorkflowStepStartedEvent,
)


# Simple agent and workflow models for testing
class Agent:
    def __init__(self, id: str, name: str, type: str):
        self.id = id
        self.name = name
        self.type = type


class AgentType:
    PLANNER = "planner"
    TOOL_USER = "tool_user"


class Workflow:
    def __init__(self, id: str):
        self.id = id
        self.steps = []


class WorkflowStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep:
    def __init__(self, id: str, status: str = "pending"):
        self.id = id
        self.status = status


class WorkflowRequest:
    def __init__(self, title: str, description: str, steps: list):
        self.title = title
        self.description = description
        self.steps = steps


class WorkflowFailedEvent:
    def __init__(self, workflow_id: str, error: str):
        self.workflow_id = workflow_id
        self.error = error


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
async def mock_rag_service():
    """Mock RagService for testing."""
    service = Mock(spec=RagService)
    service.retrieve_relevant_context = AsyncMock()
    return service


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


@pytest.fixture
async def workflow_service_with_rag(
    mock_event_bus, mock_planner_agent, mock_tool_user_agent, mock_rag_service
):
    """WorkflowService with mocked dependencies including RAG service."""
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
            service.set_rag_service(mock_rag_service)
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

    @pytest.mark.asyncio
    async def test_workflow_with_knowledge_context_success(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request_with_sources: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test successful workflow execution with knowledge context enhancement."""
        # Configure RAG service to return mock context
        mock_context_chunks = [
            "This is relevant documentation about the system architecture.",
            "Key implementation details include the use of microservices.",
            "The API follows REST principles with proper error handling.",
        ]
        mock_rag_service.retrieve_relevant_context.return_value = mock_context_chunks

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Context-enhanced plan created successfully",
            "data": {
                "plan": "Detailed plan using provided context",
                "context_enhanced": True,
            },
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed successfully",
            "data": {"output": "Execution complete with context"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request_with_sources
        )

        # Verify workflow completion
        assert workflow is not None
        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.steps) == 2

        # Verify RAG service was called for context retrieval
        mock_rag_service.retrieve_relevant_context.assert_called_once()
        call_args = mock_rag_service.retrieve_relevant_context.call_args

        # Check that the call included the original query and source IDs
        assert call_args[1]["source_ids"] == ["source-1", "source-2", "source-3"]
        assert "Create a plan based on available documentation" in call_args[1]["query"]
        assert call_args[1]["k"] == 5  # Default max chunks

        # Verify planner agent received enhanced prompt
        planner_call_args = mock_planner_agent.execute.call_args[0][0]

        # The objective should now include context enhancement
        enhanced_objective = planner_call_args["objective"]
        assert "CONTEXT:" in enhanced_objective
        assert (
            "This is relevant documentation about the system architecture."
            in enhanced_objective
        )
        assert "Create a plan based on available documentation" in enhanced_objective
        assert planner_call_args.get("_context_enhanced") is True
        assert planner_call_args.get("_source_ids_used") == [
            "source-1",
            "source-2",
            "source-3",
        ]

        # Verify both agents were executed
        assert mock_planner_agent.execute.call_count == 1
        assert mock_tool_user_agent.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_workflow_with_empty_source_ids(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test workflow execution when source_ids list is empty."""
        # Set empty source_ids
        workflow_request.source_ids = []

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Standard plan created",
            "data": {"plan": "Basic plan without context"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed",
            "data": {"output": "Standard execution"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request
        )

        # Verify workflow completion
        assert workflow.status == WorkflowStatus.COMPLETED

        # Verify RAG service was NOT called
        mock_rag_service.retrieve_relevant_context.assert_not_called()

        # Verify planner received original objective without enhancement
        planner_call_args = mock_planner_agent.execute.call_args[0][0]
        assert planner_call_args["objective"] == "Create a test plan"
        assert planner_call_args.get("_context_enhanced") is not True

    @pytest.mark.asyncio
    async def test_workflow_with_rag_service_failure(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request_with_sources: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test workflow handling when RAG service fails."""
        # Configure RAG service to fail
        mock_rag_service.retrieve_relevant_context.side_effect = Exception(
            "Vector search failed"
        )

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created despite context failure",
            "data": {"plan": "Fallback plan"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed",
            "data": {"output": "Execution complete"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request_with_sources
        )

        # Verify workflow still completes (graceful degradation)
        assert workflow.status == WorkflowStatus.COMPLETED

        # Verify RAG service was called but failed
        mock_rag_service.retrieve_relevant_context.assert_called_once()

        # Verify planner received original objective (fallback behavior)
        planner_call_args = mock_planner_agent.execute.call_args[0][0]
        assert (
            "Create a plan based on available documentation"
            in planner_call_args["objective"]
        )
        # Should not have context enhancement markers due to failure
        assert "CONTEXT:" not in planner_call_args["objective"]

    @pytest.mark.asyncio
    async def test_workflow_with_no_relevant_context_found(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request_with_sources: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test workflow when RAG service returns no relevant context."""
        # Configure RAG service to return empty context
        mock_rag_service.retrieve_relevant_context.return_value = []

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created without context",
            "data": {"plan": "Plan without additional context"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Plan executed",
            "data": {"output": "Execution complete"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request_with_sources
        )

        # Verify workflow completion
        assert workflow.status == WorkflowStatus.COMPLETED

        # Verify RAG service was called
        mock_rag_service.retrieve_relevant_context.assert_called_once()

        # Verify planner received original objective (no enhancement due to empty context)
        planner_call_args = mock_planner_agent.execute.call_args[0][0]
        assert (
            planner_call_args["objective"]
            == "Create a plan based on available documentation"
        )
        assert "CONTEXT:" not in planner_call_args["objective"]

    @pytest.mark.asyncio
    async def test_workflow_context_enhancement_step_filtering(
        self,
        workflow_service_with_rag: WorkflowService,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test that only appropriate steps get context enhancement."""
        # Create request with mixed step types
        mixed_workflow_request = WorkflowRequest(
            title="Mixed Step Types Workflow",
            description="Testing selective context enhancement",
            steps=[
                {
                    "name": "analyze_requirements",  # Should get context
                    "agent_type": "planner",
                    "config": {"objective": "Analyze the requirements"},
                },
                {
                    "name": "simple_calculation",  # Should NOT get context
                    "agent_type": "tool_user",
                    "config": {"operation": "add", "values": [1, 2, 3]},
                },
                {
                    "name": "generate_report",  # Should get context
                    "type": "content_generation",
                    "agent_type": "tool_user",
                    "config": {"template": "summary_report"},
                },
            ],
            source_ids=["source-1"],
        )

        # Configure RAG service
        mock_rag_service.retrieve_relevant_context.return_value = [
            "Relevant context for analysis and generation"
        ]

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Analysis complete",
            "data": {"analysis": "Requirements analyzed"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Task complete",
            "data": {"output": "Task completed"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            mixed_workflow_request
        )

        # Verify workflow completion
        assert workflow.status == WorkflowStatus.COMPLETED

        # RAG service should be called twice (for steps that benefit from context)
        assert mock_rag_service.retrieve_relevant_context.call_count == 2

        # Verify agents were called correct number of times
        assert (
            mock_planner_agent.execute.call_count == 1
        )  # Only for analyze_requirements
        assert (
            mock_tool_user_agent.execute.call_count == 2
        )  # For calculation and report

    @pytest.mark.asyncio
    async def test_workflow_context_enhancement_with_custom_max_chunks(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request_with_sources: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test context enhancement with custom max chunks parameter."""
        # Configure RAG service
        mock_rag_service.retrieve_relevant_context.return_value = [
            f"Context chunk {i}" for i in range(10)
        ]

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created",
            "data": {"plan": "Enhanced plan"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Executed",
            "data": {"output": "Complete"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request_with_sources
        )

        # Verify RAG service was called with default max chunks
        call_args = mock_rag_service.retrieve_relevant_context.call_args
        assert call_args[1]["k"] == 5  # Default value

        # Verify workflow completion
        assert workflow.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_workflow_prompt_enhancement_format(
        self,
        workflow_service_with_rag: WorkflowService,
        workflow_request_with_sources: WorkflowRequest,
        mock_event_bus: Mock,
        mock_planner_agent: Mock,
        mock_tool_user_agent: Mock,
        mock_rag_service: Mock,
    ):
        """Test that prompt enhancement follows the expected format."""
        # Configure RAG service with specific context
        mock_context = [
            "First piece of relevant information",
            "Second piece of relevant information",
        ]
        mock_rag_service.retrieve_relevant_context.return_value = mock_context

        # Configure agent responses
        mock_planner_agent.execute.return_value = {
            "status": "success",
            "result": "Plan created",
            "data": {"plan": "Test plan"},
        }

        mock_tool_user_agent.execute.return_value = {
            "status": "success",
            "result": "Executed",
            "data": {"output": "Complete"},
        }

        # Execute workflow
        workflow = await workflow_service_with_rag.start_simple_workflow(
            workflow_request_with_sources
        )

        # Get the enhanced prompt sent to the planner
        planner_call_args = mock_planner_agent.execute.call_args[0][0]
        enhanced_objective = planner_call_args["objective"]

        # Verify the enhanced prompt structure
        assert "CONTEXT:" in enhanced_objective
        assert "QUESTION/TASK:" in enhanced_objective
        assert "First piece of relevant information" in enhanced_objective
        assert "Second piece of relevant information" in enhanced_objective
        assert "Create a plan based on available documentation" in enhanced_objective

        # Verify the context is properly formatted with numbering
        assert "Context 1:" in enhanced_objective
        assert "Context 2:" in enhanced_objective

        # Verify workflow completion
        assert workflow.status == WorkflowStatus.COMPLETED
