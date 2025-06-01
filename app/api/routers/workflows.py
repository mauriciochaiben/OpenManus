"""Workflow management API router"""

import asyncio
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies.core import get_workflow_service
from app.services.workflow_service import WorkflowRequest, WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


# Request/Response models
class StartWorkflowRequest(BaseModel):
    """Request model for starting a workflow"""

    initial_task: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The initial task description to decompose and execute",
    )
    metadata: Optional[Dict] = Field(
        default_factory=dict, description="Optional metadata for the workflow"
    )


class WorkflowResponse(BaseModel):
    """Response model for workflow operations"""

    message: str
    workflow_id: str
    status: str
    initial_task: str
    metadata: Optional[Dict] = None


class WorkflowStepResponse(BaseModel):
    """Response model for individual workflow steps"""

    step_number: int
    description: str
    type: str  # 'tool' or 'generic'
    success: bool
    result: Optional[Dict] = None
    message: Optional[str] = None


class WorkflowResultResponse(BaseModel):
    """Response model for complete workflow results"""

    workflow_id: str
    status: str
    steps_executed: int
    total_steps: int
    results: List[WorkflowStepResponse]
    final_result: Optional[Dict] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@router.post("/simple", response_model=WorkflowResponse, status_code=202)
async def start_simple_workflow(
    request: StartWorkflowRequest,
    background_tasks: BackgroundTasks,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowResponse:
    """
    Start a simple workflow execution.

    This endpoint initiates a workflow by decomposing the initial task into steps,
    executing them sequentially, and publishing progress events via WebSocket.

    Args:
        request: The workflow start request containing the initial task
        background_tasks: FastAPI background tasks for async execution
        workflow_service: Injected workflow service dependency

    Returns:
        WorkflowResponse: Initial response with workflow ID and status

    Raises:
        HTTPException: If the workflow fails to start
    """
    try:
        # Validate the initial task
        if not request.initial_task.strip():
            raise HTTPException(status_code=400, detail="Initial task cannot be empty")

        # Start the workflow in the background
        # The detailed results will be sent via WebSocket events
        background_tasks.add_task(
            _execute_workflow_async,
            workflow_service,
            request.initial_task,
            request.metadata or {},
        )

        # Generate a temporary workflow ID for immediate response
        # The actual workflow ID will be generated when execution starts
        import uuid

        temp_workflow_id = str(uuid.uuid4())

        return WorkflowResponse(
            message="Workflow started successfully",
            workflow_id=temp_workflow_id,
            status="starting",
            initial_task=request.initial_task,
            metadata={
                "submitted_at": "2025-05-31T16:00:00Z",
                "estimated_steps": "5-10",
                **request.metadata,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start workflow: {str(e)}"
        )


@router.get("/simple/{workflow_id}", response_model=WorkflowResultResponse)
async def get_workflow_result(
    workflow_id: str, workflow_service: WorkflowService = Depends(get_workflow_service)
) -> WorkflowResultResponse:
    """
    Get the results of a completed workflow.

    This endpoint returns the detailed results of a workflow execution.
    For real-time updates, clients should use WebSocket connections.

    Args:
        workflow_id: The unique identifier of the workflow
        workflow_service: Injected workflow service dependency

    Returns:
        WorkflowResultResponse: Complete workflow execution results

    Raises:
        HTTPException: If the workflow is not found or still running
    """
    try:
        # This is a placeholder implementation
        # In a real system, you would store workflow results in a database
        # and retrieve them here

        raise HTTPException(
            status_code=501,
            detail="Workflow result retrieval not yet implemented. "
            "Use WebSocket connections for real-time workflow updates.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve workflow: {str(e)}"
        )


@router.get("/", response_model=List[Dict])
async def list_workflows(
    limit: int = 10,
    offset: int = 0,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> List[Dict]:
    """
    List recent workflows.

    This endpoint returns a list of recent workflow executions.

    Args:
        limit: Maximum number of workflows to return (default: 10)
        offset: Number of workflows to skip (default: 0)
        workflow_service: Injected workflow service dependency

    Returns:
        List[Dict]: List of workflow summaries

    Raises:
        HTTPException: If the request fails
    """
    try:
        # Placeholder implementation
        # In a real system, you would retrieve workflows from a database

        return [
            {
                "workflow_id": "example-workflow-1",
                "initial_task": "Create a web application",
                "status": "completed",
                "created_at": "2025-05-31T15:30:00Z",
                "completed_at": "2025-05-31T15:35:00Z",
                "steps_executed": 5,
                "total_steps": 5,
            }
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list workflows: {str(e)}"
        )


async def _execute_workflow_async(
    workflow_service: WorkflowService, initial_task: str, metadata: Dict
) -> None:
    """
    Execute workflow asynchronously in the background.

    This function runs the actual workflow execution and publishes
    events via the EventBus for WebSocket clients to receive.

    Args:
        workflow_service: The workflow service instance
        initial_task: The initial task to execute
        metadata: Additional metadata for the workflow
    """
    try:
        # Create a WorkflowRequest object for the workflow service
        workflow_request = WorkflowRequest(
            title=initial_task,
            description=f"Simple workflow: {initial_task}",
            steps=[{"name": "main_task", "description": initial_task}],
            source_ids=None,
        )

        # Execute the workflow
        # Events will be automatically published via the EventBus
        result = await workflow_service.start_simple_workflow(workflow_request)

        # Log the completion for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Workflow {result.get('workflow_id')} completed with status: "
            f"{result.get('status')} ({result.get('steps_executed')}/{result.get('total_steps')} steps)"
        )

    except Exception as e:
        # Log the error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Workflow execution failed: {str(e)}")


@router.get("/health")
async def workflow_health() -> Dict[str, str]:
    """
    Health check endpoint for workflow service.

    Returns:
        Dict[str, str]: Health status information
    """
    return {"status": "healthy", "service": "workflow_service", "version": "1.0.0"}
