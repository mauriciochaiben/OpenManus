"""Document domain entity"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentStatus(Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


@dataclass
class Document:
    id: str
    filename: str
    stored_filename: str
    file_size: int
    file_type: str
    status: DocumentStatus
    uploaded_at: datetime
    file_path: str
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def create(
        cls,
        filename: str,
        stored_filename: str,
        file_size: int,
        file_type: str,
        file_path: str,
        **kwargs
    ):
        """Factory method to create a new document"""
        return cls(
            id=kwargs.get("id", ""),  # Will be set by repository
            filename=filename,
            stored_filename=stored_filename,
            file_size=file_size,
            file_type=file_type,
            status=DocumentStatus.UPLOADED,
            uploaded_at=datetime.utcnow(),
            file_path=file_path,
            **kwargs
        )

    def start_processing(self):
        """Start document processing"""
        self.status = DocumentStatus.PROCESSING

    def complete_processing(self, extracted_text: str = None):
        """Complete document processing"""
        self.status = DocumentStatus.PROCESSED
        if extracted_text:
            self.extracted_text = extracted_text

    def fail_processing(self, error_message: str):
        """Mark document processing as failed"""
        self.status = DocumentStatus.ERROR
        self.error_message = error_message
