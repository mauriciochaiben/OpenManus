"""Embedding metadata models for knowledge management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EmbeddingMetadataCreate(BaseModel):
    """
    Pydantic model for creating embedding metadata.
    """

    source_document_id: str = Field(..., description="ID of the source document")
    chunk_id: str | None = Field(
        default=None, description="ID of the document chunk this embedding represents"
    )
    vector_id: str = Field(
        ..., description="ID of the embedding vector in the vector database"
    )
    model_name: str = Field(..., description="Name of the embedding model used")
    dimensions: int = Field(
        ..., gt=0, description="Number of dimensions in the embedding vector"
    )


class EmbeddingMetadata(EmbeddingMetadataCreate):
    """
    Pydantic model for embedding metadata.

    Tracks information about embeddings stored in the vector database.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the embedding metadata",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )

    class Config:
        """Configuration for the model."""

        arbitrary_types_allowed = True
