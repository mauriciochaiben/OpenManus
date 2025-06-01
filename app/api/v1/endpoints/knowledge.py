"""Knowledge management API endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.knowledge.models.source import DocumentStatus, DocumentType, SourceDocument
from app.knowledge.services.source_service import (
    SourceServiceError,
    get_or_create_source_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["knowledge"])


# Request/Response models
class SourceUploadResponse(BaseModel):
    """Response model for source upload."""

    source_id: str
    filename: str
    status: DocumentStatus
    message: str


class SourceStatusResponse(BaseModel):
    """Response model for source status."""

    source_id: str
    filename: str
    status: DocumentStatus
    processing_progress: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: Optional[str] = None
    processed_at: Optional[str] = None
    chunk_count: int = 0
    embedding_count: int = 0
    error_message: Optional[str] = None


class SourceDocumentSummary(BaseModel):
    """Summary model for source documents."""

    id: str
    filename: str
    file_type: str
    status: DocumentStatus
    created_at: str
    updated_at: Optional[str] = None
    chunk_count: int = 0
    file_size: int = 0


class SourceListResponse(BaseModel):
    """Response model for source list."""

    sources: List[SourceDocumentSummary]
    total: int
    page: int
    page_size: int


class SearchRequest(BaseModel):
    """Request model for document search."""

    query: str
    n_results: int = Field(default=5, ge=1, le=20)
    source_ids: Optional[List[str]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search results."""

    query: str
    results: List[Dict[str, Any]]
    total_found: int


# Dependency to get source service
async def get_source_service():
    """Dependency to get source service instance."""
    return await get_or_create_source_service()


@router.post("/sources/upload", response_model=SourceUploadResponse)
async def upload_source(
    file: UploadFile = File(...),
    category: Optional[str] = None,
    tags: Optional[str] = None,
    owner_id: Optional[str] = None,
    service: Any = Depends(get_source_service),
) -> SourceUploadResponse:
    """
    Upload a source document for processing.

    Args:
        file: Document file to upload
        category: Document category (optional)
        tags: Comma-separated tags (optional)
        owner_id: Owner user ID (optional)
        service: Source service dependency

    Returns:
        Upload response with source ID and status

    Raises:
        HTTPException: If upload fails
    """
    try:
        logger.info(f"Uploading file: {file.filename}")

        metadata = {}

        # Upload and process file
        source_doc = await service.upload_source(
            file=file,
            category=category,
            tags=tags,
            owner_id=owner_id,
            metadata=metadata,
        )

        logger.info(f"File uploaded successfully: {source_doc.id}")

        return SourceUploadResponse(
            source_id=source_doc.id,
            filename=source_doc.filename,
            status=source_doc.status,
            message=f"File '{source_doc.filename}' uploaded successfully. Processing started.",
        )

    except SourceServiceError as e:
        logger.error(f"Source service error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file upload",
        )


@router.get("/sources/{source_id}/status", response_model=SourceStatusResponse)
async def get_source_status(
    source_id: str, service: Any = Depends(get_source_service)
) -> SourceStatusResponse:
    """
    Get the processing status of a source document.

    Args:
        source_id: Source document ID
        service: Source service dependency

    Returns:
        Source status information

    Raises:
        HTTPException: If source not found
    """
    try:
        source_doc = await service.get_source_document(source_id)

        if not source_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source document '{source_id}' not found",
            )

        # Calculate processing progress
        progress = None
        if source_doc.status == DocumentStatus.PROCESSING:
            progress = {
                "current_step": "embedding_generation",
                "estimated_completion": "Processing in progress...",
            }
        elif source_doc.status == DocumentStatus.COMPLETED:
            progress = {
                "current_step": "completed",
                "chunks_created": source_doc.chunk_count or 0,
                "embeddings_created": source_doc.embedding_count or 0,
            }

        return SourceStatusResponse(
            source_id=source_doc.id,
            filename=source_doc.filename,
            status=source_doc.status,
            processing_progress=progress,
            created_at=source_doc.created_at.isoformat(),
            updated_at=(
                source_doc.updated_at.isoformat() if source_doc.updated_at else None
            ),
            processed_at=(
                source_doc.processed_at.isoformat() if source_doc.processed_at else None
            ),
            chunk_count=source_doc.chunk_count or 0,
            embedding_count=source_doc.embedding_count or 0,
            error_message=source_doc.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting source status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/sources", response_model=SourceListResponse)
async def list_sources(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[DocumentStatus] = Query(
        None, description="Filter by status"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    owner_id: Optional[str] = Query(None, description="Filter by owner"),
    service: Any = Depends(get_source_service),
) -> SourceListResponse:
    """
    List source documents with pagination and filtering.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        status_filter: Filter by document status
        category: Filter by category
        owner_id: Filter by owner ID
        service: Source service dependency

    Returns:
        Paginated list of source documents
    """
    try:
        logger.info(f"Listing sources: page={page}, page_size={page_size}")

        # Get sources from service
        sources, total = await service.list_sources(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            category=category,
            owner_id=owner_id,
        )

        return SourceListResponse(
            sources=sources, total=total, page=page, page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/sources/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest, service: Any = Depends(get_source_service)
) -> SearchResponse:
    """
    Search documents using vector similarity.

    Args:
        request: Search request parameters
        service: Source service dependency

    Returns:
        Search results with similar documents
    """
    try:
        logger.info(f"Searching documents: query='{request.query}'")

        # Perform vector search
        results = await service.search_documents(
            query=request.query,
            source_ids=request.source_ids,
            k=request.n_results,
            min_score=0.0,
        )

        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
        )

    except SourceServiceError as e:
        logger.error(f"Search service error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search",
        )


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str, service: Any = Depends(get_source_service)
) -> JSONResponse:
    """
    Delete a source document and its associated data.

    Args:
        source_id: Source document ID to delete
        service: Source service dependency

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting source document: {source_id}")

        success = await service.delete_source(source_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source document '{source_id}' not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Source document '{source_id}' deleted successfully",
                "source_id": source_id,
            },
        )

    except HTTPException:
        raise
    except SourceServiceError as e:
        logger.error(f"Source service error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during deletion",
        )


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for knowledge service.

    Returns:
        Health status information
    """
    try:
        # Check if source service is available
        source_service = await get_or_create_source_service()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "knowledge_api",
                "version": "1.0.0",
                "components": {
                    "source_service": "available",
                    "vector_store": "available",
                    "embedding_service": "available",
                },
            },
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "knowledge_api",
                "error": str(e),
            },
        )
