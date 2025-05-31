"""Vector Database Configuration Module."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.core.config import settings


class VectorDBConfig(BaseModel):
    """Vector Database Configuration."""

    host: str = Field(default_factory=lambda: settings.vector_db_host)
    port: int = Field(default_factory=lambda: settings.vector_db_port)
    url: str = Field(default_factory=lambda: settings.vector_db_url)

    # Collection settings
    documents_collection: str = Field(
        default_factory=lambda: settings.vector_collection_name
    )
    workflows_collection: str = Field(
        default_factory=lambda: settings.vector_workflow_collection
    )

    # Authentication
    auth_token: Optional[str] = Field(
        default_factory=lambda: settings.chroma_auth_token
    )
    auth_header: str = Field(default_factory=lambda: settings.chroma_auth_header)

    # Performance settings
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)

    def get_client_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for ChromaDB client initialization."""
        kwargs = {
            "host": self.host,
            "port": self.port,
        }

        if self.auth_token:
            kwargs["headers"] = {self.auth_header: self.auth_token}

        return kwargs

    def get_collection_metadata(self, collection_type: str) -> Dict[str, Any]:
        """Get metadata for collection creation."""
        base_metadata = {
            "created_by": "openmanus",
            "version": "1.0",
            "description": f"OpenManus {collection_type} collection",
        }

        if collection_type == "documents":
            base_metadata.update(
                {
                    "type": "documents",
                    "embedding_model": settings.vector_embedding_model,
                    "chunk_size": settings.vector_chunk_size,
                    "chunk_overlap": settings.vector_chunk_overlap,
                }
            )
        elif collection_type == "workflows":
            base_metadata.update(
                {
                    "type": "workflows",
                    "embedding_model": settings.vector_embedding_model,
                }
            )

        return base_metadata


class EmbeddingConfig(BaseModel):
    """Embedding Configuration."""

    model_name: str = Field(default_factory=lambda: settings.vector_embedding_model)
    dimension: int = Field(default_factory=lambda: settings.vector_embedding_dimension)
    normalize: bool = Field(default=True)
    batch_size: int = Field(default=32)

    # Text processing
    max_length: int = Field(default=512)
    truncate: bool = Field(default=True)

    @validator("dimension")
    def validate_dimension(cls, v):
        """Ensure dimension is positive."""
        if v <= 0:
            raise ValueError("Embedding dimension must be positive")
        return v


class DocumentProcessingConfig(BaseModel):
    """Document Processing Configuration."""

    chunk_size: int = Field(default_factory=lambda: settings.vector_chunk_size)
    chunk_overlap: int = Field(default_factory=lambda: settings.vector_chunk_overlap)

    # File handling
    max_file_size: int = Field(default_factory=lambda: settings.document_max_size_bytes)
    allowed_types: List[str] = Field(
        default_factory=lambda: settings.document_allowed_types_list
    )
    storage_path: str = Field(default_factory=lambda: settings.document_storage_path)

    # Processing limits
    timeout: int = Field(default_factory=lambda: settings.document_processing_timeout)
    max_pages: Optional[int] = Field(default=None)

    @validator("chunk_overlap")
    def validate_chunk_overlap(cls, v, values):
        """Ensure chunk overlap is less than chunk size."""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class RAGConfig(BaseModel):
    """RAG (Retrieval-Augmented Generation) Configuration."""

    search_k: int = Field(default_factory=lambda: settings.vector_search_k)
    search_threshold: float = Field(
        default_factory=lambda: settings.vector_search_threshold
    )

    # Context management
    max_context_length: int = Field(
        default_factory=lambda: settings.rag_max_context_length
    )
    overlap_ratio: float = Field(default_factory=lambda: settings.rag_overlap_ratio)
    min_score: float = Field(default_factory=lambda: settings.rag_min_score)
    max_documents: int = Field(default_factory=lambda: settings.rag_max_documents)

    # Reranking
    enable_reranking: bool = Field(default=False)
    rerank_top_k: int = Field(default=20)

    @validator("search_threshold", "min_score", "overlap_ratio")
    def validate_ratio(cls, v):
        """Ensure ratio values are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Ratio values must be between 0.0 and 1.0")
        return v


# Configuration instances
vector_db_config = VectorDBConfig()
embedding_config = EmbeddingConfig()
document_processing_config = DocumentProcessingConfig()
rag_config = RAGConfig()
