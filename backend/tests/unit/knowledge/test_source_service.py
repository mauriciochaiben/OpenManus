"""Unit tests for SourceService."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, UploadFile

sys.path.append("/Users/mauriciochaiben/OpenManus")

from backend.app.knowledge.models.chunk import DocumentChunk
from backend.app.knowledge.models.source import DocumentStatus, DocumentType
from backend.app.knowledge.services.source_service import (
    FileProcessingError,
    SourceService,
    SourceServiceError,
    UnsupportedFileTypeError,
)


class TestSourceService:
    """Test cases for SourceService."""

    @pytest.fixture
    def temp_upload_dir(self):
        """Create temporary upload directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store client."""
        mock_store = AsyncMock()
        mock_store.create_collection = AsyncMock()
        mock_store.add_documents = AsyncMock(return_value=["vec1", "vec2", "vec3"])
        return mock_store

    @pytest.fixture
    def mock_embedding_service(self):
        """Mock embedding service."""
        mock_service = AsyncMock()
        mock_service.generate_embeddings = AsyncMock(
            return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        )
        mock_service.model_name = "test-model"
        return mock_service

    @pytest.fixture
    def source_service(
        self, temp_upload_dir, mock_vector_store, mock_embedding_service
    ):
        """Create SourceService instance with mocked dependencies."""
        with patch(
            "app.knowledge.services.source_service.document_processing_config"
        ) as mock_config:
            mock_config.storage_path = str(temp_upload_dir)
            mock_config.max_file_size = 10 * 1024 * 1024  # 10MB
            mock_config.allowed_types = ["pdf", "txt", "md", "docx"]
            mock_config.chunk_size = 1000
            mock_config.chunk_overlap = 200

            service = SourceService()

            # Mock dependencies
            with patch(
                "app.knowledge.services.source_service.get_vector_store",
                return_value=mock_vector_store,
            ):
                with patch(
                    "app.knowledge.services.source_service.get_embedding_service",
                    return_value=mock_embedding_service,
                ):
                    yield service

    @pytest.fixture
    def mock_upload_file(self):
        """Create mock UploadFile."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_document.pdf"
        mock_file.size = 1024
        mock_file.read = AsyncMock(return_value=b"test content")
        mock_file.seek = AsyncMock()
        return mock_file

    @pytest.mark.asyncio
    async def test_upload_source_success(self, source_service, mock_upload_file):
        """Test successful file upload."""
        with patch.object(source_service, "_validate_file", new_callable=AsyncMock):
            with patch.object(
                source_service, "_save_file", new_callable=AsyncMock
            ) as mock_save:
                mock_save.return_value = ("/path/to/file", "hash123")

                with patch.object(
                    source_service, "_create_source_record", new_callable=AsyncMock
                ) as mock_create:
                    from app.knowledge.models.source import SourceDocument

                    mock_doc = SourceDocument(
                        filename="test_document.pdf",
                        content_hash="hash123",
                        status=DocumentStatus.PENDING,
                    )
                    mock_create.return_value = mock_doc

                    with patch("asyncio.create_task") as mock_task:
                        result = await source_service.upload_source(mock_upload_file)

                        assert result.filename == "test_document.pdf"
                        assert result.status == DocumentStatus.PENDING
                        assert result.content_hash == "hash123"
                        mock_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_file_size_limit(self, source_service):
        """Test file size validation."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "large_file.pdf"
        mock_file.size = 100 * 1024 * 1024  # 100MB

        with pytest.raises(HTTPException) as exc_info:
            await source_service._validate_file(mock_file)

        assert exc_info.value.status_code == 413
        assert "File too large" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_validate_file_unsupported_type(self, source_service):
        """Test unsupported file type validation."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.exe"
        mock_file.size = 1024

        with pytest.raises(HTTPException) as exc_info:
            await source_service._validate_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_save_file_and_calculate_hash(
        self, source_service, mock_upload_file, temp_upload_dir
    ):
        """Test file saving and hash calculation."""
        test_content = b"test file content for hashing"
        mock_upload_file.read.return_value = test_content

        file_path, content_hash = await source_service._save_file(mock_upload_file)

        assert Path(file_path).exists()
        assert content_hash is not None
        assert len(content_hash) == 64  # SHA-256 hash length

        # Verify file content
        with open(file_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == test_content

    @pytest.mark.asyncio
    async def test_extract_pdf_content(self, source_service, temp_upload_dir):
        """Test PDF text extraction."""
        # Create a mock PDF file
        pdf_path = temp_upload_dir / "test.pdf"
        pdf_path.write_bytes(b"fake pdf content")

        with patch("app.knowledge.services.source_service.PdfReader") as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Extracted PDF text content"

            mock_pdf = Mock()
            mock_pdf.pages = [mock_page]
            mock_reader.return_value = mock_pdf

            content = await source_service._extract_pdf_content(str(pdf_path))

            assert "Extracted PDF text content" in content
            assert "[Page 1]" in content

    @pytest.mark.asyncio
    async def test_extract_text_content_plain(self, source_service, temp_upload_dir):
        """Test plain text extraction."""
        # Create test text file
        text_path = temp_upload_dir / "test.txt"
        test_content = "This is test text content\nwith multiple lines."
        text_path.write_text(test_content, encoding="utf-8")

        content = await source_service._extract_text_content_plain(str(text_path))

        assert content == test_content

    @pytest.mark.asyncio
    async def test_extract_unsupported_file_type(self, source_service):
        """Test extraction of unsupported file type."""
        with pytest.raises(UnsupportedFileTypeError):
            await source_service._extract_text_content("/path/to/file.xyz", None)

    @pytest.mark.asyncio
    async def test_create_text_chunks(self, source_service):
        """Test text chunking functionality."""
        content = (
            "This is a test document. " * 100
        )  # Long content to create multiple chunks
        source_id = "test-source-123"

        chunks = await source_service._create_text_chunks(content, source_id)

        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.source_document_id == source_id for chunk in chunks)
        assert all(chunk.content_length == len(chunk.content) for chunk in chunks)

        # Check chunk indexing
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    @pytest.mark.asyncio
    async def test_process_embeddings_success(
        self, source_service, mock_vector_store, mock_embedding_service
    ):
        """Test successful embedding processing."""
        from app.knowledge.models.source import SourceDocument

        # Create test chunks
        chunks = [
            DocumentChunk(
                source_document_id="test-doc",
                content="Test chunk 1",
                chunk_index=0,
                content_length=12,
            ),
            DocumentChunk(
                source_document_id="test-doc",
                content="Test chunk 2",
                chunk_index=1,
                content_length=12,
            ),
        ]

        source_doc = SourceDocument(
            filename="test.pdf", content_hash="hash123", document_type=DocumentType.PDF
        )

        with patch(
            "app.knowledge.services.source_service.get_vector_store",
            return_value=mock_vector_store,
        ):
            with patch(
                "app.knowledge.services.source_service.get_embedding_service",
                return_value=mock_embedding_service,
            ):
                embedding_count = await source_service._process_embeddings(
                    chunks, source_doc
                )

        assert embedding_count == 3  # Mocked return value
        mock_vector_store.create_collection.assert_called_once()
        mock_vector_store.add_documents.assert_called_once()

        # Verify vector store call arguments
        call_args = mock_vector_store.add_documents.call_args
        assert call_args.kwargs["documents"] == ["Test chunk 1", "Test chunk 2"]
        assert len(call_args.kwargs["metadatas"]) == 2
        assert all(
            "source_document_id" in meta for meta in call_args.kwargs["metadatas"]
        )

    @pytest.mark.asyncio
    async def test_process_source_full_workflow(self, source_service, temp_upload_dir):
        """Test complete source processing workflow."""
        # Create test file
        test_file = temp_upload_dir / "test.txt"
        test_content = "This is test content for processing. " * 50
        test_file.write_text(test_content)

        source_id = "test-source-123"

        with patch.object(
            source_service, "_process_embeddings", new_callable=AsyncMock
        ) as mock_embeddings:
            mock_embeddings.return_value = 5

            # Mock source document retrieval
            with patch.object(
                source_service, "get_source_document", new_callable=AsyncMock
            ) as mock_get:
                from app.knowledge.models.source import SourceDocument

                mock_doc = SourceDocument(
                    id=source_id,
                    filename="test.txt",
                    content_hash="hash123",
                    file_path=str(test_file),
                )
                mock_get.return_value = mock_doc

                await source_service._process_source(str(test_file), source_id)

                mock_embeddings.assert_called_once()
                # Verify that chunks were created and embeddings processed
                call_args = mock_embeddings.call_args[0]
                chunks, source_doc = call_args
                assert len(chunks) > 0
                assert source_doc.id == source_id

    @pytest.mark.asyncio
    async def test_process_source_failure_handling(self, source_service):
        """Test error handling during source processing."""
        source_id = "test-source-123"
        invalid_file_path = "/nonexistent/file.txt"

        with pytest.raises(FileProcessingError):
            await source_service._process_source(invalid_file_path, source_id)

    @pytest.mark.asyncio
    async def test_search_documents(self, source_service, mock_vector_store):
        """Test document search functionality."""
        # Mock search results
        mock_results = {
            "documents": [["Found document 1", "Found document 2"]],
            "metadatas": [
                [
                    {"source_document_id": "doc1", "filename": "file1.pdf"},
                    {"source_document_id": "doc2", "filename": "file2.pdf"},
                ]
            ],
            "distances": [[0.1, 0.3]],
        }
        mock_vector_store.search_similar.return_value = mock_results

        with patch(
            "app.knowledge.services.source_service.get_vector_store",
            return_value=mock_vector_store,
        ):
            results = await source_service.search_documents(
                query="test query", n_results=5, category="research"
            )

        assert results == mock_results
        mock_vector_store.search_similar.assert_called_once()

        # Verify search parameters
        call_args = mock_vector_store.search_similar.call_args
        assert call_args.kwargs["query_texts"] == ["test query"]
        assert call_args.kwargs["n_results"] == 5
        assert call_args.kwargs["where"] == {"category": "research"}

    @pytest.mark.asyncio
    async def test_delete_source_document(self, source_service, mock_vector_store):
        """Test source document deletion."""
        source_id = "test-source-123"

        # Mock source document with file path
        with patch.object(
            source_service, "get_source_document", new_callable=AsyncMock
        ) as mock_get:
            from app.knowledge.models.source import SourceDocument

            mock_doc = SourceDocument(
                id=source_id,
                filename="test.pdf",
                content_hash="hash123",
                file_path="/path/to/test.pdf",
            )
            mock_get.return_value = mock_doc

            # Mock file deletion
            with patch("os.path.exists", return_value=True):
                with patch("os.unlink") as mock_unlink:
                    with patch(
                        "app.knowledge.services.source_service.get_vector_store",
                        return_value=mock_vector_store,
                    ):
                        result = await source_service.delete_source_document(source_id)

                        assert result is True
                        mock_vector_store.delete_documents.assert_called_once()
                        mock_unlink.assert_called_once_with("/path/to/test.pdf")

    @pytest.mark.asyncio
    async def test_status_transitions(self, source_service):
        """Test document status transitions during processing."""
        from app.knowledge.models.source import SourceDocument

        # Test initial status
        doc = SourceDocument(filename="test.pdf", content_hash="hash123")
        assert doc.status == DocumentStatus.PENDING

        # Test processing status
        doc.mark_as_processing()
        assert doc.status == DocumentStatus.PROCESSING
        assert doc.updated_at is not None
        assert doc.error_message is None

        # Test completed status
        doc.mark_as_completed(chunk_count=5, embedding_count=5)
        assert doc.status == DocumentStatus.COMPLETED
        assert doc.chunk_count == 5
        assert doc.embedding_count == 5
        assert doc.processed_at is not None

        # Test failed status
        error_msg = "Processing failed due to invalid format"
        doc.mark_as_failed(error_msg)
        assert doc.status == DocumentStatus.FAILED
        assert doc.error_message == error_msg
        assert doc.retry_count == 1

    def test_mime_type_validation(self, source_service):
        """Test MIME type validation for different file extensions."""
        # Test valid MIME types
        assert source_service._is_mime_type_allowed("application/pdf", "pdf")
        assert source_service._is_mime_type_allowed("text/plain", "txt")
        assert source_service._is_mime_type_allowed("text/markdown", "md")

        # Test invalid MIME types
        assert not source_service._is_mime_type_allowed("image/jpeg", "pdf")
        assert not source_service._is_mime_type_allowed("application/json", "txt")

    @pytest.mark.asyncio
    async def test_concurrent_uploads(self, source_service, temp_upload_dir):
        """Test handling of concurrent file uploads."""
        # Create multiple mock files
        mock_files = []
        for i in range(3):
            mock_file = MagicMock(spec=UploadFile)
            mock_file.filename = f"test_document_{i}.txt"
            mock_file.size = 1024
            mock_file.read = AsyncMock(return_value=f"content {i}".encode())
            mock_file.seek = AsyncMock()
            mock_files.append(mock_file)

        with patch.object(source_service, "_validate_file", new_callable=AsyncMock):
            with patch.object(
                source_service, "_create_source_record", new_callable=AsyncMock
            ) as mock_create:
                from app.knowledge.models.source import SourceDocument

                def create_doc(file, **kwargs):
                    return SourceDocument(
                        filename=file.filename,
                        content_hash=f"hash_{file.filename}",
                        status=DocumentStatus.PENDING,
                    )

                mock_create.side_effect = create_doc

                with patch("asyncio.create_task"):
                    # Upload files concurrently
                    tasks = [source_service.upload_source(file) for file in mock_files]
                    results = await asyncio.gather(*tasks)

                    assert len(results) == 3
                    assert all(doc.status == DocumentStatus.PENDING for doc in results)
                    assert (
                        len(set(doc.filename for doc in results)) == 3
                    )  # All unique filenames
