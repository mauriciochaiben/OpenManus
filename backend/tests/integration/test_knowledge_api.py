"""Integration tests for Knowledge API endpoints."""

import asyncio
import json
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

sys.path.append("/Users/mauriciochaiben/OpenManus")

from backend.app.knowledge.models.source import DocumentStatus
from backend.app.main import app


class TestKnowledgeAPI:
    """Integration tests for Knowledge API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_source_service(self):
        """Mock source service for testing."""
        mock_service = AsyncMock()
        return mock_service

    @pytest.fixture
    def sample_pdf_file(self):
        """Create sample PDF file for testing."""
        content = b"%PDF-1.4 fake pdf content for testing"
        return ("test_document.pdf", BytesIO(content), "application/pdf")

    @pytest.fixture
    def sample_text_file(self):
        """Create sample text file for testing."""
        content = b"This is a test text document with some content for processing."
        return ("test_document.txt", BytesIO(content), "text/plain")

    def test_upload_source_success(self, client, sample_pdf_file):
        """Test successful file upload."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id="test-source-123",
                filename="test_document.pdf",
                content_hash="hash123",
                status=DocumentStatus.PENDING,
            )
            mock_service.upload_source = AsyncMock(return_value=mock_doc)

            filename, file_content, content_type = sample_pdf_file

            response = client.post(
                "/knowledge/sources/upload",
                files={"file": (filename, file_content, content_type)},
                data={"category": "research", "tags": "test,pdf"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["source_id"] == "test-source-123"
            assert data["filename"] == "test_document.pdf"
            assert data["status"] == "pending"
            assert "uploaded successfully" in data["message"]

            # Verify service was called with correct parameters
            mock_service.upload_source.assert_called_once()
            call_args = mock_service.upload_source.call_args
            assert call_args.kwargs["category"] == "research"
            assert call_args.kwargs["tags"] == ["test", "pdf"]

    def test_upload_source_with_large_file(self, client):
        """Test upload with file exceeding size limit."""
        # Create a large file content
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from app.knowledge.services.source_service import SourceServiceError

            mock_service.upload_source = AsyncMock(
                side_effect=SourceServiceError("File too large")
            )

            response = client.post(
                "/knowledge/sources/upload",
                files={
                    "file": (
                        "large_file.pdf",
                        BytesIO(large_content),
                        "application/pdf",
                    )
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "File too large" in response.json()["detail"]

    def test_upload_source_unsupported_file_type(self, client):
        """Test upload with unsupported file type."""
        exe_content = b"fake executable content"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from app.knowledge.services.source_service import SourceServiceError

            mock_service.upload_source = AsyncMock(
                side_effect=SourceServiceError("Unsupported file type")
            )

            response = client.post(
                "/knowledge/sources/upload",
                files={
                    "file": (
                        "malware.exe",
                        BytesIO(exe_content),
                        "application/octet-stream",
                    )
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Unsupported file type" in response.json()["detail"]

    def test_get_source_status_success(self, client):
        """Test successful status retrieval."""
        source_id = "test-source-123"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from datetime import datetime

            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id=source_id,
                filename="test_document.pdf",
                content_hash="hash123",
                status=DocumentStatus.COMPLETED,
                chunk_count=5,
                embedding_count=5,
                created_at=datetime.utcnow(),
                processed_at=datetime.utcnow(),
            )
            mock_service.get_source_document = AsyncMock(return_value=mock_doc)

            response = client.get(f"/knowledge/sources/{source_id}/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["source_id"] == source_id
            assert data["filename"] == "test_document.pdf"
            assert data["status"] == "completed"
            assert data["chunk_count"] == 5
            assert data["embedding_count"] == 5
            assert "processing_progress" in data

    def test_get_source_status_not_found(self, client):
        """Test status retrieval for non-existent source."""
        source_id = "non-existent-source"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_service.get_source_document = AsyncMock(return_value=None)

            response = client.get(f"/knowledge/sources/{source_id}/status")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"]

    def test_get_source_status_processing(self, client):
        """Test status retrieval for document being processed."""
        source_id = "processing-source"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from datetime import datetime

            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id=source_id,
                filename="processing.pdf",
                content_hash="hash456",
                status=DocumentStatus.PROCESSING,
                created_at=datetime.utcnow(),
            )
            mock_service.get_source_document = AsyncMock(return_value=mock_doc)

            response = client.get(f"/knowledge/sources/{source_id}/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["status"] == "processing"
            assert data["processing_progress"] is not None
            assert "current_step" in data["processing_progress"]

    def test_get_source_status_failed(self, client):
        """Test status retrieval for failed document."""
        source_id = "failed-source"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from datetime import datetime

            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id=source_id,
                filename="failed.pdf",
                content_hash="hash789",
                status=DocumentStatus.FAILED,
                error_message="PDF parsing failed",
                created_at=datetime.utcnow(),
                processed_at=datetime.utcnow(),
            )
            mock_service.get_source_document = AsyncMock(return_value=mock_doc)

            response = client.get(f"/knowledge/sources/{source_id}/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["status"] == "failed"
            assert data["error_message"] == "PDF parsing failed"

    def test_list_sources_success(self, client):
        """Test successful source listing."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            # Mock will return empty list for now since implementation is pending
            response = client.get("/knowledge/sources")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert "sources" in data
            assert "total" in data
            assert "page" in data
            assert "page_size" in data
            assert data["page"] == 1
            assert data["page_size"] == 20

    def test_list_sources_with_pagination(self, client):
        """Test source listing with pagination parameters."""
        response = client.get(
            "/knowledge/sources",
            params={"page": 2, "page_size": 10, "status_filter": "completed"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["page"] == 2
        assert data["page_size"] == 10

    def test_search_documents_success(self, client):
        """Test successful document search."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_results = {
                "documents": [["Found document 1", "Found document 2"]],
                "metadatas": [
                    [
                        {
                            "source_document_id": "doc1",
                            "filename": "file1.pdf",
                            "chunk_index": 0,
                            "category": "research",
                        },
                        {
                            "source_document_id": "doc2",
                            "filename": "file2.pdf",
                            "chunk_index": 1,
                            "category": "research",
                        },
                    ]
                ],
                "distances": [[0.1, 0.3]],
            }
            mock_service.search_documents = AsyncMock(return_value=mock_results)

            search_request = {
                "query": "machine learning algorithms",
                "n_results": 5,
                "category": "research",
            }

            response = client.post("/knowledge/sources/search", json=search_request)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["query"] == "machine learning algorithms"
            assert data["total_found"] == 2
            assert len(data["results"]) == 2

            # Check result format
            result = data["results"][0]
            assert "content" in result
            assert "metadata" in result
            assert "similarity_score" in result
            assert "source_document_id" in result
            assert "filename" in result

    def test_search_documents_empty_results(self, client):
        """Test search with no matching documents."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            mock_service.search_documents = AsyncMock(return_value=mock_results)

            search_request = {"query": "non existent topic", "n_results": 5}

            response = client.post("/knowledge/sources/search", json=search_request)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["total_found"] == 0
            assert data["results"] == []

    def test_delete_source_success(self, client):
        """Test successful source deletion."""
        source_id = "test-source-123"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_service.delete_source_document = AsyncMock(return_value=True)

            response = client.delete(f"/knowledge/sources/{source_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert "deleted successfully" in data["message"]
            assert data["source_id"] == source_id

    def test_delete_source_not_found(self, client):
        """Test deletion of non-existent source."""
        source_id = "non-existent-source"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_service.delete_source_document = AsyncMock(return_value=False)

            response = client.delete(f"/knowledge/sources/{source_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"]

    def test_get_source_document_success(self, client):
        """Test successful source document retrieval."""
        source_id = "test-source-123"

        with patch("app.api.knowledge_api.source_service") as mock_service:
            from datetime import datetime

            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id=source_id,
                filename="test_document.pdf",
                content_hash="hash123",
                status=DocumentStatus.COMPLETED,
                created_at=datetime.utcnow(),
                metadata={"author": "Test Author"},
                tags=["research", "AI"],
            )
            mock_service.get_source_document = AsyncMock(return_value=mock_doc)

            response = client.get(f"/knowledge/sources/{source_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["id"] == source_id
            assert data["filename"] == "test_document.pdf"
            assert data["status"] == "completed"
            assert data["metadata"]["author"] == "Test Author"
            assert "research" in data["tags"]

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/knowledge/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "knowledge_api"
        assert "components" in data

    def test_upload_multiple_files_sequentially(
        self, client, sample_text_file, sample_pdf_file
    ):
        """Test uploading multiple files in sequence."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            from app.knowledge.models.source import SourceDocument

            def create_mock_doc(filename, doc_id):
                return SourceDocument(
                    id=doc_id,
                    filename=filename,
                    content_hash=f"hash_{doc_id}",
                    status=DocumentStatus.PENDING,
                )

            mock_service.upload_source = AsyncMock(
                side_effect=[
                    create_mock_doc("test_document.txt", "txt-123"),
                    create_mock_doc("test_document.pdf", "pdf-456"),
                ]
            )

            # Upload first file
            filename1, content1, type1 = sample_text_file
            response1 = client.post(
                "/knowledge/sources/upload",
                files={"file": (filename1, content1, type1)},
            )

            # Upload second file
            filename2, content2, type2 = sample_pdf_file
            response2 = client.post(
                "/knowledge/sources/upload",
                files={"file": (filename2, content2, type2)},
            )

            assert response1.status_code == status.HTTP_200_OK
            assert response2.status_code == status.HTTP_200_OK

            data1 = response1.json()
            data2 = response2.json()

            assert data1["source_id"] == "txt-123"
            assert data2["source_id"] == "pdf-456"
            assert data1["filename"] == "test_document.txt"
            assert data2["filename"] == "test_document.pdf"

    def test_search_with_filters(self, client):
        """Test search with various filters."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            mock_service.search_documents = AsyncMock(
                return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]}
            )

            search_request = {
                "query": "test query",
                "n_results": 10,
                "category": "research",
                "tags": ["AI", "machine-learning"],
                "owner_id": "user-123",
            }

            response = client.post("/knowledge/sources/search", json=search_request)

            assert response.status_code == status.HTTP_200_OK

            # Verify service was called with filters
            mock_service.search_documents.assert_called_once()
            call_args = mock_service.search_documents.call_args
            assert call_args.kwargs["category"] == "research"
            assert call_args.kwargs["tags"] == ["AI", "machine-learning"]
            assert call_args.kwargs["owner_id"] == "user-123"

    def test_upload_with_metadata(self, client, sample_pdf_file):
        """Test upload with additional metadata and tags."""
        with patch("app.api.knowledge_api.source_service") as mock_service:
            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id="test-source-456",
                filename="research_paper.pdf",
                content_hash="hash456",
                status=DocumentStatus.PENDING,
                category="academic",
                tags=["research", "AI", "deep-learning"],
            )
            mock_service.upload_source = AsyncMock(return_value=mock_doc)

            filename, file_content, content_type = sample_pdf_file

            response = client.post(
                "/knowledge/sources/upload",
                files={"file": ("research_paper.pdf", file_content, content_type)},
                data={
                    "category": "academic",
                    "tags": "research,AI,deep-learning",
                    "owner_id": "researcher-123",
                },
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["filename"] == "research_paper.pdf"

            # Verify service was called with metadata
            call_args = mock_service.upload_source.call_args
            assert call_args.kwargs["category"] == "academic"
            assert call_args.kwargs["tags"] == ["research", "AI", "deep-learning"]
            assert call_args.kwargs["owner_id"] == "researcher-123"
