"""Embedding metadata models for knowledge management."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class EmbeddingMetadata(BaseModel):
    """
    Pydantic model for embedding metadata.

    Tracks information about embeddings stored in the vector database.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the embedding metadata",
    )

    source_document_id: str = Field(..., description="ID of the source document")

    chunk_id: Optional[str] = Field(
        default=None, description="ID of the document chunk this embedding represents"
    )

    vector_id: str = Field(
        ..., description="ID of the embedding vector in the vector database"
    )

    collection_name: str = Field(
        ..., description="Name of the vector database collection"
    )

    embedding_model: str = Field(..., description="Name of the embedding model used")

    embedding_dimension: int = Field(
        ..., gt=0, description="Dimension of the embedding vector"
    )

    content_preview: Optional[str] = Field(
        default=None, max_length=500, description="Preview of the embedded content"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the embedding"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the embedding was created",
    )

    class Config:
        """Pydantic model configuration."""

        schema_extra = {
            "example": {
                "id": "embedding-123",
                "source_document_id": "doc-456",
                "chunk_id": "chunk-789",
                "vector_id": "vector-abc",
                "collection_name": "openmanus_documents",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "content_preview": "This is a preview of the embedded content...",
                "metadata": {"chunk_index": 0, "similarity_threshold": 0.7},
            }
        }


class EmbeddingMetadataCreate(BaseModel):
    """Model for creating embedding metadata."""

    source_document_id: str
    chunk_id: Optional[str] = None
    vector_id: str
    collection_name: str
    embedding_model: str
    embedding_dimension: int = Field(..., gt=0)
    content_preview: Optional[str] = Field(default=None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingMetadataResponse(EmbeddingMetadata):
    """Response model for embedding metadata."""

    pass
