import logging
import mimetypes
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai

from app.core.text_processing import TextProcessor
from app.knowledge.infrastructure.vector_store_client import VectorStoreClient
from app.knowledge.models.note import (
    KnowledgeSource,
    ProcessingResult,
    ProcessingStatus,
)
from app.knowledge.services.embedding_service import EmbeddingService

# Knowledge feature services exports
# This file will export all knowledge-related service classes and functions

logger = logging.getLogger(__name__)


class SourceService:
    # ...existing code...

    # Add supported audio formats
    SUPPORTED_AUDIO_FORMATS = {
        "audio/mpeg",  # mp3
        "audio/wav",  # wav
        "audio/x-wav",  # wav alternative
        "audio/mp4",  # m4a
        "audio/aac",  # aac
        "audio/ogg",  # ogg
        "audio/flac",  # flac
        "audio/webm",  # webm
    }

    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".webm"}

    def __init__(
        self,
        text_processor: TextProcessor,
        embedding_service: EmbeddingService,
        vector_store_client: VectorStoreClient,
        openai_api_key: Optional[str] = None,
    ):
        # ...existing code...
        self.openai_client = None
        if openai_api_key:
            openai.api_key = openai_api_key
            self.openai_client = openai

    def _is_audio_file(self, file_path: str, content_type: str) -> bool:
        """
        Check if the file is an audio file based on MIME type and extension.

        Args:
            file_path: Path to the file
            content_type: MIME type of the file

        Returns:
            True if the file is an audio file
        """
        # Check MIME type
        if content_type in self.SUPPORTED_AUDIO_FORMATS:
            return True

        # Check file extension as fallback
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.AUDIO_EXTENSIONS

    async def _transcribe_audio_file(self, file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper API.

        Args:
            file_path: Path to the audio file

        Returns:
            Transcribed text content

        Raises:
            Exception: If transcription fails
        """
        if not self.openai_client:
            raise Exception(
                "OpenAI client not configured. Please provide openai_api_key."
            )

        try:
            logger.info(f"Starting transcription for audio file: {file_path}")

            # Check file size (OpenAI has a 25MB limit)
            file_size = os.path.getsize(file_path)
            max_size = 25 * 1024 * 1024  # 25MB

            if file_size > max_size:
                logger.warning(
                    f"Audio file too large ({file_size} bytes), attempting to split"
                )
                return await self._transcribe_large_audio_file(file_path)

            # Transcribe using OpenAI Whisper
            with open(file_path, "rb") as audio_file:
                transcript = await self.openai_client.Audio.atranscribe(
                    model="whisper-1", file=audio_file, response_format="text"
                )

            logger.info(
                f"Successfully transcribed audio file. Text length: {len(transcript)} characters"
            )
            return transcript

        except Exception as e:
            logger.error(f"Error transcribing audio file {file_path}: {str(e)}")
            raise Exception(f"Audio transcription failed: {str(e)}")

    async def _transcribe_large_audio_file(self, file_path: str) -> str:
        """
        Handle transcription of large audio files by splitting them.

        Args:
            file_path: Path to the large audio file

        Returns:
            Combined transcribed text
        """
        try:
            # This is a simplified approach - in production you might want to use
            # ffmpeg or similar tools to split audio files properly
            logger.warning("Large audio file transcription not fully implemented")

            # For now, attempt direct transcription and let OpenAI handle it
            with open(file_path, "rb") as audio_file:
                transcript = await self.openai_client.Audio.atranscribe(
                    model="whisper-1", file=audio_file, response_format="text"
                )

            return transcript

        except Exception as e:
            logger.error(f"Error transcribing large audio file: {str(e)}")
            raise Exception(f"Large audio file transcription failed: {str(e)}")

    async def _process_audio_source(
        self, source: KnowledgeSource, file_path: str
    ) -> ProcessingResult:
        """
        Process an audio source by transcribing it to text.

        Args:
            source: The knowledge source being processed
            file_path: Path to the audio file

        Returns:
            Processing result with transcription and chunks
        """
        try:
            logger.info(f"Processing audio source: {source.filename}")

            # Update status to processing
            await self._update_source_status(
                source.id,
                ProcessingStatus(
                    status="processing", progress=10, last_updated=datetime.utcnow()
                ),
            )

            # Transcribe audio to text
            logger.info("Transcribing audio content...")
            transcribed_text = await self._transcribe_audio_file(file_path)

            if not transcribed_text.strip():
                raise Exception("Transcription resulted in empty text")

            # Update progress
            await self._update_source_status(
                source.id,
                ProcessingStatus(
                    status="processing", progress=50, last_updated=datetime.utcnow()
                ),
            )

            # Create a temporary text file for processing
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as temp_file:
                temp_file.write(transcribed_text)
                temp_text_path = temp_file.name

            try:
                # Process the transcribed text using existing text processing pipeline
                logger.info("Processing transcribed text into chunks...")

                # Split into chunks
                chunks = await self.text_processor.split_text(
                    text=transcribed_text,
                    chunk_size=1000,
                    chunk_overlap=200,
                    source_metadata={
                        "source_id": source.id,
                        "filename": source.filename,
                        "file_type": "audio_transcription",
                        "original_audio_type": source.file_type,
                        "transcription_method": "openai_whisper",
                    },
                )

                # Update progress
                await self._update_source_status(
                    source.id,
                    ProcessingStatus(
                        status="processing",
                        progress=70,
                        processed_chunks=len(chunks),
                        total_chunks=len(chunks),
                        last_updated=datetime.utcnow(),
                    ),
                )

                # Generate embeddings and store
                logger.info(f"Generating embeddings for {len(chunks)} text chunks...")
                stored_chunks = []

                for i, chunk in enumerate(chunks):
                    try:
                        # Generate embedding
                        embedding = await self.embedding_service.generate_embedding(
                            chunk.content
                        )

                        # Store in vector database
                        chunk_id = await self.vector_store_client.store_chunk(
                            chunk_id=chunk.id,
                            content=chunk.content,
                            embedding=embedding,
                            metadata={
                                **chunk.metadata,
                                "chunk_index": i,
                                "transcribed_from_audio": True,
                            },
                        )

                        stored_chunks.append(chunk_id)

                        # Update progress
                        progress = 70 + (i + 1) / len(chunks) * 25
                        await self._update_source_status(
                            source.id,
                            ProcessingStatus(
                                status="processing",
                                progress=int(progress),
                                processed_chunks=i + 1,
                                total_chunks=len(chunks),
                                last_updated=datetime.utcnow(),
                            ),
                        )

                    except Exception as e:
                        logger.error(f"Error processing chunk {i}: {str(e)}")
                        continue

                # Final status update
                await self._update_source_status(
                    source.id,
                    ProcessingStatus(
                        status="completed",
                        progress=100,
                        processed_chunks=len(stored_chunks),
                        total_chunks=len(chunks),
                        last_updated=datetime.utcnow(),
                    ),
                )

                return ProcessingResult(
                    success=True,
                    chunks_processed=len(stored_chunks),
                    total_chunks=len(chunks),
                    processing_time=(
                        datetime.utcnow() - source.upload_date
                    ).total_seconds(),
                    metadata={
                        "transcription_length": len(transcribed_text),
                        "transcription_method": "openai_whisper",
                        "original_audio_duration": "unknown",  # Could be extracted with audio analysis
                        "chunks_stored": len(stored_chunks),
                    },
                )

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_text_path)
                except Exception as e:
                    logger.warning(
                        f"Could not delete temporary file {temp_text_path}: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Error processing audio source {source.id}: {str(e)}")

            # Update status to failed
            await self._update_source_status(
                source.id,
                ProcessingStatus(
                    status="failed",
                    error_message=str(e),
                    last_updated=datetime.utcnow(),
                ),
            )

            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=(
                    datetime.utcnow() - source.upload_date
                ).total_seconds(),
            )

    async def _process_source(
        self, source: KnowledgeSource, file_path: str
    ) -> ProcessingResult:
        """
        Process a knowledge source file based on its type.

        Args:
            source: The knowledge source to process
            file_path: Path to the uploaded file

        Returns:
            Processing result with success status and metadata
        """
        try:
            logger.info(
                f"Starting processing for source: {source.filename} (type: {source.file_type})"
            )

            # Determine file type and route to appropriate processor
            if self._is_audio_file(file_path, source.file_type):
                return await self._process_audio_source(source, file_path)
            elif source.file_type == "application/pdf" or file_path.lower().endswith(
                ".pdf"
            ):
                return await self._process_pdf_source(source, file_path)
            elif source.file_type == "text/plain" or file_path.lower().endswith(".txt"):
                return await self._process_text_source(source, file_path)
            else:
                # Try to detect file type by extension
                file_extension = Path(file_path).suffix.lower()
                if file_extension in self.AUDIO_EXTENSIONS:
                    return await self._process_audio_source(source, file_path)
                else:
                    raise Exception(f"Unsupported file type: {source.file_type}")

        except Exception as e:
            logger.error(f"Error in _process_source for {source.id}: {str(e)}")
            raise

    # ...existing code for _process_pdf_source and _process_text_source...
