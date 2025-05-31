from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    # ...existing settings...

    # Vector Database Configuration (ChromaDB)
    vector_db_host: str = Field(default="localhost", env="VECTOR_DB_HOST")
    vector_db_port: int = Field(default=8000, env="VECTOR_DB_PORT")
    vector_db_url: str = Field(default="http://localhost:8000", env="VECTOR_DB_URL")

    # ChromaDB specific settings
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    chroma_auth_token: Optional[str] = Field(default=None, env="CHROMA_AUTH_TOKEN")
    chroma_auth_provider: Optional[str] = Field(
        default=None, env="CHROMA_AUTH_PROVIDER"
    )
    chroma_auth_credentials: Optional[str] = Field(
        default=None, env="CHROMA_AUTH_CREDENTIALS"
    )
    chroma_auth_header: str = Field(default="X-Chroma-Token", env="CHROMA_AUTH_HEADER")

    # Vector Database Collections
    vector_collection_name: str = Field(
        default="openmanus_documents", env="VECTOR_COLLECTION_NAME"
    )
    vector_workflow_collection: str = Field(
        default="openmanus_workflows", env="VECTOR_WORKFLOW_COLLECTION"
    )

    # Embedding Configuration
    vector_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", env="VECTOR_EMBEDDING_MODEL"
    )
    vector_embedding_dimension: int = Field(
        default=384, env="VECTOR_EMBEDDING_DIMENSION"
    )

    # Document Processing Settings
    vector_chunk_size: int = Field(default=1000, env="VECTOR_CHUNK_SIZE")
    vector_chunk_overlap: int = Field(default=200, env="VECTOR_CHUNK_OVERLAP")
    vector_search_k: int = Field(default=5, env="VECTOR_SEARCH_K")
    vector_search_threshold: float = Field(default=0.7, env="VECTOR_SEARCH_THRESHOLD")

    # Document Upload Configuration
    document_upload_max_size: str = Field(
        default="50MB", env="DOCUMENT_UPLOAD_MAX_SIZE"
    )
    document_allowed_types: str = Field(
        default="pdf,txt,md,docx", env="DOCUMENT_ALLOWED_TYPES"
    )
    document_storage_path: str = Field(
        default="./data/documents", env="DOCUMENT_STORAGE_PATH"
    )
    document_processing_timeout: int = Field(
        default=300, env="DOCUMENT_PROCESSING_TIMEOUT"
    )

    # RAG Configuration
    rag_max_context_length: int = Field(default=4000, env="RAG_MAX_CONTEXT_LENGTH")
    rag_overlap_ratio: float = Field(default=0.1, env="RAG_OVERLAP_RATIO")
    rag_min_score: float = Field(default=0.3, env="RAG_MIN_SCORE")
    rag_max_documents: int = Field(default=10, env="RAG_MAX_DOCUMENTS")

    # Embedding Service Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ollama_base_url: str = Field(
        default="http://localhost:11434", env="OLLAMA_BASE_URL"
    )

    @property
    def chroma_client_settings(self) -> dict:
        """Get ChromaDB client settings as a dictionary."""
        settings = {
            "host": self.chroma_host,
            "port": self.chroma_port,
        }

        if self.chroma_auth_token:
            settings["headers"] = {self.chroma_auth_header: self.chroma_auth_token}

        return settings

    @property
    def document_allowed_types_list(self) -> List[str]:
        """Get allowed document types as a list."""
        return [t.strip().lower() for t in self.document_allowed_types.split(",")]

    @property
    def document_max_size_bytes(self) -> int:
        """Convert document max size to bytes."""
        size_str = self.document_upload_max_size.upper()
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)

    @validator("vector_db_url")
    def validate_vector_db_url(cls, v, values):
        """Construct vector DB URL from host and port if not provided."""
        if (
            v == "http://localhost:8000"
            and "vector_db_host" in values
            and "vector_db_port" in values
        ):
            return f"http://{values['vector_db_host']}:{values['vector_db_port']}"
        return v

    @validator("vector_search_threshold")
    def validate_search_threshold(cls, v):
        """Ensure search threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("vector_search_threshold must be between 0.0 and 1.0")
        return v

    @validator("rag_overlap_ratio")
    def validate_overlap_ratio(cls, v):
        """Ensure overlap ratio is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("rag_overlap_ratio must be between 0.0 and 1.0")
        return v

    # ...existing code...
