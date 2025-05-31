"""
RAG (Retrieval-Augmented Generation) Service

This service provides functionality to retrieve relevant context from a knowledge base
using semantic similarity search with embeddings.
"""

import logging
from typing import List, Optional

from app.knowledge.infrastructure.vector_store_client import VectorStoreClient
from app.knowledge.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RagService:
    """
    Service for Retrieval-Augmented Generation operations.

    This service combines embedding generation with vector similarity search
    to retrieve relevant context from the knowledge base.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store_client: VectorStoreClient,
    ):
        """
        Initialize the RAG service with required dependencies.

        Args:
            embedding_service: Service for generating embeddings
            vector_store_client: Client for vector database operations
        """
        self.embedding_service = embedding_service
        self.vector_store_client = vector_store_client

    async def retrieve_relevant_context(
        self, query: str, source_ids: Optional[List[str]] = None, k: int = 5
    ) -> List[str]:
        """
        Retrieve relevant context chunks for a given query.

        This method generates an embedding for the query and performs similarity
        search in the vector store to find the most relevant text chunks.

        Args:
            query: The search query text
            source_ids: Optional list of source IDs to filter results by
            k: Number of top similar chunks to retrieve (default: 5)

        Returns:
            List of relevant text chunks ordered by similarity score

        Raises:
            ValueError: If query is empty or k is not positive
            Exception: If embedding generation or vector search fails
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if k <= 0:
            raise ValueError("k must be a positive integer")

        logger.info(f"Retrieving relevant context for query: '{query[:100]}...'")

        try:
            # Generate embedding for the query
            logger.debug("Generating embedding for query")
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Prepare search parameters
            search_params = {"embedding": query_embedding, "k": k}

            # Add source filtering if provided
            if source_ids is not None and len(source_ids) > 0:
                search_params["filter"] = {"source_id": {"$in": source_ids}}
                logger.debug(f"Filtering by source IDs: {source_ids}")

            # Perform similarity search
            logger.debug(f"Searching for {k} most similar chunks")
            search_results = await self.vector_store_client.search(**search_params)

            # Extract text content from search results
            context_chunks = []
            for result in search_results:
                if "text" in result:
                    context_chunks.append(result["text"])
                elif "content" in result:
                    context_chunks.append(result["content"])
                else:
                    logger.warning(f"Search result missing text content: {result}")

            logger.info(f"Retrieved {len(context_chunks)} relevant context chunks")
            return context_chunks

        except Exception as e:
            logger.error(f"Failed to retrieve relevant context: {str(e)}")
            raise Exception(f"Context retrieval failed: {str(e)}") from e

    async def retrieve_relevant_context_with_scores(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        k: int = 5,
        min_score: float = 0.0,
    ) -> List[dict]:
        """
        Retrieve relevant context chunks with similarity scores.

        Similar to retrieve_relevant_context but also returns similarity scores
        and allows filtering by minimum score threshold.

        Args:
            query: The search query text
            source_ids: Optional list of source IDs to filter results by
            k: Number of top similar chunks to retrieve (default: 5)
            min_score: Minimum similarity score threshold (default: 0.0)

        Returns:
            List of dictionaries containing 'text' and 'score' keys

        Raises:
            ValueError: If query is empty, k is not positive, or min_score is invalid
            Exception: If embedding generation or vector search fails
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if k <= 0:
            raise ValueError("k must be a positive integer")

        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score must be between 0.0 and 1.0")

        logger.info(f"Retrieving context with scores for query: '{query[:100]}...'")

        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Prepare search parameters
            search_params = {
                "embedding": query_embedding,
                "k": k,
                "include_scores": True,
            }

            # Add source filtering if provided
            if source_ids is not None and len(source_ids) > 0:
                search_params["filter"] = {"source_id": {"$in": source_ids}}

            # Perform similarity search
            search_results = await self.vector_store_client.search(**search_params)

            # Extract text content and scores, applying score filter
            context_with_scores = []
            for result in search_results:
                score = result.get("score", 0.0)
                if score >= min_score:
                    text = result.get("text") or result.get("content", "")
                    if text:
                        context_with_scores.append(
                            {
                                "text": text,
                                "score": score,
                                "metadata": result.get("metadata", {}),
                            }
                        )

            logger.info(
                f"Retrieved {len(context_with_scores)} context chunks with scores >= {min_score}"
            )
            return context_with_scores

        except Exception as e:
            logger.error(f"Failed to retrieve context with scores: {str(e)}")
            raise Exception(f"Context retrieval with scores failed: {str(e)}") from e
