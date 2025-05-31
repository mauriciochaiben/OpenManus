"""Document chunk models for knowledge management."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentChunk(BaseModel):
    """
    Pydantic model for document chunks.

    Represents text chunks extracted from source documents
    for embedding and vector search.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the chunk",
    )

    source_document_id: str = Field(
        ..., description="ID of the source document this chunk belongs to"
    )

    content: str = Field(..., min_length=1, description="Text content of the chunk")

    chunk_index: int = Field(
        ...,
        ge=0,
        description="Sequential index of this chunk within the source document",
    )

    start_position: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character position where this chunk starts in the original document",
    )

    end_position: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character position where this chunk ends in the original document",
    )

    content_length: int = Field(
        ..., ge=0, description="Length of the chunk content in characters"
    )

    embedding_id: Optional[str] = Field(
        default=None, description="ID of the embedding vector in the vector database"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the chunk"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the chunk was created",
    )

    @field_validator("content_length", mode="before")
    @classmethod
    def validate_content_length(cls, v, info):
        """Ensure content_length matches actual content length."""
        if info.data and "content" in info.data:
            content = info.data["content"]
            if content and v != len(content):
                return len(content)
        return v

    @field_validator("end_position")
    @classmethod
    def validate_positions(cls, v, info):
        """Ensure end_position is greater than start_position."""
        if info.data and "start_position" in info.data:
            start_pos = info.data["start_position"]
            if start_pos is not None and v is not None and v <= start_pos:
                raise ValueError("end_position must be greater than start_position")
        return v


class DocumentChunkCreate(BaseModel):
    """Model for creating new document chunks."""

    source_document_id: str
    content: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)
    start_position: Optional[int] = Field(default=None, ge=0)
    end_position: Optional[int] = Field(default=None, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunkResponse(DocumentChunk):
    """Response model for document chunks."""

    pass
