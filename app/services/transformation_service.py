"""
Transformation Service

Service for applying content transformations using LLM with prompt templates.
Supports loading source content, formatting prompts, and generating transformed results.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError, ValidationError
from app.core.llm.llm_client import LLMClient
from app.knowledge.services.rag_service import RagService
from app.knowledge.services.source_service import SourceService

logger = logging.getLogger(__name__)


@dataclass
class TransformationResult:
    """Result of a content transformation."""

    id: str
    source_id: str
    template_name: str
    transformed_content: str
    prompt_used: str
    metadata: dict[str, Any]
    created_at: datetime
    processing_time: float
    token_usage: dict[str, int] | None = None


class PromptTemplate(BaseModel):
    """Model for prompt templates."""

    name: str = Field(..., description="Unique name for the template")
    description: str = Field(..., description="Description of what this template does")
    template: str = Field(..., description="Jinja2 template string")
    variables: list[str] = Field(default_factory=list, description="List of required variables")
    output_format: str = Field(default="text", description="Expected output format")
    category: str = Field(default="general", description="Template category")
    tags: list[str] = Field(default_factory=list, description="Tags for organization")
    version: str = Field(default="1.0", description="Template version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TransformationRequest(BaseModel):
    """Request model for transformations."""

    source_id: str = Field(..., description="ID of the knowledge source")
    template_name: str = Field(..., description="Name of the prompt template to use")
    variables: dict[str, Any] = Field(default_factory=dict, description="Template variables")
    use_rag: bool = Field(default=True, description="Whether to use RAG for content retrieval")
    max_content_chunks: int = Field(default=10, description="Maximum chunks to include")
    include_metadata: bool = Field(default=True, description="Include source metadata")


class TransformationService:
    """
    Service for applying content transformations using LLM and templates.

    Handles loading source content, formatting prompts with Jinja2,
    and generating transformed results using language models.
    """

    def __init__(
        self,
        rag_service: RagService,
        source_service: SourceService,
        llm_client: LLMClient,
        templates_dir: str | Path = "app/templates/transformations",
    ):
        """
        Initialize the transformation service.

        Args:
            rag_service: Service for retrieving relevant content
            source_service: Service for source management
            llm_client: Client for LLM interactions
            templates_dir: Directory containing prompt templates
        """
        self.rag_service = rag_service
        self.source_service = source_service
        self.llm_client = llm_client
        self.templates_dir = Path(templates_dir)

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Cache for loaded templates
        self._template_cache: dict[str, PromptTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """Load all available prompt templates."""
        try:
            if not self.templates_dir.exists():
                logger.warning(f"Templates directory does not exist: {self.templates_dir}")
                return

            # Load templates from JSON files
            for template_file in self.templates_dir.glob("*.json"):
                try:
                    with template_file.open(encoding="utf-8") as f:
                        template_data = json.load(f)

                    template = PromptTemplate(**template_data)
                    self._template_cache[template.name] = template
                    logger.debug(f"Loaded template: {template.name}")

                except Exception as e:
                    logger.error(f"Error loading template from {template_file}: {str(e)}")

            logger.info(f"Loaded {len(self._template_cache)} prompt templates")

        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")

    async def apply_transformation(
        self,
        source_id: str,
        prompt_template: str,
        variables: dict[str, Any] | None = None,
        use_rag: bool = True,
        max_content_chunks: int = 10,
    ) -> TransformationResult:
        """
        Apply a transformation to source content using a prompt template.

        Args:
            source_id: ID of the knowledge source
            prompt_template: Name of the prompt template or template string
            variables: Additional variables for template rendering
            use_rag: Whether to use RAG for content retrieval
            max_content_chunks: Maximum number of content chunks to include

        Returns:
            Transformation result with generated content

        Raises:
            NotFoundError: If source or template not found
            ValidationError: If transformation fails
        """
        start_time = datetime.utcnow()
        transformation_id = str(uuid.uuid4())

        try:
            logger.info(f"Starting transformation {transformation_id} for source {source_id}")

            # Load source content
            source_content = await self._load_source_content(source_id, use_rag, max_content_chunks)

            # Get or create template
            template = await self._get_template(prompt_template)

            # Prepare template variables
            template_vars = {
                "source_content": source_content["content"],
                "source_metadata": source_content["metadata"],
                "source_id": source_id,
                **(variables or {}),
            }

            # Render prompt
            rendered_prompt = await self._render_prompt(template, template_vars)

            # Generate transformation using LLM
            transformed_content = await self._generate_transformation(rendered_prompt, template.output_format)

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Create result
            result = TransformationResult(
                id=transformation_id,
                source_id=source_id,
                template_name=template.name,
                transformed_content=transformed_content,
                prompt_used=rendered_prompt,
                metadata={
                    "template_version": template.version,
                    "template_category": template.category,
                    "content_chunks_used": source_content["chunk_count"],
                    "variables_used": list(template_vars.keys()),
                    "use_rag": use_rag,
                },
                created_at=start_time,
                processing_time=processing_time,
            )

            logger.info(f"Transformation {transformation_id} completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error in transformation {transformation_id}: {str(e)}")
            raise ValidationError(f"Transformation failed: {str(e)}") from e

    async def _load_source_content(self, source_id: str, use_rag: bool, max_chunks: int) -> dict[str, Any]:
        """
        Load content from a knowledge source.

        Args:
            source_id: ID of the source
            use_rag: Whether to use RAG for content retrieval
            max_chunks: Maximum chunks to retrieve

        Returns:
            Dictionary with content and metadata
        """
        try:
            # Get source metadata
            source = await self.source_service.get_source(source_id)
            if not source:
                raise NotFoundError(f"Source {source_id} not found")

            if use_rag:
                # Use RAG to get relevant content chunks
                # For transformation, we want comprehensive content, so use a broad query
                query = f"content from {source.filename}"
                content_chunks = await self.rag_service.retrieve_relevant_context(
                    query=query, source_ids=[source_id], k=max_chunks
                )
                content = "\n\n".join(content_chunks)
                chunk_count = len(content_chunks)
            else:
                # Get all content directly (this would need implementation in source_service)
                content = await self.source_service.get_full_content(source_id)
                chunk_count = 1

            return {
                "content": content,
                "metadata": {
                    "filename": source.filename,
                    "file_type": source.file_type,
                    "source_id": source_id,
                    "chunk_count": source.chunk_count,
                    "upload_date": source.upload_date.isoformat(),
                },
                "chunk_count": chunk_count,
            }

        except Exception as e:
            logger.error(f"Error loading content for source {source_id}: {str(e)}")
            raise

    async def _get_template(self, template_identifier: str) -> PromptTemplate:
        """
        Get a prompt template by name or treat as template string.

        Args:
            template_identifier: Template name or template string

        Returns:
            PromptTemplate object
        """
        # Check if it's a template name
        if template_identifier in self._template_cache:
            return self._template_cache[template_identifier]

        # Check if it's a template file
        template_file = self.templates_dir / f"{template_identifier}.json"
        if template_file.exists():
            try:
                with Path(template_file).open(encoding="utf-8") as f:
                    template_data = json.load(f)
                template = PromptTemplate(**template_data)
                self._template_cache[template.name] = template
                return template
            except Exception as e:
                logger.error(f"Error loading template file {template_file}: {str(e)}")

        # Treat as inline template string
        return PromptTemplate(
            name="inline_template",
            description="Inline template provided directly",
            template=template_identifier,
            variables=[],
            output_format="text",
            category="inline",
        )

    async def _render_prompt(self, template: PromptTemplate, variables: dict[str, Any]) -> str:
        """
        Render a Jinja2 template with provided variables.

        Args:
            template: The prompt template
            variables: Variables for template rendering

        Returns:
            Rendered prompt string
        """
        try:
            jinja_template = Template(template.template)
            rendered = jinja_template.render(**variables)
            return rendered.strip()

        except Exception as e:
            logger.error(f"Error rendering template {template.name}: {str(e)}")
            raise ValidationError(f"Template rendering failed: {str(e)}") from e

    async def _generate_transformation(self, prompt: str, output_format: str = "text") -> str:
        """
        Generate transformed content using LLM.

        Args:
            prompt: The rendered prompt
            output_format: Expected output format

        Returns:
            Generated content
        """
        try:
            # Prepare LLM request
            system_prompt = self._get_system_prompt(output_format)

            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.3,
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating transformation: {str(e)}")
            raise ValidationError(f"LLM generation failed: {str(e)}") from e

    def _get_system_prompt(self, output_format: str) -> str:
        """Get appropriate system prompt based on output format."""
        system_prompts = {
            "text": "You are a helpful assistant that transforms content according to the given instructions. "
            "Provide clear, well-structured responses.",
            "markdown": "You are a helpful assistant that transforms content into well-formatted Markdown. "
            "Use proper headings, lists, and formatting.",
            "json": "You are a helpful assistant that transforms content into valid JSON format. "
            "Ensure proper structure and syntax.",
            "summary": "You are a helpful assistant that creates concise, accurate summaries. "
            "Focus on key points and main ideas.",
            "analysis": "You are a helpful assistant that provides detailed analysis. "
            "Be thorough, objective, and insightful.",
        }

        return system_prompts.get(output_format, system_prompts["text"])

    async def get_available_templates(self) -> list[PromptTemplate]:
        """Get list of all available prompt templates."""
        return list(self._template_cache.values())

    async def create_template(self, template: PromptTemplate) -> bool:
        """
        Create a new prompt template.

        Args:
            template: Template to create

        Returns:
            True if created successfully
        """
        try:
            # Save to cache
            self._template_cache[template.name] = template

            # Save to file
            template_file = self.templates_dir / f"{template.name}.json"
            self.templates_dir.mkdir(parents=True, exist_ok=True)

            with template_file.open("w", encoding="utf-8") as f:
                json.dump(template.dict(), f, indent=2, default=str)

            logger.info(f"Created template: {template.name}")
            return True

        except Exception as e:
            logger.error(f"Error creating template {template.name}: {str(e)}")
            return False

    async def batch_transform(
        self, request: TransformationRequest, source_ids: list[str]
    ) -> list[TransformationResult]:
        """
        Apply transformation to multiple sources.

        Args:
            request: Transformation request parameters
            source_ids: List of source IDs to transform

        Returns:
            List of transformation results
        """
        results = []

        for source_id in source_ids:
            try:
                result = await self.apply_transformation(
                    source_id=source_id,
                    prompt_template=request.template_name,
                    variables=request.variables,
                    use_rag=request.use_rag,
                    max_content_chunks=request.max_content_chunks,
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Error transforming source {source_id}: {str(e)}")
                # Create error result
                error_result = TransformationResult(
                    id=str(uuid.uuid4()),
                    source_id=source_id,
                    template_name=request.template_name,
                    transformed_content="",
                    prompt_used="",
                    metadata={"error": str(e)},
                    created_at=datetime.utcnow(),
                    processing_time=0.0,
                )
                results.append(error_result)

        return results


# Default templates that can be created on service initialization
DEFAULT_TEMPLATES = [
    {
        "name": "summarize",
        "description": "Create a concise summary of the content",
        "template": """Please create a comprehensive summary of the following content:

**Source:** {{ source_metadata.filename }}
**Content:**
{{ source_content }}

Provide a clear, concise summary that captures the main points and key information.""",
        "variables": ["source_content", "source_metadata"],
        "output_format": "text",
        "category": "analysis",
        "tags": ["summary", "analysis"],
    },
    {
        "name": "extract_key_points",
        "description": "Extract key points and insights from content",
        "template": """Analyze the following content and extract the key points:

**Source:** {{ source_metadata.filename }}
**Content:**
{{ source_content }}

Please provide:
1. Main topics covered
2. Key insights or findings
3. Important details or facts
4. Actionable items (if any)

Format as a structured list.""",
        "variables": ["source_content", "source_metadata"],
        "output_format": "markdown",
        "category": "analysis",
        "tags": ["analysis", "extraction", "key-points"],
    },
    {
        "name": "convert_to_qa",
        "description": "Convert content into question-answer format",
        "template": """Convert the following content into a question and answer format:

**Source:** {{ source_metadata.filename }}
**Content:**
{{ source_content }}

Create relevant questions based on the content and provide clear, comprehensive answers. "
        "Focus on the most important information.""",
        "variables": ["source_content", "source_metadata"],
        "output_format": "markdown",
        "category": "education",
        "tags": ["qa", "education", "learning"],
    },
]
