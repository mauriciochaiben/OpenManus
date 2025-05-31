"""Embedding service for generating text embeddings."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import numpy as np

from app.core.config import settings
from app.core.vector_config import embedding_config

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
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
            except ImportError:
                raise ImportError("openai package is required for OpenAI embeddings")
        return self._client

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            client = await self._get_client()

            response = await client.embeddings.create(model=self.model, input=texts)

            embeddings = [data.embedding for data in response.data]
            return embeddings

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

            except ImportError:
                raise ImportError(
                    "sentence-transformers package is required for local embeddings"
                )

        return self._model

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
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
            except ImportError:
                raise ImportError("httpx package is required for Ollama embeddings")
        return self._client

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
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
        self.provider = self._create_provider()

        logger.info(f"EmbeddingService initialized with model: {self.model_name}")

    def _create_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        model_name = self.model_name.lower()

        # OpenAI provider
        if "openai" in model_name or "ada" in model_name:
            api_key = getattr(settings, "openai_api_key", None)
            if not api_key:
                raise EmbeddingServiceError(
                    "OpenAI API key is required for OpenAI embeddings"
                )
            return OpenAIEmbeddingProvider(api_key, self.model_name)

        # Ollama provider
        elif "ollama" in model_name or hasattr(settings, "ollama_base_url"):
            ollama_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            # Extract model name (remove 'ollama/' prefix if present)
            model = model_name.replace("ollama/", "")
            return OllamaEmbeddingProvider(model, ollama_url)

        # Default to Sentence Transformers
        else:
            return SentenceTransformersProvider(self.model_name)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
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
            raise EmbeddingServiceError(f"Failed to generate embeddings: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

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

    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
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
            return self.provider.get_dimension()
        except Exception as e:
            logger.warning(f"Failed to get embedding dimension: {str(e)}")
            return embedding_config.dimension

    async def health_check(self) -> Dict[str, Any]:
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
                "provider": type(self.provider).__name__,
                "test_embedding_length": len(embedding),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "provider": type(self.provider).__name__,
                "error": str(e),
            }

    async def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score between 0 and 1
        """
        try:
            embeddings = await self.generate_embeddings([text1, text2])

            if len(embeddings) != 2:
                raise EmbeddingServiceError(
                    "Failed to generate embeddings for similarity calculation"
                )

            # Calculate cosine similarity
            vec1 = np.array(embeddings[0])
            vec2 = np.array(embeddings[1])

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, (similarity + 1) / 2))

        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            raise EmbeddingServiceError(f"Failed to calculate similarity: {str(e)}")


# Global service instance
embedding_service = EmbeddingService()


async def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service instance.

    Returns:
        EmbeddingService instance
    """
    return embedding_service
