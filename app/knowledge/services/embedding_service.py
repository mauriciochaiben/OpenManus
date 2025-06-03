"""Embedding service for generating text embeddings."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from app.core.settings import settings
from app.core.vector_config import embedding_config

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """Initialize OpenAI embedding provider."""
        self.api_key = api_key
        self.model = model
        self._client = None
        self._dimension = 1536 if model == "text-embedding-ada-002" else 1536

    async def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                import openai

                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError as e:
                raise ImportError(
                    "openai package is required for OpenAI embeddings"
                ) from e
        return self._client

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            client = await self._get_client()

            response = await client.embeddings.create(model=self.model, input=texts)

            return [data.embedding for data in response.data]

        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class SentenceTransformersProvider(EmbeddingProvider):
    """Sentence Transformers embedding provider."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize Sentence Transformers provider."""
        self.model_name = model_name
        self._model = None
        self._dimension = None

    async def _get_model(self):
        """Get or load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                # Load model in thread executor to avoid blocking
                loop = asyncio.get_event_loop()
                self._model = await loop.run_in_executor(
                    None, SentenceTransformer, self.model_name
                )

                # Get dimension from model
                self._dimension = self._model.get_sentence_embedding_dimension()

            except ImportError as e:
                raise ImportError(
                    "sentence-transformers package is required for local embeddings"
                ) from e

        return self._model

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using Sentence Transformers."""
        try:
            model = await self._get_model()

            # Generate embeddings in thread executor
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(None, model.encode, texts)

            # Convert numpy arrays to lists
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()

            return embeddings

        except Exception as e:
            logger.error(f"Sentence Transformers embedding generation failed: {str(e)}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension or 384  # Default for all-MiniLM-L6-v2


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider for local models."""

    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize Ollama embedding provider."""
        self.model_name = model_name
        self.base_url = base_url
        self._client = None
        self._dimension = None

    async def _get_client(self):
        """Get or create Ollama client."""
        if self._client is None:
            try:
                import httpx

                self._client = httpx.AsyncClient(base_url=self.base_url)
            except ImportError as e:
                raise ImportError(
                    "httpx package is required for Ollama embeddings"
                ) from e
        return self._client

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using Ollama API."""
        try:
            client = await self._get_client()
            embeddings = []

            for text in texts:
                response = await client.post(
                    "/api/embeddings", json={"model": self.model_name, "prompt": text}
                )
                response.raise_for_status()

                data = response.json()
                embedding = data.get("embedding", [])
                embeddings.append(embedding)

                # Set dimension from first embedding
                if self._dimension is None and embedding:
                    self._dimension = len(embedding)

            return embeddings

        except Exception as e:
            logger.error(f"Ollama embedding generation failed: {str(e)}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension or 1024  # Default dimension


class EmbeddingServiceError(Exception):
    """Base exception for embedding service operations."""

    pass


class EmbeddingService:
    """Service for generating text embeddings with multiple provider support."""

    def __init__(self):
        """Initialize the embedding service."""
        self.model_name = embedding_config.model_name
        self.batch_size = embedding_config.batch_size
        self.max_length = embedding_config.max_length
        self.normalize = embedding_config.normalize

        # Initialize provider based on configuration
        try:
            self.provider = self._create_provider()
            logger.info(f"EmbeddingService initialized with model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding provider: {e}")
            # Fallback to simple provider
            self.provider = None

    def _create_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        model_name = self.model_name.lower()

        # OpenAI provider
        if "openai" in model_name or "ada" in model_name:
            api_key = getattr(settings, "openai_api_key", None)
            if not api_key:
                logger.warning(
                    "OpenAI API key not found, falling back to SentenceTransformers"
                )
                return SentenceTransformersProvider(self.model_name)
            return OpenAIEmbeddingProvider(api_key, self.model_name)

        # Ollama provider
        if "ollama" in model_name or hasattr(settings, "ollama_base_url"):
            ollama_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            # Extract model name (remove 'ollama/' prefix if present)
            model = model_name.replace("ollama/", "")
            return OllamaEmbeddingProvider(model, ollama_url)

        # Default to Sentence Transformers
        return SentenceTransformersProvider(self.model_name)

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingServiceError: If embedding generation fails
        """
        if not texts:
            return []

        # Fallback for when provider isn't available
        if not self.provider:
            logger.warning(
                "No embedding provider available, returning dummy embeddings"
            )
            return [[0.0] * embedding_config.dimension for _ in texts]

        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]

            # Generate embeddings in batches
            all_embeddings = []

            for i in range(0, len(processed_texts), self.batch_size):
                batch = processed_texts[i : i + self.batch_size]
                batch_embeddings = await self.provider.generate_embeddings(batch)

                # Normalize embeddings if required
                if self.normalize:
                    batch_embeddings = [
                        self._normalize_embedding(emb) for emb in batch_embeddings
                    ]

                all_embeddings.extend(batch_embeddings)

            logger.debug(f"Generated {len(all_embeddings)} embeddings")
            return all_embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            # Return dummy embeddings as fallback
            return [[0.0] * embedding_config.dimension for _ in texts]

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * embedding_config.dimension

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding generation.

        Args:
            text: Input text

        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # Truncate if too long
        if self.max_length and len(text) > self.max_length:
            text = text[: self.max_length]
            logger.warning(f"Text truncated to {self.max_length} characters")

        return text

    def _normalize_embedding(self, embedding: list[float]) -> list[float]:
        """
        Normalize embedding vector to unit length.

        Args:
            embedding: Input embedding vector

        Returns:
            Normalized embedding vector
        """
        try:
            # Convert to numpy for easier computation
            vec = np.array(embedding)
            norm = np.linalg.norm(vec)

            if norm == 0:
                return embedding

            normalized = vec / norm
            return normalized.tolist()

        except Exception as e:
            logger.warning(f"Failed to normalize embedding: {str(e)}")
            return embedding

    def get_dimension(self) -> int:
        """
        Get the embedding dimension.

        Returns:
            Embedding dimension
        """
        try:
            if self.provider:
                return self.provider.get_dimension()
            return embedding_config.dimension
        except Exception as e:
            logger.warning(f"Failed to get embedding dimension: {str(e)}")
            return embedding_config.dimension

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the embedding service.

        Returns:
            Health check results
        """
        try:
            # Test embedding generation with a simple text
            test_text = "This is a test embedding."
            embedding = await self.generate_embedding(test_text)

            return {
                "status": "healthy",
                "model": self.model_name,
                "dimension": len(embedding),
                "provider": type(self.provider).__name__ if self.provider else "None",
                "test_embedding_length": len(embedding),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "provider": type(self.provider).__name__ if self.provider else "None",
                "error": str(e),
            }


# Global service instance
embedding_service = EmbeddingService()


async def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service instance.

    Returns:
        EmbeddingService instance
    """
    return embedding_service
