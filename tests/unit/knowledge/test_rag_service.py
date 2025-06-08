import pytest

# Check dependencies early
pytest.importorskip("chromadb")

# Standard library imports
import sys
from typing import Any
from unittest.mock import AsyncMock, Mock

sys.path.append("/Users/mauriciochaiben/OpenManus")

# Application imports
from app.knowledge.infrastructure.vector_store_client import VectorStoreClient
from app.knowledge.services.embedding_service import EmbeddingService
from app.knowledge.services.rag_service import RagService


@pytest.fixture
def mock_embedding_service():
    """Mock EmbeddingService for testing."""
    service = Mock(spec=EmbeddingService)
    service.generate_embedding = AsyncMock()
    return service


@pytest.fixture
def mock_vector_store_client():
    """Mock VectorStoreClient for testing."""
    client = Mock(spec=VectorStoreClient)
    client.search = AsyncMock()
    return client


@pytest.fixture
def rag_service(mock_embedding_service, mock_vector_store_client):
    """RagService instance with mocked dependencies."""
    return RagService(
        embedding_service=mock_embedding_service,
        vector_store_client=mock_vector_store_client,
    )


@pytest.fixture
def sample_embedding():
    """Sample embedding vector for testing."""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional vector


@pytest.fixture
def sample_search_results():
    """Sample search results from vector store."""
    return [
        {
            "text": "This is the first relevant document about machine learning.",
            "score": 0.95,
            "metadata": {"source_id": "doc1", "page": 1},
        },
        {
            "text": "Second document discusses artificial intelligence concepts.",
            "score": 0.87,
            "metadata": {"source_id": "doc2", "page": 1},
        },
        {
            "text": "Third document covers deep learning fundamentals.",
            "score": 0.82,
            "metadata": {"source_id": "doc1", "page": 2},
        },
        {
            "content": "Fourth document with content field instead of text.",
            "score": 0.78,
            "metadata": {"source_id": "doc3", "page": 1},
        },
        {
            "text": "Fifth document about neural networks.",
            "score": 0.75,
            "metadata": {"source_id": "doc2", "page": 3},
        },
    ]


class TestRagService:
    """Unit tests for RagService."""

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_success(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test successful context retrieval without filtering."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding

        # Mock should respect the k parameter and return only k results
        def mock_search(*_args, **kwargs):
            k = kwargs.get("k", 5)
            return sample_search_results[:k]

        mock_vector_store_client.search.side_effect = mock_search

        # Execute
        query = "What is machine learning?"
        result = await rag_service.retrieve_relevant_context(query, k=3)

        # Verify - first 3 results, where index 3 has 'content' instead of 'text'
        assert len(result) == 3
        assert result[0] == "This is the first relevant document about machine learning."
        assert result[1] == "Second document discusses artificial intelligence concepts."
        assert result[2] == "Third document covers deep learning fundamentals."

        # Verify service calls
        mock_embedding_service.generate_embedding.assert_called_once_with(query)
        mock_vector_store_client.search.assert_called_once_with(embedding=sample_embedding, k=3)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_source_filtering(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test context retrieval with source ID filtering."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding

        # Mock should respect the k parameter and return only k results
        def mock_search(*_args, **kwargs):
            k = kwargs.get("k", 5)
            return sample_search_results[:k]

        mock_vector_store_client.search.side_effect = mock_search

        # Execute with source filtering
        query = "What is AI?"
        source_ids = ["doc1", "doc3"]
        result = await rag_service.retrieve_relevant_context(query, source_ids=source_ids, k=5)

        # Verify - all 5 results (4 with 'text' field + 1 with 'content' field)
        assert len(result) == 5

        # Verify search was called with filter
        mock_vector_store_client.search.assert_called_once_with(
            embedding=sample_embedding, k=5, filter={"source_id": {"$in": source_ids}}
        )

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_empty_query(self, rag_service: RagService):
        """Test error handling for empty query."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await rag_service.retrieve_relevant_context("")

        with pytest.raises(ValueError, match="Query cannot be empty"):
            await rag_service.retrieve_relevant_context("   ")

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_invalid_k(self, rag_service: RagService):
        """Test error handling for invalid k parameter."""
        with pytest.raises(ValueError, match="k must be a positive integer"):
            await rag_service.retrieve_relevant_context("test query", k=0)

        with pytest.raises(ValueError, match="k must be a positive integer"):
            await rag_service.retrieve_relevant_context("test query", k=-1)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_embedding_service_failure(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
    ):
        """Test error handling when embedding service fails."""
        # Setup embedding service to fail
        mock_embedding_service.generate_embedding.side_effect = Exception("Embedding generation failed")

        # Execute and verify exception
        with pytest.raises(Exception, match="Context retrieval failed"):
            await rag_service.retrieve_relevant_context("test query")

        # Verify vector store was not called
        mock_vector_store_client.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_vector_store_failure(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
    ):
        """Test error handling when vector store search fails."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.side_effect = Exception("Vector search failed")

        # Execute and verify exception
        with pytest.raises(Exception, match="Context retrieval failed"):
            await rag_service.retrieve_relevant_context("test query")

        # Verify embedding service was called
        mock_embedding_service.generate_embedding.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_empty_results(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
    ):
        """Test handling of empty search results."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.return_value = []

        # Execute
        result = await rag_service.retrieve_relevant_context("test query")

        # Verify
        assert result == []

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_empty_source_ids(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test that empty source_ids list doesn't add filter."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding

        # Mock should respect the k parameter and return only k results
        def mock_search(*_args, **kwargs):
            k = kwargs.get("k", 5)
            return sample_search_results[:k]

        mock_vector_store_client.search.side_effect = mock_search

        # Execute with empty source_ids
        result = await rag_service.retrieve_relevant_context("test query", source_ids=[], k=3)

        # Verify - first 3 results
        assert len(result) == 3

        # Verify no filter was applied
        mock_vector_store_client.search.assert_called_once_with(embedding=sample_embedding, k=3)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_scores_success(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test successful context retrieval with scores."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding

        # Mock should respect the k parameter and return only k results
        def mock_search(*_args, **kwargs):
            k = kwargs.get("k", 5)
            return sample_search_results[:k]

        mock_vector_store_client.search.side_effect = mock_search

        # Execute
        result = await rag_service.retrieve_relevant_context_with_scores("test query", k=3)

        # Verify - first 3 results
        assert len(result) == 3
        assert all("text" in item and "score" in item and "metadata" in item for item in result)
        assert result[0]["text"] == "This is the first relevant document about machine learning."
        assert result[0]["score"] == 0.95
        assert result[2]["text"] == "Third document covers deep learning fundamentals."
        assert result[2]["score"] == 0.82

        # Verify search was called with include_scores
        mock_vector_store_client.search.assert_called_once_with(embedding=sample_embedding, k=3, include_scores=True)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_scores_min_threshold(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test context retrieval with minimum score threshold."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.return_value = sample_search_results

        # Execute with high threshold
        result = await rag_service.retrieve_relevant_context_with_scores("test query", k=5, min_score=0.85)

        # Verify only high-scoring results are returned
        assert len(result) == 2  # Only scores >= 0.85
        assert result[0]["score"] == 0.95
        assert result[1]["score"] == 0.87

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_scores_invalid_min_score(self, rag_service: RagService):
        """Test error handling for invalid min_score parameter."""
        with pytest.raises(ValueError, match="min_score must be between 0.0 and 1.0"):
            await rag_service.retrieve_relevant_context_with_scores("test", min_score=-0.1)

        with pytest.raises(ValueError, match="min_score must be between 0.0 and 1.0"):
            await rag_service.retrieve_relevant_context_with_scores("test", min_score=1.1)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_scores_and_filtering(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
        sample_search_results: list[dict[str, Any]],
    ):
        """Test context retrieval with scores and source filtering."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.return_value = sample_search_results

        # Execute with both filtering and score threshold
        source_ids = ["doc1", "doc2"]
        await rag_service.retrieve_relevant_context_with_scores("test query", source_ids=source_ids, k=5, min_score=0.8)

        # Verify filtering was applied
        mock_vector_store_client.search.assert_called_once_with(
            embedding=sample_embedding,
            k=5,
            include_scores=True,
            filter={"source_id": {"$in": source_ids}},
        )

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_malformed_results(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
    ):
        """Test handling of malformed search results."""
        # Setup mocks with malformed results
        malformed_results = [
            {"text": "Good result", "score": 0.9},
            {"score": 0.8},  # Missing text/content
            {"metadata": {"source": "doc1"}},  # Missing text/content and score
            {"content": "Another good result", "score": 0.7},
        ]

        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.return_value = malformed_results

        # Execute
        result = await rag_service.retrieve_relevant_context("test query")

        # Verify only valid results are returned
        assert len(result) == 2
        assert result[0] == "Good result"
        assert result[1] == "Another good result"

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context_with_scores_malformed_results(
        self,
        rag_service: RagService,
        mock_embedding_service: Mock,
        mock_vector_store_client: Mock,
        sample_embedding: list[float],
    ):
        """Test handling of malformed results in scores method."""
        # Setup mocks with malformed results
        malformed_results = [
            {"text": "Good result", "score": 0.9, "metadata": {"source": "doc1"}},
            {"score": 0.8, "metadata": {"source": "doc2"}},  # Missing text
            {"text": "", "score": 0.7, "metadata": {"source": "doc3"}},  # Empty text
            {"content": "Content result", "score": 0.6, "metadata": {"source": "doc4"}},
        ]

        mock_embedding_service.generate_embedding.return_value = sample_embedding
        mock_vector_store_client.search.return_value = malformed_results

        # Execute
        result = await rag_service.retrieve_relevant_context_with_scores("test query")

        # Verify only valid results are returned
        assert len(result) == 2
        assert result[0]["text"] == "Good result"
        assert result[0]["score"] == 0.9
        assert result[1]["text"] == "Content result"
        assert result[1]["score"] == 0.6

    @pytest.mark.asyncio
    async def test_initialization(self, mock_embedding_service, mock_vector_store_client):
        """Test RagService initialization."""
        service = RagService(mock_embedding_service, mock_vector_store_client)

        assert service.embedding_service == mock_embedding_service
        assert service.vector_store_client == mock_vector_store_client
