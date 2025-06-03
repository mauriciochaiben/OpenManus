"""Text processing utilities for the OpenManus knowledge management system."""

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    id: str
    content: str
    metadata: dict[str, Any]
    start_position: int | None = None
    end_position: int | None = None


class TextProcessor:
    """Text processing utility for splitting text into chunks and processing documents."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the text processor.

        Args:
            chunk_size: Maximum size of each text chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def split_text(
        self,
        text: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        source_metadata: dict[str, Any] | None = None,
    ) -> list[TextChunk]:
        """Split text into overlapping chunks.

        Args:
            text: The text to split
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap
            source_metadata: Metadata to include with each chunk

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap
        source_metadata = source_metadata or {}

        # Clean up the text
        text = self._clean_text(text)

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate end position for this chunk
            end = min(start + chunk_size, len(text))

            # If we're not at the end of the text, try to break at a sentence boundary
            if end < len(text):
                end = self._find_sentence_boundary(text, end, start + chunk_size // 2)

            # Extract the chunk text
            chunk_text = text[start:end].strip()

            if chunk_text:  # Only create chunk if it has content
                chunk_id = (
                    f"{source_metadata.get('source_id', 'unknown')}_{chunk_index}"
                )

                chunk_metadata = {
                    **source_metadata,
                    "chunk_index": chunk_index,
                    "chunk_size": len(chunk_text),
                    "start_position": start,
                    "end_position": end,
                    "overlap_with_previous": chunk_index > 0,
                }

                chunk = TextChunk(
                    id=chunk_id,
                    content=chunk_text,
                    metadata=chunk_metadata,
                    start_position=start,
                    end_position=end,
                )

                chunks.append(chunk)
                chunk_index += 1

            # Move start position for next chunk, considering overlap
            if end >= len(text):
                break

            start = max(start + 1, end - chunk_overlap)

        logger.info(
            f"Split text into {len(chunks)} chunks (original length: {len(text)} chars)"
        )
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove excessive newlines
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        # Strip leading/trailing whitespace
        return text.strip()

    def _find_sentence_boundary(
        self, text: str, preferred_end: int, min_end: int
    ) -> int:
        """Find a good sentence boundary for splitting text.

        Args:
            text: The text to search
            preferred_end: Preferred end position
            min_end: Minimum acceptable end position

        Returns:
            Best end position for the chunk
        """
        # Look for sentence endings within a reasonable range
        search_start = max(min_end, preferred_end - 100)
        search_end = min(len(text), preferred_end + 100)

        # Search for sentence boundaries (period, exclamation, question mark)
        sentence_endings = []
        for i in range(search_start, search_end):
            char = text[i]
            if (
                char in ".!?"
                and i + 1 < len(text)
                and (text[i + 1].isspace() or text[i + 1] in "\n\r")
                and not (
                    char == "."
                    and i > 0
                    and text[i - 1].isupper()
                    and i > 1
                    and text[i - 2].isupper()
                )
            ):
                sentence_endings.append(i + 1)

        if sentence_endings:
            # Find the sentence ending closest to our preferred position
            return min(sentence_endings, key=lambda x: abs(x - preferred_end))

        # Look for paragraph breaks
        for i in range(search_start, search_end):
            if text[i : i + 2] == "\n\n":
                return i

        # Look for single line breaks
        for i in range(search_start, search_end):
            if text[i] == "\n":
                return i

        # If no good boundary found, use preferred end
        return preferred_end

    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> list[str]:
        """Extract key phrases from text.

        Args:
            text: Text to analyze
            max_phrases: Maximum number of phrases to return

        Returns:
            List of key phrases
        """
        # Simple extraction based on common patterns
        # In a real implementation, you might use NLP libraries like spaCy or NLTK

        # Split into sentences
        sentences = re.split(r"[.!?]+", text)

        phrases = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                # Extract noun phrases (simplified pattern)
                words = sentence.split()
                if len(words) >= 3 and len(words) <= 10:
                    phrases.append(sentence)

        # Sort by length and take the most substantial phrases
        phrases.sort(key=len, reverse=True)
        return phrases[:max_phrases]

    def calculate_readability(self, text: str) -> dict[str, float]:
        """Calculate basic readability metrics.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with readability metrics
        """
        if not text.strip():
            return {"words": 0, "sentences": 0, "avg_words_per_sentence": 0}

        # Count words
        words = len(text.split())

        # Count sentences (simple approximation)
        sentences = len(re.findall(r"[.!?]+", text))
        if sentences == 0:
            sentences = 1

        avg_words_per_sentence = words / sentences

        return {
            "words": words,
            "sentences": sentences,
            "avg_words_per_sentence": avg_words_per_sentence,
            "estimated_reading_time_minutes": max(1, words // 200),
        }
