"""Source document models for knowledge management."""

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import UUID4


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


class SourceDocument(BaseModel):
    """
    Pydantic model for source documents in the knowledge base.

    This model represents documents that have been uploaded and processed
    for embedding in the vector database.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the document",
    )

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

    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        description="Current processing status of the document",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the document was created",
    )

    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the document was last updated"
    )

    processed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the document processing completed"
    )

    # Document properties
    file_size: Optional[int] = Field(
        default=None, ge=0, description="File size in bytes"
    )

    document_type: Optional[DocumentType] = Field(
        default=None, description="Type of document based on file extension"
    )

    mime_type: Optional[str] = Field(
        default=None, description="MIME type of the document"
    )

    # Content and processing
    content: Optional[str] = Field(
        default=None, description="Extracted text content from the document"
    )

    content_length: Optional[int] = Field(
        default=None, ge=0, description="Length of extracted content in characters"
    )

    chunk_count: int = Field(
        default=0, ge=0, description="Number of chunks created from this document"
    )

    embedding_count: int = Field(
        default=0, ge=0, description="Number of embeddings created from this document"
    )

    # Storage and paths
    file_path: Optional[str] = Field(
        default=None, description="Local file system path where the document is stored"
    )

    collection_name: Optional[str] = Field(
        default=None,
        description="Vector database collection containing this document's embeddings",
    )

    # Processing metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the document"
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None, description="Error message if processing failed"
    )

    retry_count: int = Field(
        default=0, ge=0, description="Number of processing retry attempts"
    )

    # Tags and classification
    tags: List[str] = Field(
        default_factory=list, description="User-defined tags for the document"
    )

    category: Optional[str] = Field(
        default=None, description="Document category for organization"
    )

    # Access control
    owner_id: Optional[str] = Field(
        default=None, description="ID of the user who uploaded the document"
    )

    is_public: bool = Field(
        default=False, description="Whether the document is publicly accessible"
    )

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID4: lambda v: str(v)}
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "research_paper.pdf",
                "content_hash": "a1b2c3d4e5f6...",
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z",
                "file_size": 1024000,
                "document_type": "pdf",
                "mime_type": "application/pdf",
                "content_length": 5000,
                "chunk_count": 10,
                "embedding_count": 10,
                "collection_name": "openmanus_documents",
                "metadata": {
                    "author": "John Doe",
                    "subject": "AI Research",
                    "page_count": 25,
                },
                "tags": ["research", "ai", "machine-learning"],
                "category": "academic",
            }
        }

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        """Validate filename format and characters."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")

        # Remove path separators for security
        clean_filename = Path(v).name
        if clean_filename != v:
            raise ValueError("Filename cannot contain path separators")

        return clean_filename

    @field_validator("content_hash")
    @classmethod
    def validate_content_hash(cls, v):
        """Validate content hash format (SHA-256)."""
        if len(v) != 64:
            raise ValueError("Content hash must be 64 characters (SHA-256)")

        try:
            int(v, 16)  # Check if valid hexadecimal
        except ValueError:
            raise ValueError("Content hash must be valid hexadecimal")

        return v.lower()

    @field_validator("document_type", mode="before")
    @classmethod
    def infer_document_type(cls, v, info):
        """Infer document type from filename if not provided."""
        if v is None and info.data and "filename" in info.data:
            filename = info.data["filename"]
            extension = Path(filename).suffix.lower().lstrip(".")

            # Map extensions to document types
            type_mapping = {
                "pdf": DocumentType.PDF,
                "txt": DocumentType.TXT,
                "md": DocumentType.MARKDOWN,
                "markdown": DocumentType.MARKDOWN,
                "docx": DocumentType.DOCX,
                "doc": DocumentType.DOCX,
                "html": DocumentType.HTML,
                "htm": DocumentType.HTML,
                "json": DocumentType.JSON,
                "csv": DocumentType.CSV,
            }

            return type_mapping.get(extension)

        return v

    @field_validator("updated_at", mode="before")
    @classmethod
    def set_updated_at(cls, v, info):
        """Set updated_at to current time when status changes."""
        if (
            info.data
            and "status" in info.data
            and info.data["status"] != DocumentStatus.PENDING
        ):
            return datetime.utcnow()
        return v

    @field_validator("processed_at", mode="before")
    @classmethod
    def set_processed_at(cls, v, info):
        """Set processed_at when status is completed or failed."""
        if (
            info.data
            and "status" in info.data
            and info.data["status"]
            in [
                DocumentStatus.COMPLETED,
                DocumentStatus.FAILED,
            ]
        ):
            return datetime.utcnow()
        return v

    @model_validator(mode="after")
    def validate_content_consistency(self):
        """Validate consistency between content-related fields."""
        content = self.content
        content_length = self.content_length

        if content and content_length is None:
            self.content_length = len(content)
        elif content and content_length != len(content):
            raise ValueError("content_length must match actual content length")

        return self

    @model_validator(mode="after")
    def validate_status_consistency(self):
        """Validate consistency between status and related fields."""
        status = self.status
        error_message = self.error_message

        if status == DocumentStatus.FAILED and not error_message:
            raise ValueError("Failed documents must have an error message")

        if status != DocumentStatus.FAILED and error_message:
            self.error_message = None  # Clear error message for non-failed status

        return self

    def is_processing_complete(self) -> bool:
        """Check if document processing is complete."""
        return self.status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]

    def is_ready_for_search(self) -> bool:
        """Check if document is ready for vector search."""
        return (
            self.status == DocumentStatus.COMPLETED
            and self.embedding_count > 0
            and self.collection_name is not None
        )

    def mark_as_processing(self) -> None:
        """Mark document as currently processing."""
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.utcnow()
        self.error_message = None

    def mark_as_completed(self, chunk_count: int = 0, embedding_count: int = 0) -> None:
        """Mark document as successfully processed."""
        self.status = DocumentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.chunk_count = chunk_count
        self.embedding_count = embedding_count
        self.error_message = None

    def mark_as_failed(self, error_message: str) -> None:
        """Mark document as failed with error message."""
        self.status = DocumentStatus.FAILED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error_message = error_message
        self.retry_count += 1

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def remove_metadata(self, key: str) -> None:
        """Remove metadata entry."""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()


class SourceDocumentCreate(BaseModel):
    """Model for creating new source documents."""

    filename: str = Field(..., min_length=1, max_length=255)
    content_hash: str = Field(..., min_length=64, max_length=64)
    file_size: Optional[int] = Field(default=None, ge=0)
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    owner_id: Optional[str] = None
    is_public: bool = Field(default=False)


class SourceDocumentUpdate(BaseModel):
    """Model for updating existing source documents."""

    filename: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[DocumentStatus] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    error_message: Optional[str] = None


class SourceDocumentResponse(SourceDocument):
    """Response model for source documents (includes all fields)."""

    pass


class SourceDocumentSummary(BaseModel):
    """Summary model for listing source documents."""

    id: str
    filename: str
    status: DocumentStatus
    created_at: datetime
    updated_at: Optional[datetime]
    file_size: Optional[int]
    document_type: Optional[DocumentType]
    chunk_count: int
    embedding_count: int
    tags: List[str]
    category: Optional[str]
    is_public: bool
