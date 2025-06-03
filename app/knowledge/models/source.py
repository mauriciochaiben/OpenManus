"""Source document models for knowledge management."""

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, validator


class DocumentStatus(str, Enum):
    """Document processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "md"
    DOCX = "docx"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    AUDIO = "audio"


class SourceDocumentCreate(BaseModel):
    """
    Pydantic model for creating a source document.
    """

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename of the document",
    )
    content_hash: str = Field(
        ...,
        min_length=1,
        description="SHA-256 hash of the document content for deduplication",
    )
    file_type: DocumentType = Field(..., description="Type of the document (pdf, txt, etc.)")
    mime_type: str = Field(..., description="MIME type of the document")
    file_size: int = Field(..., ge=0, description="Size of the document in bytes")
    owner_id: str | None = Field(default=None, description="ID of the user who uploaded the document")
    category: str | None = Field(default=None, description="Category or topic of the document")
    tags: list[str] | None = Field(default_factory=list, description="Tags associated with the document")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Additional metadata for the document")


class SourceDocument(SourceDocumentCreate):
    """
    Pydantic model for source documents in the knowledge base.

    This model represents documents that have been uploaded and processed
    for embedding in the vector database.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the document",
    )
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="Processing status of the document")
    file_path: Path | None = Field(default=None, description="Path to the document file on disk")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Document creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")
    processed_at: datetime | None = Field(default=None, description="Processing completion timestamp")
    chunk_count: int = Field(default=0, description="Number of chunks created from the document")
    embedding_count: int = Field(default=0, description="Number of embeddings created for the document")
    error_message: str | None = Field(default=None, description="Error message if processing failed")

    @validator("tags", pre=True)
    def format_tags(cls, v):
        """Format tags as list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v


class SourceDocumentSummary(BaseModel):
    """
    Summarized version of source document for list views.
    """

    id: str
    filename: str
    file_type: str
    status: DocumentStatus
    category: str | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime | None = None
    chunk_count: int
    file_size: int


class SourceDocumentResponse(SourceDocument):
    """
    Full source document response with all metadata.
    """

    pass


class SourceStatusResponse(BaseModel):
    """Response model for source status."""

    source_id: str
    filename: str
    status: DocumentStatus
    processing_progress: dict[str, Any] | None = None
    created_at: str
    updated_at: str | None = None
    processed_at: str | None = None
    chunk_count: int = 0
    embedding_count: int = 0
    error_message: str | None = None


class SourceListResponse(BaseModel):
    """Response model for source list."""

    sources: list[SourceDocumentSummary]
    total: int
    page: int
    page_size: int


class SearchRequest(BaseModel):
    """Request model for document search."""

    query: str = Field(..., min_length=1, description="Search query text")
    source_ids: list[str] | None = Field(default=None, description="Filter by specific source IDs")
    k: int = Field(default=5, ge=1, le=100, description="Number of results to return")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class SearchResultItem(BaseModel):
    """Search result item model."""

    text: str
    score: float
    metadata: dict[str, Any]


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: list[SearchResultItem]
    query: str
    total_results: int
