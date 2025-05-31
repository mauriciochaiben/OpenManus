"""In-memory document repository implementation"""

import uuid
from typing import Dict, List, Optional

from app.domain.entities import Document
from app.repositories.interfaces import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory implementation of document repository"""

    def __init__(self):
        self._documents: Dict[str, Document] = {}

    async def create(self, document: Document) -> Document:
        """Create a new document"""
        if not document.id:
            document.id = str(uuid.uuid4())
        self._documents[document.id] = document
        return document

    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """Find document by ID"""
        return self._documents.get(document_id)

    async def find_all(self) -> List[Document]:
        """Get all documents"""
        return list(self._documents.values())

    async def update(self, document: Document) -> Document:
        """Update existing document"""
        if document.id not in self._documents:
            raise ValueError(f"Document with ID {document.id} not found")
        self._documents[document.id] = document
        return document

    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False
