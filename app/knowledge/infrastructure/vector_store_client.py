"""Vector Store Client for ChromaDB integration."""

import asyncio
import logging
from typing import Any
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from chromadb.errors import ChromaError, NotFoundError

from app.core.vector_config import rag_config, vector_db_config

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Base exception for vector store operations."""

    pass


class ConnectionError(VectorStoreError):
    """Raised when connection to vector store fails."""

    pass


class CollectionError(VectorStoreError):
    """Raised when collection operations fail."""

    pass


class VectorStoreClient:
    """ChromaDB Vector Store Client with async support."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        auth_token: str | None = None,
    ):
        """
        Initialize the Vector Store Client.

        Args:
            host: ChromaDB host (defaults to config)
            port: ChromaDB port (defaults to config)
            auth_token: Authentication token (defaults to config)

        """
        self.host = host or vector_db_config.host
        self.port = port or vector_db_config.port
        self.auth_token = auth_token or vector_db_config.auth_token

        self._client: chromadb.Client | None = None
        self._collections_cache: dict[str, Collection] = {}
        self._is_connected = False

        logger.info(f"Initializing VectorStoreClient for {self.host}:{self.port}")

    async def connect(self) -> None:
        """Connect to ChromaDB server."""
        try:
            # Prepare client settings
            client_settings = Settings(
                chroma_server_host=self.host,
                chroma_server_http_port=str(self.port),
                chroma_server_cors_allow_origins=["*"],
            )

            # Prepare headers for authentication
            headers = {}
            if self.auth_token:
                headers[vector_db_config.auth_header] = self.auth_token

            # Create ChromaDB client
            if headers:
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    headers=headers,
                    settings=client_settings,
                )
            else:
                self._client = chromadb.HttpClient(host=self.host, port=self.port, settings=client_settings)

            # Test connection
            await self._test_connection()
            self._is_connected = True

            logger.info(f"Successfully connected to ChromaDB at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e!s}")
            raise ConnectionError(f"Failed to connect to vector store: {e!s}") from e

    async def _test_connection(self) -> None:
        """Test the connection to ChromaDB."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._client.heartbeat)
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e!s}") from e

    async def disconnect(self) -> None:
        """Disconnect from ChromaDB."""
        self._client = None
        self._collections_cache.clear()
        self._is_connected = False
        logger.info("Disconnected from ChromaDB")

    def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if not self._is_connected or not self._client:
            raise ConnectionError("Not connected to vector store. Call connect() first.")

    async def create_collection(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
        embedding_function: Any | None = None,
    ) -> Collection:
        """
        Create a collection if it doesn't exist.

        Args:
            name: Collection name
            metadata: Collection metadata
            embedding_function: Custom embedding function

        Returns:
            Collection object

        """
        self._ensure_connected()

        try:
            loop = asyncio.get_event_loop()

            # Check if collection exists
            try:
                collection = await loop.run_in_executor(None, self._client.get_collection, name)
                logger.info(f"Collection '{name}' already exists")
                self._collections_cache[name] = collection
                return collection

            except (NotFoundError, ChromaError):
                # Collection doesn't exist, create it
                collection_metadata = metadata or vector_db_config.get_collection_metadata("documents")

                collection = await loop.run_in_executor(
                    None,
                    lambda: self._client.create_collection(
                        name=name,
                        metadata=collection_metadata,
                        embedding_function=embedding_function,
                    ),
                )

                logger.info(f"Created collection '{name}' with metadata: {collection_metadata}")
                self._collections_cache[name] = collection
                return collection

        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e!s}")
            raise CollectionError(f"Failed to create collection: {e!s}") from e

    async def get_collection(self, name: str) -> Collection:
        """
        Get an existing collection.

        Args:
            name: Collection name

        Returns:
            Collection object

        """
        self._ensure_connected()

        if name in self._collections_cache:
            return self._collections_cache[name]

        try:
            loop = asyncio.get_event_loop()
            collection = await loop.run_in_executor(None, self._client.get_collection, name)
            self._collections_cache[name] = collection
            return collection

        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {e!s}")
            raise CollectionError(f"Collection '{name}' not found: {e!s}") from e

    async def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        embeddings: list[list[float]] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        Add documents to a collection.

        Args:
            collection_name: Target collection name
            documents: List of document texts
            embeddings: Pre-computed embeddings (optional)
            metadatas: Document metadata (optional)
            ids: Document IDs (optional, will generate if not provided)

        Returns:
            List of document IDs

        """
        self._ensure_connected()

        if not documents:
            raise ValueError("Documents list cannot be empty")

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid4()) for _ in documents]

        if len(ids) != len(documents):
            raise ValueError("Number of IDs must match number of documents")

        # Prepare metadata
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in documents]
        elif len(metadatas) != len(documents):
            raise ValueError("Number of metadata entries must match number of documents")

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()

            # Add documents to collection
            if embeddings:
                await loop.run_in_executor(
                    None,
                    lambda: collection.add(
                        documents=documents,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids,
                    ),
                )
            else:
                # Let ChromaDB compute embeddings
                await loop.run_in_executor(
                    None,
                    lambda: collection.add(documents=documents, metadatas=metadatas, ids=ids),
                )

            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return ids

        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {e!s}")
            raise VectorStoreError(f"Failed to add documents: {e!s}") from e

    async def search_similar(
        self,
        collection_name: str,
        query_texts: list[str] | None = None,
        query_embeddings: list[list[float]] | None = None,
        n_results: int | None = None,
        where: dict[str, Any] | None = None,
        where_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Search for similar documents in a collection.

        Args:
            collection_name: Collection to search in
            query_texts: Query texts (alternative to embeddings)
            query_embeddings: Query embeddings (alternative to texts)
            n_results: Number of results to return
            where: Metadata filter
            where_document: Document content filter

        Returns:
            Search results with documents, distances, and metadata

        """
        self._ensure_connected()

        if not query_texts and not query_embeddings:
            raise ValueError("Either query_texts or query_embeddings must be provided")

        n_results = n_results or rag_config.search_k

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()

            # Perform similarity search
            if query_embeddings:
                results = await loop.run_in_executor(
                    None,
                    lambda: collection.query(
                        query_embeddings=query_embeddings,
                        n_results=n_results,
                        where=where,
                        where_document=where_document,
                    ),
                )
            else:
                results = await loop.run_in_executor(
                    None,
                    lambda: collection.query(
                        query_texts=query_texts,
                        n_results=n_results,
                        where=where,
                        where_document=where_document,
                    ),
                )

            # Filter results by threshold if configured
            if rag_config.search_threshold > 0:
                results = self._filter_by_threshold(results, rag_config.search_threshold)

            logger.info(f"Found {len(results.get('documents', [[]])[0])} similar documents in '{collection_name}'")
            return results

        except Exception as e:
            logger.error(f"Search failed in '{collection_name}': {e!s}")
            raise VectorStoreError(f"Search failed: {e!s}") from e

    def _filter_by_threshold(self, results: dict[str, Any], threshold: float) -> dict[str, Any]:
        """Filter search results by distance threshold."""
        if "distances" not in results or not results["distances"]:
            return results

        filtered_results = {
            "ids": [],
            "documents": [],
            "metadatas": [],
            "distances": [],
        }

        for i, distances in enumerate(results["distances"]):
            filtered_indices = [j for j, dist in enumerate(distances) if dist <= threshold]

            if filtered_indices:
                filtered_results["ids"].append([results["ids"][i][j] for j in filtered_indices])
                filtered_results["documents"].append([results["documents"][i][j] for j in filtered_indices])
                filtered_results["metadatas"].append([results["metadatas"][i][j] for j in filtered_indices])
                filtered_results["distances"].append([distances[j] for j in filtered_indices])
            else:
                # Keep empty lists for consistency
                filtered_results["ids"].append([])
                filtered_results["documents"].append([])
                filtered_results["metadatas"].append([])
                filtered_results["distances"].append([])

        return filtered_results

    async def update_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str] | None = None,
        embeddings: list[list[float]] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Update existing documents in a collection.

        Args:
            collection_name: Target collection name
            ids: Document IDs to update
            documents: New document texts
            embeddings: New embeddings
            metadatas: New metadata

        """
        self._ensure_connected()

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None,
                lambda: collection.update(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                ),
            )

            logger.info(f"Updated {len(ids)} documents in collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Failed to update documents in '{collection_name}': {e!s}")
            raise VectorStoreError(f"Failed to update documents: {e!s}") from e

    async def delete_documents(
        self,
        collection_name: str,
        ids: list[str] | None = None,
        where: dict[str, Any] | None = None,
    ) -> None:
        """
        Delete documents from a collection.

        Args:
            collection_name: Target collection name
            ids: Document IDs to delete
            where: Metadata filter for deletion

        """
        self._ensure_connected()

        if not ids and not where:
            raise ValueError("Either ids or where filter must be provided")

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()

            await loop.run_in_executor(None, lambda: collection.delete(ids=ids, where=where))

            logger.info(f"Deleted documents from collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Failed to delete documents from '{collection_name}': {e!s}")
            raise VectorStoreError(f"Failed to delete documents: {e!s}") from e

    async def get_collection_info(self, collection_name: str) -> dict[str, Any]:
        """
        Get information about a collection.

        Args:
            collection_name: Collection name

        Returns:
            Collection information including count and metadata

        """
        self._ensure_connected()

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()

            count = await loop.run_in_executor(None, collection.count)

            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata,
            }

        except Exception as e:
            logger.error(f"Failed to get info for collection '{collection_name}': {e!s}")
            raise CollectionError(f"Failed to get collection info: {e!s}") from e

    async def list_collections(self) -> list[str]:
        """
        List all collections.

        Returns:
            List of collection names

        """
        self._ensure_connected()

        try:
            loop = asyncio.get_event_loop()
            collections = await loop.run_in_executor(None, self._client.list_collections)
            return [col.name for col in collections]

        except Exception as e:
            logger.error(f"Failed to list collections: {e!s}")
            raise VectorStoreError(f"Failed to list collections: {e!s}") from e

    async def reset_collection(self, collection_name: str) -> None:
        """
        Reset (clear) a collection.

        Args:
            collection_name: Collection to reset

        """
        self._ensure_connected()

        try:
            collection = await self.get_collection(collection_name)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, collection.delete)

            # Remove from cache
            if collection_name in self._collections_cache:
                del self._collections_cache[collection_name]

            logger.info(f"Reset collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Failed to reset collection '{collection_name}': {e!s}")
            raise CollectionError(f"Failed to reset collection: {e!s}") from e

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected


# Global vector store client instance
vector_store_client = VectorStoreClient()


async def get_vector_store() -> VectorStoreClient:
    """
    Get the global vector store client instance.

    Ensures connection is established.
    """
    if not vector_store_client.is_connected:
        await vector_store_client.connect()
    return vector_store_client
