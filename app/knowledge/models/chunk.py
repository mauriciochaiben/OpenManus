"""Document chunk models for knowledge management."""

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, Field


class DocumentChunkCreate(BaseModel):
    """
    Pydantic model for creating document chunks.
    """

    source_document_id: str = Field(..., description="ID of the source document this chunk belongs to")
    content: str = Field(..., min_length=1, description="Text content of the chunk")
    chunk_index: int = Field(
        ...,
        ge=0,
        description="Index/position of the chunk within the document",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the chunk (e.g., page number, section)",
    )


class DocumentChunk(DocumentChunkCreate):
    """
    Pydantic model for document chunks.

    Represents text chunks extracted from source documents
    for embedding and vector search.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the chunk",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Chunk creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")
    vector_id: str | None = Field(default=None, description="ID of the chunk in the vector database")
    embedding_id: str | None = Field(default=None, description="ID of the embedding metadata for this chunk")

    class Config:
        """Configuration for the model."""

        arbitrary_types_allowed = True
