"""Global test configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from main import app  # Import the app here to avoid circular imports

    with TestClient(app) as client:
        yield client


@pytest.fixture
def temp_directory():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    mock_store = AsyncMock()
    mock_store.create_collection = AsyncMock()
    mock_store.add_documents = AsyncMock(return_value=["vec1", "vec2"])
    mock_store.search_similar = AsyncMock(
        return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]}
    )
    mock_store.delete_documents = AsyncMock()
    return mock_store


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    mock_service = AsyncMock()
    mock_service.generate_embeddings = AsyncMock(
        return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    )
    mock_service.model_name = "test-embedding-model"
    mock_service.get_dimension = Mock(return_value=384)
    return mock_service


@pytest.fixture
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
