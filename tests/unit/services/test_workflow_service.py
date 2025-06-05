"""
Unit tests for WorkflowService.

This module contains comprehensive unit tests for the WorkflowService class,
testing workflow orchestration, step classification, tool execution, and event publishing.
"""

from unittest.mock import AsyncMock

import pytest
pytest.importorskip("openai")

from app.infrastructure.messaging.event_bus import EventBus
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent
from app.services.workflow_service import (
    WorkflowCompletedEvent,
    WorkflowService,
    WorkflowStartedEvent,
    WorkflowStepCompletedEvent,
    WorkflowStepStartedEvent,
)


class TestWorkflowService:
    """Test cases for WorkflowService functionality."""

    @pytest.fixture
    def mock_planner_agent(self):
        """Create a mock PlannerAgent for testing."""
        mock_agent = AsyncMock(spec=PlannerAgent)
        mock_agent.run.return_value = {
            "status": "success",
            "steps": [
                "Step 1: Analyze requirements",
                "Step 2: Search for documentation",
                "Step 3: Create implementation",
                "Step 4: Test the solution",
                "Step 5: Deploy the application",
            ],
            "metadata": {
                "original_task": "test task",
                "num_steps": 5,
                "planning_strategy": "sequential",
                "complexity": "medium",
            },
        }
        return mock_agent

    @pytest.fixture
    def mock_tool_user_agent(self):
        """Create a mock ToolUserAgent for testing."""
        mock_agent = AsyncMock(spec=ToolUserAgent)
        mock_agent.run.return_value = {
            "success": True,
            "result": {
                "tool_name": "web_search",
                "output": "Search completed successfully",
                "data": ["result1", "result2", "result3"],
            },
            "message": "Tool executed successfully",
        }
        return mock_agent

    @pytest.fixture
    def mock_event_bus(self):
        """Create a mock EventBus for testing."""
        return AsyncMock(spec=EventBus)

    @pytest.fixture
    def workflow_service(self, mock_planner_agent, mock_tool_user_agent, mock_event_bus):
        """Create a WorkflowService instance with mocked dependencies."""
        return WorkflowService(
            planner_agent=mock_planner_agent,
            tool_user_agent=mock_tool_user_agent,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_start_simple_workflow_success(self, workflow_service, mock_event_bus):
        """Test successful workflow execution."""
        result = await workflow_service.start_simple_workflow("Create a web application")

        # Verify result structure
        assert result["status"] == "success"
        assert result["steps_executed"] == 5
        assert result["total_steps"] == 5
        assert len(result["results"]) == 5
        assert result["final_result"] is not None
        assert "workflow_id" in result

        # Verify workflow events were published
        assert mock_event_bus.publish.call_count >= 2  # At least started and completed

        # Check that WorkflowStartedEvent was published
        started_event_call = mock_event_bus.publish.call_args_list[0]
        started_event = started_event_call[0][0]
        assert isinstance(started_event, WorkflowStartedEvent)
        assert started_event.initial_task == "Create a web application"

        # Check that WorkflowCompletedEvent was published
        completed_event_call = mock_event_bus.publish.call_args_list[-1]
        completed_event = completed_event_call[0][0]
        assert isinstance(completed_event, WorkflowCompletedEvent)
        assert completed_event.success is True
        assert completed_event.total_steps == 5
        assert completed_event.completed_steps == 5

    @pytest.mark.asyncio
    async def test_start_simple_workflow_planner_failure(self, workflow_service, mock_planner_agent):
        """Test workflow execution when planner fails."""
        mock_planner_agent.run.return_value = {
            "status": "error",
            "message": "Planning failed",
            "steps": [],
        }

        result = await workflow_service.start_simple_workflow("Invalid task")

        assert result["status"] == "error"
        assert result["steps_executed"] == 0
        assert result["total_steps"] == 0
        assert "Planning failed" in result["error"]

    @pytest.mark.asyncio
    async def test_start_simple_workflow_partial_success(self, workflow_service, mock_tool_user_agent):
        """Test workflow execution with some failing steps."""
        # Make tool execution fail - only step 2 ("Search for documentation") will use the tool
        mock_tool_user_agent.run.return_value = {
            "success": False,
            "result": None,
            "message": "Tool search failed",
        }

        result = await workflow_service.start_simple_workflow("Test partial failure")

        assert result["status"] == "partial_success"
        assert result["steps_executed"] == 4  # 4 out of 5 successful (step 2 fails)
        assert result["total_steps"] == 5

        # Check that one step failed (the search step)
        failed_steps = [r for r in result["results"] if not r["success"]]
        assert len(failed_steps) == 1
        assert "Search for documentation" in failed_steps[0]["description"]

    def test_classify_step_tool_detection(self, workflow_service):
        """Test step classification for tool detection."""
        # Tool-requiring steps
        tool_steps = [
            "Search for Python documentation",
            "Download the latest version",
            "Read configuration file",
            "Call the REST API",
            "Query the database",
            "Send email notification",
            "Fetch data from server",
            "Save results to file",
        ]

        for step in tool_steps:
            assert workflow_service._classify_step(step) == "tool"

        # Generic steps
        generic_steps = [
            "Analyze the requirements",
            "Design the architecture",
            "Review the code",
            "Plan the implementation",
            "Validate the results",
        ]

        for step in generic_steps:
            assert workflow_service._classify_step(step) == "generic"

    def test_extract_tool_info_web_search(self, workflow_service):
        """Test tool information extraction for web search."""
        step = "Search for Python tutorials online"
        tool_info = workflow_service._extract_tool_info(step)

        assert tool_info["tool_name"] == "web_search"
        assert "Python tutorials online" in tool_info["arguments"]["query"]
        assert tool_info["arguments"]["max_results"] == 5
        assert tool_info["timeout"] == 30

    def test_extract_tool_info_file_operations(self, workflow_service):
        """Test tool information extraction for file operations."""
        read_step = "Read the configuration file"
        read_info = workflow_service._extract_tool_info(read_step)

        assert read_info["tool_name"] == "file_handler"
        assert read_info["arguments"]["operation"] == "read"

        write_step = "Write data to output file"
        write_info = workflow_service._extract_tool_info(write_step)

        assert write_info["tool_name"] == "file_handler"
        assert write_info["arguments"]["operation"] == "write"

    def test_extract_tool_info_generic(self, workflow_service):
        """Test tool information extraction for generic tools."""
        step = "Calculate the statistical average"
        tool_info = workflow_service._extract_tool_info(step)

        assert tool_info["tool_name"] == "generic_tool"
        assert tool_info["arguments"]["description"] == step
        assert tool_info["arguments"]["action"] == "execute"

    @pytest.mark.asyncio
    async def test_execute_generic_step(self, workflow_service):
        """Test execution of generic steps."""
        result = await workflow_service._execute_generic_step("Analyze the data patterns")

        assert result["success"] is True
        assert result["result"]["step_type"] == "generic"
        assert "Analyze the data patterns" in result["result"]["description"]
        assert result["message"] == "Generic step executed successfully"

    @pytest.mark.asyncio
    async def test_execute_tool_step_success(self, workflow_service, mock_tool_user_agent):
        """Test successful tool step execution."""
        result = await workflow_service._execute_tool_step("Search for documentation")

        assert result["success"] is True
        assert result["result"]["tool_name"] == "web_search"
        assert mock_tool_user_agent.run.called

    @pytest.mark.asyncio
    async def test_execute_tool_step_failure(self, workflow_service, mock_tool_user_agent):
        """Test tool step execution failure."""
        mock_tool_user_agent.run.side_effect = Exception("Tool execution failed")

        result = await workflow_service._execute_tool_step("Search for documentation")

        assert result["success"] is False
        assert result["result"] is None
        assert "Tool execution failed" in result["message"]

    def test_aggregate_results_all_success(self, workflow_service):
        """Test result aggregation when all steps succeed."""
        step_results = [
            {"success": True, "result": "result1", "message": "ok"},
            {"success": True, "result": "result2", "message": "ok"},
            {"success": True, "result": "result3", "message": "ok"},
        ]

        final_result = workflow_service._aggregate_results(step_results)

        assert final_result["workflow_summary"]["total_steps"] == 3
        assert final_result["workflow_summary"]["successful_steps"] == 3
        assert final_result["workflow_summary"]["failed_steps"] == 0
        assert final_result["workflow_summary"]["success_rate"] == 1.0
        assert final_result["overall_status"] == "success"

    def test_aggregate_results_partial_success(self, workflow_service):
        """Test result aggregation with partial success."""
        step_results = [
            {"success": True, "result": "result1", "message": "ok"},
            {"success": False, "result": None, "message": "failed"},
            {"success": True, "result": "result3", "message": "ok"},
        ]

        final_result = workflow_service._aggregate_results(step_results)

        assert final_result["workflow_summary"]["total_steps"] == 3
        assert final_result["workflow_summary"]["successful_steps"] == 2
        assert final_result["workflow_summary"]["failed_steps"] == 1
        assert final_result["workflow_summary"]["success_rate"] == 2 / 3
        assert final_result["overall_status"] == "partial_success"

    def test_create_error_result(self, workflow_service):
        """Test error result creation."""
        error_result = workflow_service._create_error_result("test-workflow-id", "Test error message", 2, 5)

        assert error_result["workflow_id"] == "test-workflow-id"
        assert error_result["status"] == "error"
        assert error_result["steps_executed"] == 2
        assert error_result["total_steps"] == 5
        assert error_result["error"] == "Test error message"
        assert error_result["metadata"]["error_occurred"] is True

    @pytest.mark.asyncio
    async def test_workflow_without_event_bus(self, mock_planner_agent, mock_tool_user_agent):
        """Test workflow execution without event bus."""
        service = WorkflowService(
            planner_agent=mock_planner_agent,
            tool_user_agent=mock_tool_user_agent,
            event_bus=None,
        )

        result = await service.start_simple_workflow("Test without events")

        # Should still work without event publishing
        assert result["status"] == "success"
        assert result["steps_executed"] == 5

    def test_tool_keywords_coverage(self, workflow_service):
        """Test that tool keywords cover expected domains."""
        keywords = workflow_service.TOOL_KEYWORDS

        # Should contain search-related keywords
        assert any(kw in keywords for kw in ["search", "query", "find"])

        # Should contain file-related keywords
        assert any(kw in keywords for kw in ["file", "read", "write"])

        # Should contain API-related keywords
        assert any(kw in keywords for kw in ["api", "call", "request"])

        # Should contain database-related keywords
        assert any(kw in keywords for kw in ["database", "sql", "query"])

        # Should have reasonable number of keywords
        assert len(keywords) > 20
        assert len(keywords) < 100

    @pytest.mark.asyncio
    async def test_workflow_events_order(self, workflow_service, mock_event_bus):
        """Test that workflow events are published in correct order."""
        await workflow_service.start_simple_workflow("Test event order")

        # Extract all published events
        published_events = [call[0][0] for call in mock_event_bus.publish.call_args_list]

        # Should start with WorkflowStartedEvent
        assert isinstance(published_events[0], WorkflowStartedEvent)

        # Should end with WorkflowCompletedEvent
        assert isinstance(published_events[-1], WorkflowCompletedEvent)

        # Should have step events in between
        step_events = [
            e for e in published_events if isinstance(e, WorkflowStepStartedEvent | WorkflowStepCompletedEvent)
        ]
        assert len(step_events) > 0

    @pytest.mark.asyncio
    async def test_decompose_task_error_handling(self, workflow_service, mock_planner_agent):
        """Test error handling in task decomposition."""
        mock_planner_agent.run.side_effect = Exception("Planner crashed")

        result = await workflow_service._decompose_task("Test task")

        assert result["status"] == "error"
        assert "Task decomposition failed" in result["message"]
        assert result["steps"] == []


class TestWorkflowEvents:
    """Test cases for workflow event classes."""

    def test_workflow_started_event(self):
        """Test WorkflowStartedEvent creation."""
        event = WorkflowStartedEvent(workflow_id="test-id", initial_task="Test task")

        assert event.workflow_id == "test-id"
        assert event.initial_task == "Test task"

    def test_workflow_step_started_event(self):
        """Test WorkflowStepStartedEvent creation."""
        event = WorkflowStepStartedEvent(
            workflow_id="test-id",
            step_number=1,
            step_description="First step",
            step_type="tool",
        )

        assert event.workflow_id == "test-id"
        assert event.step_number == 1
        assert event.step_description == "First step"
        assert event.step_type == "tool"

    def test_workflow_step_completed_event(self):
        """Test WorkflowStepCompletedEvent creation."""
        event = WorkflowStepCompletedEvent(
            workflow_id="test-id",
            step_number=1,
            step_description="First step",
            step_type="tool",
            success=True,
            result={"output": "success"},
            error=None,
        )

        assert event.workflow_id == "test-id"
        assert event.step_number == 1
        assert event.success is True
        assert event.result == {"output": "success"}
        assert event.error is None

    def test_workflow_completed_event(self):
        """Test WorkflowCompletedEvent creation."""
        event = WorkflowCompletedEvent(
            workflow_id="test-id",
            success=True,
            total_steps=5,
            completed_steps=5,
            final_result={"summary": "All done"},
            successful_steps=["step1", "step2", "step3", "step4", "step5"],
            failed_steps=[],
            final_status="completed",
        )

        assert event.workflow_id == "test-id"
        assert event.success is True
        assert event.total_steps == 5
        assert event.completed_steps == 5
        assert event.final_result == {"summary": "All done"}


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
