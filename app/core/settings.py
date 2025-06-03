"""
Centralized Configuration Management for OpenManus

This module provides a unified configuration system using Pydantic BaseSettings
with support for TOML files and environment variables. It replaces the dispersed
configuration loading across the application.
"""

import json
import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def get_environment() -> str:
    """Get the current environment (development, production, etc.)."""
    return os.getenv("ENVIRONMENT", "development")


PROJECT_ROOT = get_project_root()
ENVIRONMENT = get_environment()


class ProxySettings(BaseModel):
    """Proxy configuration settings."""

    server: str | None = Field(None, description="Proxy server address")
    username: str | None = Field(None, description="Proxy username")
    password: str | None = Field(None, description="Proxy password")


class LLMSettings(BaseModel):
    """LLM configuration settings."""

    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    max_tokens: int = Field(4096, description="Maximum number of tokens per request")
    max_input_tokens: int | None = Field(
        None,
        description="Maximum input tokens to use across all requests (None for unlimited)",
    )
    temperature: float = Field(1.0, description="Sampling temperature")
    api_type: str = Field(..., description="Azure, Openai, or Ollama")
    api_version: str = Field("", description="Azure OpenAI version if AzureOpenAI")


class BrowserSettings(BaseModel):
    """Browser configuration settings."""

    headless: bool = Field(False, description="Whether to run browser in headless mode")
    disable_security: bool = Field(True, description="Disable browser security features")
    extra_chromium_args: list[str] = Field(default_factory=list, description="Extra arguments to pass to the browser")
    chrome_instance_path: str | None = Field(None, description="Path to a Chrome instance to use")
    wss_url: str | None = Field(None, description="Connect to a browser instance via WebSocket")
    cdp_url: str | None = Field(None, description="Connect to a browser instance via CDP")
    proxy: ProxySettings | None = Field(None, description="Proxy settings for the browser")
    max_content_length: int = Field(2000, description="Maximum length for content retrieval operations")


class SearchSettings(BaseModel):
    """Search configuration settings."""

    engine: str = Field(default="Google", description="Search engine to use")
    fallback_engines: list[str] = Field(
        default_factory=lambda: ["DuckDuckGo", "Baidu", "Bing"],
        description="Fallback search engines to try if the primary engine fails",
    )
    retry_delay: int = Field(
        default=60,
        description="Seconds to wait before retrying all engines again after they all fail",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of times to retry all engines when all fail",
    )
    lang: str = Field(
        default="en",
        description="Language code for search results (e.g., en, zh, fr)",
    )
    country: str = Field(
        default="us",
        description="Country code for search results (e.g., us, cn, uk)",
    )


class SandboxSettings(BaseModel):
    """Sandbox configuration settings."""

    use_sandbox: bool = Field(False, description="Whether to use the sandbox")
    image: str = Field("python:3.12-slim", description="Base image")
    work_dir: str = Field("/workspace", description="Container working directory")
    memory_limit: str = Field("512m", description="Memory limit")
    cpu_limit: float = Field(1.0, description="CPU limit")
    timeout: int = Field(300, description="Default command timeout (seconds)")
    network_enabled: bool = Field(False, description="Whether network access is allowed")


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    type: str = Field(..., description="Server connection type (sse or stdio)")
    url: str | None = Field(None, description="Server URL for SSE connections")
    command: str | None = Field(None, description="Command for stdio connections")
    args: list[str] = Field(default_factory=list, description="Arguments for stdio command")


class MCPSettings(BaseModel):
    """MCP (Model Context Protocol) configuration settings."""

    server_reference: str = Field("app.mcp.server", description="Module reference for the MCP server")
    servers: dict[str, MCPServerConfig] = Field(default_factory=dict, description="MCP server configurations")


class VectorDBSettings(BaseModel):
    """Vector Database configuration settings."""

    host: str = Field(default="localhost", description="ChromaDB host")
    port: int = Field(default=8000, description="ChromaDB port")
    url: str = Field(default="http://localhost:8000", description="ChromaDB URL")

    # Authentication
    auth_token: str | None = Field(default=None, description="ChromaDB auth token")
    auth_provider: str | None = Field(default=None, description="ChromaDB auth provider")
    auth_credentials: str | None = Field(default=None, description="ChromaDB auth credentials")
    auth_header: str = Field(default="X-Chroma-Token", description="ChromaDB auth header")

    # Collections
    documents_collection: str = Field(default="openmanus_documents", description="Documents collection name")
    workflows_collection: str = Field(default="openmanus_workflows", description="Workflows collection name")

    # Performance settings
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")


class EmbeddingSettings(BaseModel):
    """Embedding configuration settings."""

    # Model settings
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name",
    )
    dimension: int = Field(default=384, description="Embedding dimension")
    normalize: bool = Field(default=True, description="Normalize embeddings")
    batch_size: int = Field(default=32, description="Batch size for embedding generation")

    # Text processing
    max_length: int = Field(default=512, description="Maximum text length for embeddings")
    truncate: bool = Field(default=True, description="Truncate text if too long")

    # Provider settings
    openai_api_key: str | None = Field(default=None, description="OpenAI API key for embeddings")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")


class DocumentProcessingSettings(BaseModel):
    """Document processing configuration settings."""

    # Chunking settings
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")

    # Search settings
    search_k: int = Field(default=5, description="Number of documents to retrieve")
    search_threshold: float = Field(default=0.7, description="Similarity threshold for search")

    # Upload settings
    max_upload_size: str = Field(default="50MB", description="Maximum upload file size")
    allowed_types: str = Field(default="pdf,txt,md,docx", description="Allowed file types")
    storage_path: str = Field(default="./data/documents", description="Document storage path")
    processing_timeout: int = Field(default=300, description="Processing timeout in seconds")

    @computed_field
    @property
    def allowed_types_list(self) -> list[str]:
        """Get allowed document types as a list."""
        return [t.strip().lower() for t in self.allowed_types.split(",")]

    @computed_field
    @property
    def max_size_bytes(self) -> int:
        """Convert max size to bytes."""
        size_str = self.max_upload_size.upper()
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        if size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)


class RAGSettings(BaseModel):
    """RAG (Retrieval-Augmented Generation) configuration settings."""

    max_context_length: int = Field(default=4000, description="Maximum context length for RAG")
    overlap_ratio: float = Field(default=0.1, description="Overlap ratio for context chunks")
    min_score: float = Field(default=0.3, description="Minimum similarity score")
    max_documents: int = Field(default=10, description="Maximum documents to retrieve")


class KnowledgeSettings(BaseModel):
    """Knowledge management configuration settings."""

    vector_db: VectorDBSettings = Field(default_factory=VectorDBSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    document_processing: DocumentProcessingSettings = Field(default_factory=DocumentProcessingSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)


class Settings(BaseSettings):
    """Main application settings using Pydantic BaseSettings.

    This class automatically loads configuration from:
    1. Environment variables (highest priority)
    2. TOML configuration files
    3. Default values (lowest priority)
    """

    model_config = SettingsConfigDict(
        # Environment variable settings
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        # Allow extra fields for dynamic configuration
        extra="allow",
    )

    # ===============================
    # Core Application Settings
    # ===============================
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # ===============================
    # LLM Configuration
    # ===============================
    # Default LLM settings (can be overridden by named configurations)
    llm_model: str = Field(default="gpt-4o-mini", description="Default LLM model")
    llm_base_url: str = Field(default="https://api.openai.com/v1", description="Default LLM base URL")
    llm_api_key: str = Field(default="", description="Default LLM API key")
    llm_max_tokens: int = Field(default=4096, description="Default max tokens")
    llm_temperature: float = Field(default=0.7, description="Default temperature")
    llm_api_type: str = Field(default="openai", description="Default API type")
    llm_api_version: str = Field(default="", description="Default API version")
    llm_max_input_tokens: int | None = Field(default=None, description="Default max input tokens")

    # ===============================
    # Browser Configuration
    # ===============================
    browser_headless: bool = Field(default=False, description="Browser headless mode")
    browser_disable_security: bool = Field(default=True, description="Disable browser security")
    browser_max_content_length: int = Field(default=2000, description="Max content length")
    browser_chrome_instance_path: str | None = Field(default=None, description="Chrome instance path")
    browser_wss_url: str | None = Field(default=None, description="WebSocket URL")
    browser_cdp_url: str | None = Field(default=None, description="CDP URL")

    # Browser proxy settings
    browser_proxy_server: str | None = Field(default=None, description="Proxy server")
    browser_proxy_username: str | None = Field(default=None, description="Proxy username")
    browser_proxy_password: str | None = Field(default=None, description="Proxy password")

    # ===============================
    # Search Configuration
    # ===============================
    search_engine: str = Field(default="Google", description="Primary search engine")
    search_retry_delay: int = Field(default=60, description="Search retry delay")
    search_max_retries: int = Field(default=3, description="Search max retries")
    search_lang: str = Field(default="en", description="Search language")
    search_country: str = Field(default="us", description="Search country")

    # ===============================
    # Sandbox Configuration
    # ===============================
    sandbox_use_sandbox: bool = Field(default=False, description="Use sandbox")
    sandbox_image: str = Field(default="python:3.12-slim", description="Sandbox image")
    sandbox_work_dir: str = Field(default="/workspace", description="Sandbox work directory")
    sandbox_memory_limit: str = Field(default="512m", description="Sandbox memory limit")
    sandbox_cpu_limit: float = Field(default=1.0, description="Sandbox CPU limit")
    sandbox_timeout: int = Field(default=300, description="Sandbox timeout")
    sandbox_network_enabled: bool = Field(default=False, description="Sandbox network access")

    # ===============================
    # TTS Configuration
    # ===============================
    elevenlabs_api_key: str | None = Field(default=None, description="ElevenLabs API key")
    podcast_host_1_voice_id: str = Field(default="default", description="Podcast host 1 voice ID")
    podcast_host_2_voice_id: str = Field(default="default", description="Podcast host 2 voice ID")
    podcast_output_dir: str = Field(default="output/podcasts", description="Podcast output directory")

    # ===============================
    # Code Execution Settings
    # ===============================
    code_execution_enabled: bool = Field(default=True, description="Enable code execution")
    code_execution_timeout: int = Field(default=30, description="Code execution timeout")
    code_execution_memory_limit: int = Field(default=100, description="Code execution memory limit (MB)")
    code_execution_max_output: int = Field(default=10000, description="Max code execution output (characters)")
    code_execution_restricted_python: bool = Field(default=True, description="Use restricted Python")

    # ===============================
    # Tool Execution & Sandboxing
    # ===============================
    tool_execution_timeout: int = Field(default=30, description="Tool execution timeout")
    tool_sandbox_enabled: bool = Field(default=True, description="Enable tool sandbox")
    tool_sandbox_memory_limit: str = Field(default="128m", description="Tool sandbox memory limit")
    tool_sandbox_cpu_limit: float = Field(default=0.5, description="Tool sandbox CPU limit")
    tool_sandbox_network_disabled: bool = Field(default=True, description="Disable tool sandbox network")
    tool_force_sandbox_unsafe: bool = Field(default=True, description="Force sandbox for unsafe tools")

    # ===============================
    # Vector Database Configuration
    # ===============================
    vector_db_host: str = Field(default="localhost", description="Vector DB host")
    vector_db_port: int = Field(default=8000, description="Vector DB port")
    vector_db_url: str = Field(default="http://localhost:8000", description="Vector DB URL")
    vector_collection_name: str = Field(default="openmanus_documents", description="Documents collection")
    vector_workflow_collection: str = Field(default="openmanus_workflows", description="Workflows collection")
    chroma_auth_token: str | None = Field(default=None, description="ChromaDB auth token")
    chroma_auth_header: str = Field(default="X-Chroma-Token", description="ChromaDB auth header")

    # ===============================
    # Embedding Configuration
    # ===============================
    vector_embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model")
    vector_embedding_dimension: int = Field(default=384, description="Embedding dimension")
    embedding_normalize: bool = Field(default=True, description="Normalize embeddings")
    embedding_batch_size: int = Field(default=32, description="Embedding batch size")
    embedding_max_length: int = Field(default=512, description="Max embedding text length")
    embedding_truncate: bool = Field(default=True, description="Truncate long text")
    embedding_openai_api_key: str | None = Field(default=None, description="OpenAI API key for embeddings")
    embedding_ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")

    # ===============================
    # Document Processing Configuration
    # ===============================
    vector_chunk_size: int = Field(default=1000, description="Document chunk size")
    vector_chunk_overlap: int = Field(default=200, description="Document chunk overlap")
    document_max_size_bytes: int = Field(default=50 * 1024 * 1024, description="Max document size (50MB)")
    document_storage_path: str = Field(default="./data/documents", description="Document storage path")
    document_processing_timeout: int = Field(default=300, description="Document processing timeout")
    document_allowed_types: str = Field(default="pdf,txt,md,docx", description="Allowed document types")

    @computed_field
    @property
    def upload_dir(self) -> str:
        """Get upload directory from TOML config."""
        toml_config = self._load_toml_config()
        upload_config = toml_config.get("upload", {})
        return upload_config.get("directory", "./uploads")

    # ===============================
    # RAG Configuration
    # ===============================
    vector_search_k: int = Field(default=5, description="Number of documents to retrieve")
    vector_search_threshold: float = Field(default=0.7, description="Search similarity threshold")
    rag_max_context_length: int = Field(default=4000, description="Max RAG context length")
    rag_overlap_ratio: float = Field(default=0.1, description="RAG overlap ratio")
    rag_min_score: float = Field(default=0.3, description="RAG minimum score")
    rag_max_documents: int = Field(default=10, description="Max RAG documents")

    # ===============================
    # MCP Configuration
    # ===============================
    mcp_server_reference: str = Field(default="app.mcp.server", description="MCP server reference")

    # ===============================
    # Paths
    # ===============================
    @computed_field
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return PROJECT_ROOT

    @computed_field
    @property
    def workspace_root(self) -> Path:
        """Get the workspace root directory."""
        return PROJECT_ROOT / "workspace"

    @computed_field
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory."""
        return PROJECT_ROOT / "config"

    # ===============================
    # Configuration Loading Methods
    # ===============================
    def _load_toml_config(self) -> dict[str, Any]:
        """Load configuration from TOML files."""
        config_data = {}

        # Load base configuration
        base_config_path = self.config_dir / "config.toml"
        if base_config_path.exists():
            with base_config_path.open("rb") as f:
                config_data.update(tomllib.load(f))

        # Load environment-specific configuration
        env_config_path = self.config_dir / f"{self.environment}.toml"
        if env_config_path.exists():
            with env_config_path.open("rb") as f:
                env_config = tomllib.load(f)
                # Merge environment config over base config
                self._deep_merge_dict(config_data, env_config)

        # Load example config as fallback
        if not config_data:
            example_config_path = self.config_dir / "examples" / "config.example.toml"
            if example_config_path.exists():
                with example_config_path.open("rb") as f:
                    config_data.update(tomllib.load(f))

        return config_data

    def _deep_merge_dict(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Deep merge override dict into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value

    def _load_mcp_config(self) -> dict[str, MCPServerConfig]:
        """Load MCP server configuration from JSON file."""
        # Try specialized config first
        config_path = self.config_dir / "mcp.specialized.json"
        if not config_path.exists():
            config_path = self.config_dir / "mcp.json"

        if not config_path.exists():
            return {}

        try:
            with config_path.open() as f:
                data = json.load(f)
                servers = {}

                for server_id, server_config in data.get("mcpServers", {}).items():
                    servers[server_id] = MCPServerConfig(
                        type=server_config["type"],
                        url=server_config.get("url"),
                        command=server_config.get("command"),
                        args=server_config.get("args", []),
                    )
                return servers
        except Exception as e:
            raise ValueError(f"Failed to load MCP server config: {e}") from e

    # ===============================
    # Structured Configuration Properties
    # ===============================
    @computed_field
    @property
    def llm_configs(self) -> dict[str, LLMSettings]:
        """Get LLM configurations from TOML."""
        toml_config = self._load_toml_config()
        llm_config = toml_config.get("llm", {})

        # Extract base LLM settings
        base_settings = {
            "model": llm_config.get("model", self.llm_model),
            "base_url": llm_config.get("base_url", self.llm_base_url),
            "api_key": llm_config.get("api_key", self.llm_api_key),
            "max_tokens": llm_config.get("max_tokens", self.llm_max_tokens),
            "max_input_tokens": llm_config.get("max_input_tokens", self.llm_max_input_tokens),
            "temperature": llm_config.get("temperature", self.llm_temperature),
            "api_type": llm_config.get("api_type", self.llm_api_type),
            "api_version": llm_config.get("api_version", self.llm_api_version),
        }

        # Get named configurations
        llm_overrides = {k: v for k, v in llm_config.items() if isinstance(v, dict)}

        # Build final LLM configurations
        configs = {"default": LLMSettings(**base_settings)}

        for name, override_config in llm_overrides.items():
            merged_config = {**base_settings, **override_config}
            configs[name] = LLMSettings(**merged_config)

        return configs

    @computed_field
    @property
    def browser_config(self) -> BrowserSettings | None:
        """Get browser configuration."""
        toml_config = self._load_toml_config()
        browser_config = toml_config.get("browser", {})

        if not browser_config and not any(
            [
                self.browser_proxy_server,
                self.browser_chrome_instance_path,
                self.browser_wss_url,
                self.browser_cdp_url,
            ]
        ):
            return None

        # Handle proxy settings
        proxy_settings = None
        proxy_config = browser_config.get("proxy", {})
        if proxy_config.get("server") or self.browser_proxy_server:
            proxy_settings = ProxySettings(
                server=proxy_config.get("server", self.browser_proxy_server),
                username=proxy_config.get("username", self.browser_proxy_username),
                password=proxy_config.get("password", self.browser_proxy_password),
            )

        return BrowserSettings(
            headless=browser_config.get("headless", self.browser_headless),
            disable_security=browser_config.get("disable_security", self.browser_disable_security),
            extra_chromium_args=browser_config.get("extra_chromium_args", []),
            chrome_instance_path=browser_config.get("chrome_instance_path", self.browser_chrome_instance_path),
            wss_url=browser_config.get("wss_url", self.browser_wss_url),
            cdp_url=browser_config.get("cdp_url", self.browser_cdp_url),
            proxy=proxy_settings,
            max_content_length=browser_config.get("max_content_length", self.browser_max_content_length),
        )

    @computed_field
    @property
    def search_config(self) -> SearchSettings:
        """Get search configuration."""
        toml_config = self._load_toml_config()
        search_config = toml_config.get("search", {})

        return SearchSettings(
            engine=search_config.get("engine", self.search_engine),
            fallback_engines=search_config.get("fallback_engines", ["DuckDuckGo", "Baidu", "Bing"]),
            retry_delay=search_config.get("retry_delay", self.search_retry_delay),
            max_retries=search_config.get("max_retries", self.search_max_retries),
            lang=search_config.get("lang", self.search_lang),
            country=search_config.get("country", self.search_country),
        )

    @computed_field
    @property
    def sandbox_config(self) -> SandboxSettings:
        """Get sandbox configuration."""
        toml_config = self._load_toml_config()
        sandbox_config = toml_config.get("sandbox", {})

        return SandboxSettings(
            use_sandbox=sandbox_config.get("use_sandbox", self.sandbox_use_sandbox),
            image=sandbox_config.get("image", self.sandbox_image),
            work_dir=sandbox_config.get("work_dir", self.sandbox_work_dir),
            memory_limit=sandbox_config.get("memory_limit", self.sandbox_memory_limit),
            cpu_limit=sandbox_config.get("cpu_limit", self.sandbox_cpu_limit),
            timeout=sandbox_config.get("timeout", self.sandbox_timeout),
            network_enabled=sandbox_config.get("network_enabled", self.sandbox_network_enabled),
        )

    @computed_field
    @property
    def mcp_config(self) -> MCPSettings:
        """Get MCP configuration."""
        toml_config = self._load_toml_config()
        mcp_config = toml_config.get("mcp", {})

        return MCPSettings(
            server_reference=mcp_config.get("server_reference", self.mcp_server_reference),
            servers=self._load_mcp_config(),
        )

    @computed_field
    @property
    def knowledge_config(self) -> KnowledgeSettings:
        """Get knowledge management configuration."""
        return KnowledgeSettings(
            vector_db=VectorDBSettings(
                host=self.vector_db_host,
                port=self.vector_db_port,
                url=self.vector_db_url,
                auth_token=self.chroma_auth_token,
                auth_header=self.chroma_auth_header,
                documents_collection=self.vector_collection_name,
                workflows_collection=self.vector_workflow_collection,
            ),
            embedding=EmbeddingSettings(
                model_name=self.vector_embedding_model,
                dimension=self.vector_embedding_dimension,
                normalize=self.embedding_normalize,
                batch_size=self.embedding_batch_size,
                max_length=self.embedding_max_length,
                truncate=self.embedding_truncate,
                openai_api_key=self.embedding_openai_api_key,
                ollama_base_url=self.embedding_ollama_base_url,
            ),
            document_processing=DocumentProcessingSettings(
                chunk_size=self.vector_chunk_size,
                chunk_overlap=self.vector_chunk_overlap,
                search_k=self.vector_search_k,
                search_threshold=self.vector_search_threshold,
                max_upload_size=f"{self.document_max_size_bytes // (1024*1024)}MB",
                allowed_types=self.document_allowed_types,
                storage_path=self.document_storage_path,
                processing_timeout=self.document_processing_timeout,
            ),
            rag=RAGSettings(
                max_context_length=self.rag_max_context_length,
                overlap_ratio=self.rag_overlap_ratio,
                min_score=self.rag_min_score,
                max_documents=self.rag_max_documents,
            ),
        )

    @computed_field
    @property
    def upload_config(self) -> dict[str, Any]:
        """Get upload configuration from TOML."""
        toml_config = self._load_toml_config()
        upload_config = toml_config.get("upload", {})

        return {
            "directory": upload_config.get("directory", self.upload_dir),
            "max_file_size": upload_config.get("max_file_size", "50MB"),
            "allowed_extensions": upload_config.get(
                "allowed_extensions",
                ["pdf", "txt", "md", "docx", "json", "csv", "xlsx"],
            ),
        }

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_envs = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()


# ===============================
# Global Settings Instance
# ===============================
def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings()


# Create global settings instance
settings = get_settings()

# Backward compatibility alias
config = settings
