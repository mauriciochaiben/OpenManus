from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # ...existing code...

    # TTS Configuration
    elevenlabs_api_key: Optional[str] = None
    podcast_host_1_voice_id: str = "default"
    podcast_host_2_voice_id: str = "default"
    podcast_output_dir: str = "output/podcasts"

    # Code Execution Settings
    code_execution_enabled: bool = True
    code_execution_timeout: int = 30
    code_execution_memory_limit: int = 100  # MB
    code_execution_max_output: int = 10000  # characters
    code_execution_allowed_languages: List[str] = ["python", "javascript"]
    code_execution_restricted_python: bool = True

    # Tool Execution & Sandboxing Settings
    tool_execution_timeout: int = 30
    tool_sandbox_enabled: bool = True
    tool_sandbox_memory_limit: str = "128m"
    tool_sandbox_cpu_limit: float = 0.5
    tool_sandbox_network_disabled: bool = True
    tool_force_sandbox_unsafe: bool = True

    # Vector Database Configuration
    vector_db_host: str = "localhost"
    vector_db_port: int = 8000
    vector_db_url: str = "http://localhost:8000"
    vector_collection_name: str = "documents"
    vector_workflow_collection: str = "workflows"
    chroma_auth_token: Optional[str] = None
    chroma_auth_header: str = "Authorization"
    
    # Embedding Configuration
    vector_embedding_model: str = "all-MiniLM-L6-v2"
    vector_embedding_dimension: int = 384
    
    # Document Processing Configuration
    vector_chunk_size: int = 500
    vector_chunk_overlap: int = 50
    document_max_size_bytes: int = 50 * 1024 * 1024  # 50MB
    document_allowed_types_list: List[str] = [".pdf", ".txt", ".md", ".doc", ".docx"]
    document_storage_path: str = "uploads/"
    document_processing_timeout: int = 300
    
    # RAG Configuration
    vector_search_k: int = 5
    vector_search_threshold: float = 0.7
    rag_max_context_length: int = 4000
    rag_overlap_ratio: float = 0.1
    rag_min_score: float = 0.5
    rag_max_documents: int = 10
    
    
settings = Settings()
