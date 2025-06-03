"""
Podcast Generator Workflow

Specialized workflow for generating podcasts from knowledge content.
Aggregates content from notes/sources, generates scripts, and converts to audio.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.llm.llm_client import LLMClient
from app.knowledge.services.note_service import NoteService
from app.knowledge.services.rag_service import RagService
from app.knowledge.services.source_service import SourceService

# TTS imports (assuming ElevenLabs integration)
try:
    import elevenlabs

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logging.warning(
        "ElevenLabs not available. Install elevenlabs package for TTS functionality."
    )

logger = logging.getLogger(__name__)


@dataclass
class PodcastHost:
    """Configuration for a podcast host voice."""

    name: str
    voice_id: str
    personality: str
    role: str = "host"


@dataclass
class PodcastScript:
    """Generated podcast script with segments."""

    id: str
    title: str
    description: str
    hosts: list[PodcastHost]
    segments: list[dict[str, Any]]
    total_duration_estimate: int  # in seconds
    metadata: dict[str, Any]
    created_at: datetime


@dataclass
class PodcastAudio:
    """Generated podcast audio file."""

    id: str
    script_id: str
    file_path: str
    file_size: int
    duration: int
    format: str
    metadata: dict[str, Any]
    created_at: datetime


class PodcastGenerator:
    """
    Generates podcasts from knowledge content.

    Handles content aggregation, script generation, and audio synthesis
    to create complete podcast episodes from notes and sources.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        source_service: SourceService,
        note_service: NoteService,
        rag_service: RagService,
        output_dir: str | Path = "output/podcasts",
    ):
        """
        Initialize the podcast generator.

        Args:
            llm_client: Client for LLM interactions
            source_service: Service for knowledge sources
            note_service: Service for notes
            rag_service: Service for RAG content retrieval
            output_dir: Directory to save generated podcasts
        """
        self.llm_client = llm_client
        self.source_service = source_service
        self.note_service = note_service
        self.rag_service = rag_service
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure TTS if available
        self.tts_available = ELEVENLABS_AVAILABLE
        if self.tts_available and hasattr(settings, "elevenlabs_api_key"):
            elevenlabs.set_api_key(settings.elevenlabs_api_key)

        # Default podcast hosts configuration
        self.default_hosts = [
            PodcastHost(
                name="Alex",
                voice_id=getattr(settings, "podcast_host_1_voice_id", "default"),
                personality="enthusiastic and knowledgeable",
                role="main_host",
            ),
            PodcastHost(
                name="Sam",
                voice_id=getattr(settings, "podcast_host_2_voice_id", "default"),
                personality="thoughtful and analytical",
                role="co_host",
            ),
        ]

    async def generate_podcast(
        self,
        source_ids: list[str] | None = None,
        note_ids: list[str] | None = None,
        topic: str | None = None,
        style: str = "conversational",
        duration_target: int = 300,  # 5 minutes default
        hosts: list[PodcastHost] | None = None,
        include_intro: bool = True,
        include_outro: bool = True,
    ) -> dict[str, Any]:
        """
        Generate a complete podcast from content sources.

        Args:
            source_ids: Knowledge source IDs to include
            note_ids: Note IDs to include
            topic: Specific topic to focus on
            style: Podcast style (conversational, interview, monologue)
            duration_target: Target duration in seconds
            hosts: Custom host configurations
            include_intro: Include introduction segment
            include_outro: Include conclusion segment

        Returns:
            Dictionary with script and audio file information
        """
        try:
            logger.info("Starting podcast generation")

            # Use default hosts if none provided
            podcast_hosts = hosts or self.default_hosts

            # Aggregate content from sources
            content = await self._aggregate_content(source_ids, note_ids, topic)

            # Generate podcast script
            script = await self._generate_script(
                content=content,
                topic=topic,
                style=style,
                duration_target=duration_target,
                hosts=podcast_hosts,
                include_intro=include_intro,
                include_outro=include_outro,
            )

            # Generate audio from script
            audio = await self._generate_audio(script)

            return {
                "success": True,
                "script": script,
                "audio": audio,
                "metadata": {
                    "source_count": len(source_ids or []),
                    "note_count": len(note_ids or []),
                    "content_length": len(content),
                    "generation_time": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error generating podcast: {str(e)}")
            raise ValidationError(f"Podcast generation failed: {str(e)}") from e

    async def _aggregate_content(
        self,
        source_ids: list[str] | None,
        note_ids: list[str] | None,
        topic: str | None,
    ) -> str:
        """
        Aggregate content from various sources.

        Args:
            source_ids: Knowledge source IDs
            note_ids: Note IDs
            topic: Topic for RAG-based content retrieval

        Returns:
            Aggregated content string
        """
        content_parts = []

        try:
            # Get content from knowledge sources
            if source_ids:
                for source_id in source_ids:
                    try:
                        if topic:
                            # Use RAG to get relevant content
                            chunks = await self.rag_service.retrieve_relevant_context(
                                query=topic, source_ids=[source_id], k=5
                            )
                            source_content = "\n\n".join(chunks)
                        else:
                            # Get all content from source
                            source_content = await self.source_service.get_full_content(
                                source_id
                            )

                        source = await self.source_service.get_source(source_id)
                        content_parts.append(
                            f"# From {source.filename}\n\n{source_content}"
                        )

                    except Exception as e:
                        logger.error(
                            f"Error getting content from source {source_id}: {str(e)}"
                        )
                        continue

            # Get content from notes
            if note_ids:
                for note_id in note_ids:
                    try:
                        note = await self.note_service.get_note(note_id)
                        content_parts.append(f"# Note: {note.title}\n\n{note.content}")

                    except Exception as e:
                        logger.error(f"Error getting note {note_id}: {str(e)}")
                        continue

            # If no specific sources but topic provided, use RAG broadly
            if not source_ids and not note_ids and topic:
                try:
                    chunks = await self.rag_service.retrieve_relevant_context(
                        query=topic, k=10
                    )
                    content_parts.append(
                        f"# Content about {topic}\n\n" + "\n\n".join(chunks)
                    )
                except Exception as e:
                    logger.error(
                        f"Error getting RAG content for topic {topic}: {str(e)}"
                    )

            if not content_parts:
                raise ValidationError("No content found to generate podcast from")

            return "\n\n---\n\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error aggregating content: {str(e)}")
            raise

    async def _generate_script(
        self,
        content: str,
        topic: str | None,
        style: str,
        duration_target: int,
        hosts: list[PodcastHost],
        include_intro: bool,
        include_outro: bool,
    ) -> PodcastScript:
        """
        Generate podcast script using LLM.

        Args:
            content: Aggregated content
            topic: Main topic
            style: Podcast style
            duration_target: Target duration
            hosts: Host configurations
            include_intro: Include introduction
            include_outro: Include conclusion

        Returns:
            Generated podcast script
        """
        try:
            # Prepare prompt for script generation
            word_count_target = (
                duration_target * 2.5
            )  # ~150 words per minute speaking pace

            hosts_description = "\n".join(
                [f"- {host.name} ({host.role}): {host.personality}" for host in hosts]
            )

            prompt = f"""Generate a {style} podcast script based on the following content.

PODCAST DETAILS:
- Target duration: {duration_target} seconds (~{word_count_target:.0f} words)
- Style: {style}
- Topic: {topic or "Various topics from the content"}
- Include intro: {include_intro}
- Include outro: {include_outro}

HOSTS:
{hosts_description}

CONTENT TO DISCUSS:
{content[:8000]}  # Limit content length for prompt

INSTRUCTIONS:
1. Create an engaging podcast script with natural dialogue between the hosts
2. Structure the content logically with clear segments
3. Include smooth transitions between topics
4. Make the discussion accessible and interesting
5. Use the hosts' personalities to create dynamic conversation
6. Include timestamps for major segments
7. Format as: [HOST_NAME]: dialogue content

The script should feel natural and conversational, not like reading from notes."""

            # Generate script using LLM
            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt="You are an expert podcast script writer. Create engaging, natural-sounding dialogue that brings content to life through conversation.",
                max_tokens=3000,
                temperature=0.7,
            )

            # Parse the script into segments
            segments = self._parse_script_segments(response)

            # Create script object
            script_id = str(uuid.uuid4())
            script = PodcastScript(
                id=script_id,
                title=topic or "Generated Podcast",
                description="Podcast generated from knowledge content",
                hosts=hosts,
                segments=segments,
                total_duration_estimate=duration_target,
                metadata={
                    "style": style,
                    "word_count": len(response.split()),
                    "segment_count": len(segments),
                    "content_source_length": len(content),
                },
                created_at=datetime.utcnow(),
            )

            # Save script to file
            await self._save_script(script, response)

            return script

        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise

    def _parse_script_segments(self, script_text: str) -> list[dict[str, Any]]:
        """Parse script text into structured segments."""
        segments = []
        lines = script_text.split("\n")
        current_segment = {"type": "dialogue", "content": []}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for host dialogue (format: [HOST_NAME]: content)
            if ": " in line and line.startswith("[") and "]" in line:
                host_end = line.find("]")
                host_name = line[1:host_end]
                dialogue = line[host_end + 2 :].strip()

                current_segment["content"].append(
                    {"speaker": host_name, "text": dialogue}
                )
            # Check for timestamp markers
            elif line.startswith("[") and line.endswith("]") and "min" in line.lower():
                if current_segment["content"]:
                    segments.append(current_segment)
                current_segment = {"type": "timestamp", "time": line, "content": []}
            else:
                # Regular content or stage directions
                current_segment["content"].append({"speaker": "narrator", "text": line})

        if current_segment["content"]:
            segments.append(current_segment)

        return segments

    async def _save_script(self, script: PodcastScript, script_text: str):
        """Save script to file."""
        script_file = self.output_dir / f"script_{script.id}.json"
        text_file = self.output_dir / f"script_{script.id}.txt"

        # Save structured script
        with script_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": script.id,
                    "title": script.title,
                    "description": script.description,
                    "hosts": [
                        {"name": h.name, "role": h.role, "personality": h.personality}
                        for h in script.hosts
                    ],
                    "segments": script.segments,
                    "metadata": script.metadata,
                    "created_at": script.created_at.isoformat(),
                },
                f,
                indent=2,
            )

        # Save plain text script
        with text_file.open("w", encoding="utf-8") as f:
            f.write(script_text)

    async def _generate_audio(self, script: PodcastScript) -> PodcastAudio | None:
        """
        Generate audio from script using TTS.

        Args:
            script: Podcast script to convert

        Returns:
            Audio file information or None if TTS not available
        """
        if not self.tts_available:
            logger.warning("TTS not available, skipping audio generation")
            return None

        try:
            logger.info(f"Generating audio for script {script.id}")

            audio_segments = []

            # Process each segment
            for segment in script.segments:
                if segment["type"] == "dialogue":
                    for item in segment["content"]:
                        speaker = item["speaker"]
                        text = item["text"]

                        # Find matching host voice
                        voice_id = "default"
                        for host in script.hosts:
                            if host.name.lower() == speaker.lower():
                                voice_id = host.voice_id
                                break

                        # Generate audio for this text
                        if text.strip():
                            try:
                                audio_data = elevenlabs.generate(
                                    text=text,
                                    voice=voice_id,
                                    model="eleven_monolingual_v1",
                                )
                                audio_segments.append(audio_data)

                            except Exception as e:
                                logger.error(
                                    f"Error generating audio for segment: {str(e)}"
                                )
                                continue

            if not audio_segments:
                logger.warning("No audio segments generated")
                return None

            # Combine audio segments
            combined_audio = b"".join(audio_segments)

            # Save audio file
            audio_id = str(uuid.uuid4())
            audio_file = self.output_dir / f"podcast_{audio_id}.mp3"

            with audio_file.open("wb") as f:
                f.write(combined_audio)

            # Create audio object
            audio = PodcastAudio(
                id=audio_id,
                script_id=script.id,
                file_path=str(audio_file),
                file_size=len(combined_audio),
                duration=script.total_duration_estimate,
                format="mp3",
                metadata={
                    "segments_count": len(audio_segments),
                    "hosts_count": len(script.hosts),
                    "tts_model": "eleven_monolingual_v1",
                },
                created_at=datetime.utcnow(),
            )

            logger.info(f"Audio generated successfully: {audio_file}")
            return audio

        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return None


class PodcastWorkflow:
    """
    Workflow integration for podcast generation.

    Integrates podcast generation into the WorkflowService system.
    """

    def __init__(self, podcast_generator: PodcastGenerator):
        """Initialize with podcast generator."""
        self.podcast_generator = podcast_generator

    async def execute(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Execute podcast generation workflow.

        Args:
            config: Workflow configuration with podcast parameters

        Returns:
            Workflow result with podcast information
        """
        try:
            # Extract configuration
            source_ids = config.get("source_ids", [])
            note_ids = config.get("note_ids", [])
            topic = config.get("topic")
            style = config.get("style", "conversational")
            duration_target = config.get("duration_target", 300)
            include_intro = config.get("include_intro", True)
            include_outro = config.get("include_outro", True)

            # Generate podcast
            result = await self.podcast_generator.generate_podcast(
                source_ids=source_ids,
                note_ids=note_ids,
                topic=topic,
                style=style,
                duration_target=duration_target,
                include_intro=include_intro,
                include_outro=include_outro,
            )

            return {
                "status": "success",
                "result": "Podcast generated successfully",
                "data": {
                    "script_id": result["script"].id,
                    "audio_id": result["audio"].id if result["audio"] else None,
                    "audio_file": (
                        result["audio"].file_path if result["audio"] else None
                    ),
                    "title": result["script"].title,
                    "duration": result["script"].total_duration_estimate,
                    "metadata": result["metadata"],
                },
            }

        except Exception as e:
            logger.error(f"Podcast workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "result": f"Podcast generation failed: {str(e)}",
                "error": str(e),
            }


# Default podcast workflow configuration for WorkflowService integration
PODCAST_WORKFLOW_CONFIG = {
    "name": "podcast_generation",
    "type": "content_generation",
    "description": "Generate podcasts from knowledge content",
    "agent_type": "podcast_generator",
    "default_config": {
        "style": "conversational",
        "duration_target": 300,
        "include_intro": True,
        "include_outro": True,
    },
}
