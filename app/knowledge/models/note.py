"""
Note Model

Pydantic model for representing user notes that can reference knowledge sources.
Notes support markdown content and can be linked to knowledge sources for context.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


# Processing and Source Models
class ProcessingStatus(BaseModel):
    """Model for tracking processing status of knowledge sources."""

    status: str = Field(..., description="Processing status: pending, processing, completed, failed")
    progress: int | None = Field(default=None, ge=0, le=100, description="Processing progress percentage")
    processed_chunks: int | None = Field(default=None, ge=0, description="Number of chunks processed")
    total_chunks: int | None = Field(default=None, ge=0, description="Total number of chunks to process")
    error_message: str | None = Field(default=None, description="Error message if processing failed")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ProcessingResult(BaseModel):
    """Model for processing results."""

    success: bool = Field(..., description="Whether processing was successful")
    chunks_processed: int | None = Field(default=None, ge=0, description="Number of chunks successfully processed")
    total_chunks: int | None = Field(default=None, ge=0, description="Total number of chunks")
    processing_time: float | None = Field(default=None, ge=0, description="Processing time in seconds")
    error_message: str | None = Field(default=None, description="Error message if processing failed")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional processing metadata")


class KnowledgeSource(BaseModel):
    """Model for knowledge source documents."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier",
    )
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_type: str = Field(..., description="MIME type of the file")
    file_size: int | None = Field(default=None, ge=0, description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    status: str = Field(default="pending", description="Processing status")
    content_hash: str | None = Field(default=None, description="Content hash for deduplication")
    chunk_count: int | None = Field(default=None, ge=0, description="Number of chunks created")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")
    processing_status: ProcessingStatus | None = Field(default=None, description="Detailed processing status")


class Note(BaseModel):
    """
    Note model for storing user notes with markdown content.

    Notes can reference knowledge sources and support rich markdown formatting.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the note",
    )

    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")

    content: str = Field(..., description="Note content in Markdown format")

    source_ids: list[str] | None = Field(
        default=None, description="List of knowledge source IDs referenced by this note"
    )

    tags: list[str] | None = Field(default=None, description="Tags for categorizing and organizing notes")

    author_id: str | None = Field(default=None, description="ID of the user who created the note")

    is_public: bool = Field(default=False, description="Whether the note is publicly visible")

    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata for the note")

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the note was created",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the note was last updated",
    )

    @validator("source_ids")
    def validate_source_ids(cls, v):
        """Validate source IDs list."""
        if v is not None:
            # Remove duplicates and empty strings
            v = [sid.strip() for sid in v if sid and sid.strip()]
            # Remove duplicates while preserving order
            seen = set()
            v = [sid for sid in v if not (sid in seen or seen.add(sid))]
        return v if v else None

    @validator("tags")
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v is not None:
            # Clean tags: remove empty strings, strip whitespace, lowercase
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
            # Remove duplicates while preserving order
            seen = set()
            v = [tag for tag in v if not (tag in seen or seen.add(tag))]
        return v if v else None

    @validator("content")
    def validate_content(cls, v):
        """Validate note content."""
        if not v.strip():
            raise ValueError("Note content cannot be empty")
        return v.strip()

    @validator("updated_at", always=True)
    def set_updated_at(cls, v, values):  # noqa: ARG002
        """Automatically update the updated_at timestamp."""
        return datetime.utcnow()

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "id": "note-123e4567-e89b-12d3-a456-426614174000",
                "title": "AI Agent Architecture Notes",
                "content": (
                    "# AI Agent Architecture\n\n"
                    "## Key Components\n\n"
                    "- **Planning Agent**: Responsible for task decomposition\n"
                    "- **Tool User Agent**: Executes tasks using available tools\n\n"
                    "## References\n\n"
                    "See the uploaded documentation for more details on implementation."
                ),
                "source_ids": ["source-456", "source-789"],
                "tags": ["ai", "architecture", "agents"],
                "author_id": "user-123",
                "is_public": False,
                "metadata": {"word_count": 45, "reading_time": "1 minute"},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T14:45:00Z",
            }
        }


class NoteCreate(BaseModel):
    """Model for creating a new note."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")

    content: str = Field(..., description="Note content in Markdown format")

    source_ids: list[str] | None = Field(
        default=None, description="List of knowledge source IDs referenced by this note"
    )

    tags: list[str] | None = Field(default=None, description="Tags for categorizing the note")

    is_public: bool = Field(default=False, description="Whether the note should be publicly visible")

    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata for the note")

    @validator("source_ids")
    def validate_source_ids(cls, v):
        """Validate source IDs list."""
        if v is not None:
            v = [sid.strip() for sid in v if sid and sid.strip()]
            seen = set()
            v = [sid for sid in v if not (sid in seen or seen.add(sid))]
        return v if v else None

    @validator("tags")
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v is not None:
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
            seen = set()
            v = [tag for tag in v if not (tag in seen or seen.add(tag))]
        return v if v else None

    @validator("content")
    def validate_content(cls, v):
        """Validate note content."""
        if not v.strip():
            raise ValueError("Note content cannot be empty")
        return v.strip()


class NoteUpdate(BaseModel):
    """Model for updating an existing note."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Updated title of the note")

    content: str | None = Field(None, description="Updated note content in Markdown format")

    source_ids: list[str] | None = Field(None, description="Updated list of knowledge source IDs")

    tags: list[str] | None = Field(None, description="Updated tags for the note")

    is_public: bool | None = Field(None, description="Updated visibility setting")

    metadata: dict[str, Any] | None = Field(None, description="Updated metadata for the note")

    @validator("source_ids")
    def validate_source_ids(cls, v):
        """Validate source IDs list."""
        if v is not None:
            v = [sid.strip() for sid in v if sid and sid.strip()]
            seen = set()
            v = [sid for sid in v if not (sid in seen or seen.add(sid))]
        return v if v else None

    @validator("tags")
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v is not None:
            v = [tag.strip().lower() for tag in v if tag and tag.strip()]
            seen = set()
            v = [tag for tag in v if not (tag in seen or seen.add(tag))]
        return v if v else None

    @validator("content")
    def validate_content(cls, v):
        """Validate note content."""
        if v is not None and not v.strip():
            raise ValueError("Note content cannot be empty")
        return v.strip() if v is not None else v


class NoteResponse(BaseModel):
    """Model for note API responses."""

    id: str
    title: str
    content: str
    source_ids: list[str] | None
    tags: list[str] | None
    author_id: str | None
    is_public: bool
    metadata: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    # Additional computed fields
    word_count: int | None = Field(None, description="Computed word count of the note content")

    reading_time: str | None = Field(None, description="Estimated reading time for the note")

    source_count: int | None = Field(None, description="Number of referenced knowledge sources")

    @classmethod
    def from_note(cls, note: Note) -> "NoteResponse":
        """Create a NoteResponse from a Note model."""
        # Calculate word count
        word_count = len(note.content.split()) if note.content else 0

        # Estimate reading time (average 200 words per minute)
        reading_time_minutes = max(1, word_count // 200)
        reading_time = f"{reading_time_minutes} minute{'s' if reading_time_minutes != 1 else ''}"

        # Count referenced sources
        source_count = len(note.source_ids) if note.source_ids else 0

        return cls(
            id=note.id,
            title=note.title,
            content=note.content,
            source_ids=note.source_ids,
            tags=note.tags,
            author_id=note.author_id,
            is_public=note.is_public,
            metadata=note.metadata,
            created_at=note.created_at,
            updated_at=note.updated_at,
            word_count=word_count,
            reading_time=reading_time,
            source_count=source_count,
        )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class NoteSearchQuery(BaseModel):
    """Model for note search queries."""

    query: str | None = Field(None, description="Text query to search in note title and content")

    tags: list[str] | None = Field(None, description="Filter by specific tags")

    source_ids: list[str] | None = Field(None, description="Filter by notes that reference specific sources")

    author_id: str | None = Field(None, description="Filter by author ID")

    is_public: bool | None = Field(None, description="Filter by public/private status")

    created_after: datetime | None = Field(None, description="Filter notes created after this date")

    created_before: datetime | None = Field(None, description="Filter notes created before this date")

    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of results to return")

    offset: int = Field(default=0, ge=0, description="Number of results to skip")

    sort_by: str = Field(default="updated_at", description="Field to sort by")

    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order: asc or desc")


class NoteSearchResponse(BaseModel):
    """Model for note search results."""

    notes: list[NoteResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
