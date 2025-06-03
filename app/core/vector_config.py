"""
DEPRECATED: Vector Database Configuration Module.

This module is deprecated and will be removed in a future version.
Please use the new centralized configuration system:

    from app.core.settings import settings

    # Access vector database configuration
    vector_config = settings.knowledge_config.vector_db
    embedding_config = settings.knowledge_config.embedding
    document_config = settings.knowledge_config.document_processing
    rag_config = settings.knowledge_config.rag

For backward compatibility, the old configuration objects are still available
but will issue deprecation warnings.
"""

import warnings
from typing import Any

from pydantic import BaseModel, Field, validator

from app.core.settings import settings

# Issue deprecation warning when this module is imported
warnings.warn(
    "app.core.vector_config is deprecated. Use 'from app.core.settings import "
    "settings; settings.knowledge_config' instead.",
    DeprecationWarning,
    stacklevel=2,
)


class VectorDBConfig(BaseModel):
    """Vector Database Configuration.

    DEPRECATED: Use settings.knowledge_config.vector_db instead.
    """

    host: str = Field(default_factory=lambda: settings.knowledge_config.vector_db.host)
    port: int = Field(default_factory=lambda: settings.knowledge_config.vector_db.port)
    url: str = Field(default_factory=lambda: settings.knowledge_config.vector_db.url)

    # Collection settings
    documents_collection: str = Field(default_factory=lambda: settings.knowledge_config.vector_db.documents_collection)
    workflows_collection: str = Field(default_factory=lambda: settings.knowledge_config.vector_db.workflows_collection)

    # Authentication
    auth_token: str | None = Field(default_factory=lambda: settings.knowledge_config.vector_db.auth_token)
    auth_header: str = Field(default_factory=lambda: settings.knowledge_config.vector_db.auth_header)

    # Performance settings
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)

    def get_client_kwargs(self) -> dict[str, Any]:
        """Get kwargs for ChromaDB client initialization."""
        kwargs = {
            "host": self.host,
            "port": self.port,
        }

        if self.auth_token:
            kwargs["headers"] = {self.auth_header: self.auth_token}

        return kwargs

    def get_collection_metadata(self, collection_type: str) -> dict[str, Any]:
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
                    "embedding_model": settings.knowledge_config.embedding.model_name,
                    "chunk_size": settings.knowledge_config.document_processing.chunk_size,
                    "chunk_overlap": settings.knowledge_config.document_processing.chunk_overlap,
                }
            )
        elif collection_type == "workflows":
            base_metadata.update(
                {
                    "type": "workflows",
                    "embedding_model": settings.knowledge_config.embedding.model_name,
                }
            )

        return base_metadata


class EmbeddingConfig(BaseModel):
    """Embedding Configuration.

    DEPRECATED: Use settings.knowledge_config.embedding instead.
    """

    model_name: str = Field(default_factory=lambda: settings.knowledge_config.embedding.model_name)
    dimension: int = Field(default_factory=lambda: settings.knowledge_config.embedding.dimension)
    normalize: bool = Field(default_factory=lambda: settings.knowledge_config.embedding.normalize)
    batch_size: int = Field(default_factory=lambda: settings.knowledge_config.embedding.batch_size)

    # Text processing
    max_length: int = Field(default_factory=lambda: settings.knowledge_config.embedding.max_length)
    truncate: bool = Field(default_factory=lambda: settings.knowledge_config.embedding.truncate)

    @validator("dimension")
    def validate_dimension(cls, v):
        """Ensure dimension is positive."""
        if v <= 0:
            raise ValueError("Embedding dimension must be positive")
        return v


class DocumentProcessingConfig(BaseModel):
    """Document Processing Configuration.

    DEPRECATED: Use settings.knowledge_config.document_processing instead.
    """

    chunk_size: int = Field(default_factory=lambda: settings.knowledge_config.document_processing.chunk_size)
    chunk_overlap: int = Field(default_factory=lambda: settings.knowledge_config.document_processing.chunk_overlap)

    # File handling
    max_file_size: int = Field(default_factory=lambda: settings.knowledge_config.document_processing.max_size_bytes)
    allowed_types: list[str] = Field(
        default_factory=lambda: settings.knowledge_config.document_processing.allowed_types_list
    )
    storage_path: str = Field(default_factory=lambda: settings.knowledge_config.document_processing.storage_path)

    # Processing limits
    timeout: int = Field(default_factory=lambda: settings.knowledge_config.document_processing.processing_timeout)
    max_pages: int | None = Field(default=None)

    @validator("chunk_overlap")
    def validate_chunk_overlap(cls, v, values):
        """Ensure chunk overlap is less than chunk size."""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class RAGConfig(BaseModel):
    """RAG (Retrieval-Augmented Generation) Configuration.

    DEPRECATED: Use settings.knowledge_config.rag instead.
    """

    search_k: int = Field(default_factory=lambda: settings.knowledge_config.document_processing.search_k)
    search_threshold: float = Field(
        default_factory=lambda: settings.knowledge_config.document_processing.search_threshold
    )

    # Context management
    max_context_length: int = Field(default_factory=lambda: settings.knowledge_config.rag.max_context_length)
    overlap_ratio: float = Field(default_factory=lambda: settings.knowledge_config.rag.overlap_ratio)
    min_score: float = Field(default_factory=lambda: settings.knowledge_config.rag.min_score)
    max_documents: int = Field(default_factory=lambda: settings.knowledge_config.rag.max_documents)

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
# DEPRECATED: Use settings.knowledge_config instead
def _warn_config_usage(config_name: str):
    """Issue deprecation warning for configuration usage."""
    warnings.warn(
        f"Using {config_name} is deprecated. Use 'from app.core.settings import "
        f"settings; settings.knowledge_config' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


# Backward compatibility configuration instances
class _DeprecatedVectorDBConfig:
    def __getattr__(self, name):
        _warn_config_usage("vector_db_config")
        return getattr(settings.knowledge_config.vector_db, name)


class _DeprecatedEmbeddingConfig:
    def __getattr__(self, name):
        _warn_config_usage("embedding_config")
        return getattr(settings.knowledge_config.embedding, name)


class _DeprecatedDocumentProcessingConfig:
    def __getattr__(self, name):
        _warn_config_usage("document_processing_config")
        return getattr(settings.knowledge_config.document_processing, name)


class _DeprecatedRAGConfig:
    def __getattr__(self, name):
        _warn_config_usage("rag_config")
        return getattr(settings.knowledge_config.rag, name)


vector_db_config = _DeprecatedVectorDBConfig()
embedding_config = _DeprecatedEmbeddingConfig()
document_processing_config = _DeprecatedDocumentProcessingConfig()
rag_config = _DeprecatedRAGConfig()
rag_config = RAGConfig()
