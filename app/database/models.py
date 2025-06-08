"""
Database models for OpenManus application.

SQLAlchemy models for database persistence.
"""

from datetime import datetime
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NoteModel(Base):
    """SQLAlchemy model for notes table."""

    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    source_ids = Column(JSON, nullable=True)  # List of source IDs
    tags = Column(JSON, nullable=True)  # List of tags
    author_id = Column(String, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    note_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<NoteModel(id='{self.id}', title='{self.title}')>"


class SourceModel(Base):
    """SQLAlchemy model for source documents table."""

    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    content_hash = Column(String(64), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    file_size = Column(Integer, nullable=True)
    document_type = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    content_length = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    embedding_count = Column(Integer, default=0, nullable=False)
    file_path = Column(String(500), nullable=True)
    collection_name = Column(String(100), nullable=True)
    source_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    owner_id = Column(String, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<SourceModel(id='{self.id}', filename='{self.filename}', status='{self.status}')>"
