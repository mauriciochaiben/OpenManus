import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies.core import get_workflow_service
from app.api.routers.workflows import WorkflowStepResponse
from app.knowledge.infrastructure.vector_store_client import VectorStoreClient
from app.knowledge.services.embedding_service import EmbeddingService
from app.knowledge.services.rag_service import RagService
from app.services.role_manager import RoleManager, create_yaml_role_manager
from app.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency injection functions
def get_rag_service() -> RagService:
    """Get RAG service instance with dependencies."""
    embedding_service = EmbeddingService()  # Configure as needed
    vector_store_client = VectorStoreClient()  # Configure as needed
    return RagService(embedding_service, vector_store_client)


def get_role_manager() -> RoleManager:
    """Get role manager instance."""
    return create_yaml_role_manager(
        config_dir="app/config/roles",
        event_bus=None,  # Will be injected by workflow service
    )


# Workflow request and response models
class WorkflowRequest(BaseModel):
    title: str
    description: str
    steps: list[dict]
    source_ids: list[str] | None = Field(
        default=None, description="Knowledge source IDs for context"
    )


class WorkflowResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    steps: list[dict]
    created_at: str
    updated_at: str
    context_enhanced: bool


# Workflow creation endpoint
@router.post("/complex", response_model=WorkflowResponse)
async def create_complex_workflow(
    request: WorkflowRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),
    rag_service: RagService = Depends(get_rag_service),
    role_manager: RoleManager = Depends(get_role_manager),
):
    """Create and execute a complex workflow with dynamic agent selection."""
    try:
        # Configure services
        workflow_service.set_rag_service(rag_service)
        workflow_service.set_role_manager(role_manager)

        # Create workflow request object
        workflow_request = WorkflowRequest(
            title=request.title,
            description=request.description,
            steps=request.steps,
            source_ids=request.source_ids,
        )

        # Start complex workflow
        workflow = await workflow_service.start_complex_workflow(workflow_request)

        return WorkflowResponse(
            id=workflow.id,
            title=workflow.title,
            description=workflow.description,
            status=workflow.status,
            steps=[
                WorkflowStepResponse(
                    id=step.id,
                    name=step.name,
                    status=step.status,
                    result=step.result,
                    error=step.error,
                )
                for step in workflow.steps
            ],
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            context_enhanced=bool(request.source_ids),
            execution_type="complex",
        )

    except Exception as e:
        logger.error(f"Error creating complex workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/simple", response_model=WorkflowResponse)
async def create_simple_workflow(
    request: WorkflowRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),
    rag_service: RagService = Depends(get_rag_service),
    role_manager: RoleManager = Depends(get_role_manager),
):
    """Create and execute a simple workflow (enhanced with role manager)."""
    try:
        # Configure services
        workflow_service.set_rag_service(rag_service)
        workflow_service.set_role_manager(role_manager)

        # Create workflow request object
        workflow_request = WorkflowRequest(
            title=request.title,
            description=request.description,
            steps=request.steps,
            source_ids=request.source_ids,
        )

        # Start workflow (now uses enhanced system internally)
        workflow = await workflow_service.start_simple_workflow(workflow_request)

        return WorkflowResponse(
            id=workflow.id,
            title=workflow.title,
            description=workflow.description,
            status=workflow.status,
            steps=[
                WorkflowStepResponse(
                    id=step.id,
                    name=step.name,
                    status=step.status,
                    result=step.result,
                    error=step.error,
                )
                for step in workflow.steps
            ],
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            context_enhanced=bool(request.source_ids),
            execution_type="simple",
        )

    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# @router.post("/podcast", response_model=WorkflowResponse)
# async def create_podcast_workflow(
#     source_ids: Optional[List[str]] = Body(None),
#     note_ids: Optional[List[str]] = Body(None),
#     topic: Optional[str] = Body(None),
#     style: str = Body("conversational"),
#     duration_target: int = Body(300),
#     include_intro: bool = Body(True),
#     include_outro: bool = Body(True),
#     workflow_service: WorkflowService = Depends(get_workflow_service),
#     rag_service: RagService = Depends(get_rag_service),
#     # source_service: SourceService = Depends(get_source_service),
#     # note_service: NoteService = Depends(get_note_service),
# ):
#     """Create a podcast from knowledge sources and notes."""
#     # Commented out temporarily until dependencies are available
#     pass
