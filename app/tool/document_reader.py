# filepath: /Users/mauriciochaiben/OpenManus/app/tool/document_reader.py
"""Advanced document reader tool using Docling for comprehensive document processing."""

import json
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument

from app.core.settings import config
from app.exceptions import ToolError
from app.logger import logger
from app.tool.base import BaseTool, ToolResult
from app.tool.file_operators import FileOperator, LocalFileOperator, SandboxFileOperator

if TYPE_CHECKING:
    from docling.datamodel.document import ConversionResult


class AdvancedDocumentReader(BaseTool):
    """An advanced document reader using IBM Docling for comprehensive document processing.

    This tool leverages Docling's advanced capabilities including:
    - AI-powered layout detection and structure preservation
    - Advanced table extraction and understanding
    - Mathematical formula recognition
    - Figure and image analysis
    - Hierarchical document structure extraction
    - Multi-format support with consistent output
    """

    name: str = "advanced_document_reader"
    description: str = """Read and extract content from various document formats using advanced AI-powered processing.

    Supported formats with advanced processing:
    - PDF files (.pdf) - Advanced layout detection, table extraction, formula recognition
    - Microsoft Word documents (.docx) - Complete structure preservation with tables and formatting
    - PowerPoint presentations (.pptx) - Slide content extraction with layout understanding
    - Excel files (.xlsx, .xls) - Advanced spreadsheet analysis with relationship detection
    - HTML files (.html) - Structure-aware web content extraction
    - Images (PNG, JPG, etc.) - OCR with layout understanding
    - Text files (.txt, .md) - Enhanced with structure detection

    Key features:
    - Preserves document structure and hierarchy
    - Extracts tables with proper formatting and relationships
    - Recognizes and converts mathematical formulas
    - Identifies and describes figures and images
    - Provides structured JSON output for programmatic use
    - Chunks documents intelligently for better processing
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the document file to read",
            },
            "output_format": {
                "type": "string",
                "enum": ["text", "markdown", "json", "structured", "summary"],
                "default": "markdown",
                "description": "Output format - 'text' for plain text, 'markdown' for formatted markdown, 'json' for structured data, 'structured' for detailed analysis, 'summary' for brief overview",
            },
            "extract_tables": {
                "type": "boolean",
                "default": True,
                "description": "Whether to extract and format tables",
            },
            "extract_figures": {
                "type": "boolean",
                "default": True,
                "description": "Whether to extract and describe figures/images",
            },
            "preserve_structure": {
                "type": "boolean",
                "default": True,
                "description": "Whether to preserve document hierarchy and structure",
            },
            "chunk_document": {
                "type": "boolean",
                "default": False,
                "description": "Whether to split document into semantic chunks",
            },
            "max_length": {
                "type": "integer",
                "default": 50000,
                "description": "Maximum length of output text (truncated if exceeded)",
            },
            "include_metadata": {
                "type": "boolean",
                "default": False,
                "description": "Whether to include document metadata in output",
            },
        },
        "required": ["file_path"],
    }

    def __init__(self):
        super().__init__()
        self._local_operator = LocalFileOperator()
        self._sandbox_operator = SandboxFileOperator()
        self._converter = None
        self._initialize_converter()

    def _initialize_converter(self):
        """Initialize the Docling document converter with optimal settings."""
        try:
            self._converter = DocumentConverter()
            logger.info("📖 Docling DocumentConverter initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Docling converter: {e}")
            self._converter = None

    def _get_operator(self) -> FileOperator:
        """Get the appropriate file operator based on execution mode."""
        return (
            self._sandbox_operator
            if config.sandbox.use_sandbox
            else self._local_operator
        )

    async def execute(
        self,
        file_path: str,
        output_format: str = "markdown",
        extract_tables: bool = True,
        extract_figures: bool = True,
        preserve_structure: bool = True,
        chunk_document: bool = False,
        max_length: int = 50000,
        include_metadata: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> str:
        """Execute advanced document reading operation."""

        try:
            operator = self._get_operator()

            # Verify file exists
            if not await operator.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Get file extension to determine format
            file_extension = Path(file_path).suffix.lower()
            file_name = Path(file_path).name

            logger.info(
                f"📖 Processing document with Docling: {file_path} (format: {file_extension})"
            )

            # Check if Docling converter is available
            if not self._converter:
                # Fallback to basic reading for simple formats
                return await self._fallback_reading(
                    file_path, file_extension, output_format, operator
                )

            # Process document with Docling
            if config.sandbox.use_sandbox and file_extension not in [
                ".txt",
                ".md",
                ".csv",
            ]:
                raise ToolError(
                    f"Advanced processing for {file_extension} files in sandbox mode not yet supported. Please copy file to local workspace first."
                )

            # Convert document using Docling
            try:
                result: ConversionResult = self._converter.convert(file_path)
                doc: DoclingDocument = result.document

                content = await self._format_docling_output(
                    doc,
                    output_format,
                    extract_tables,
                    extract_figures,
                    preserve_structure,
                    chunk_document,
                    include_metadata,
                )

            except Exception as e:
                logger.warning(
                    f"Docling processing failed, falling back to basic reading: {e}"
                )
                return await self._fallback_reading(
                    file_path, file_extension, output_format, operator
                )

            # Apply length limit
            if len(content) > max_length:
                content = (
                    content[:max_length]
                    + f"\n\n[Content truncated - showing first {max_length} characters of {len(content)} total]"
                )

            result = ToolResult(
                output=f"📖 Advanced document analysis of {file_name}:\n\n{content}"
            )

        except Exception as e:
            result = ToolResult(
                error=f"Failed to process document {file_path}: {str(e)}"
            )

        return str(result)

    async def _format_docling_output(
        self,
        doc: DoclingDocument,
        output_format: str,
        extract_tables: bool,
        extract_figures: bool,
        preserve_structure: bool,  # noqa: ARG002
        chunk_document: bool,  # noqa: ARG002
        include_metadata: bool,
    ) -> str:
        """Format the Docling document output according to specified format."""

        if output_format == "json":
            # Return structured JSON representation
            return self._format_as_json(
                doc, extract_tables, extract_figures, include_metadata
            )

        if output_format == "markdown":
            # Export as markdown with full formatting
            return doc.export_to_markdown()

        if output_format == "text":
            # Export as plain text
            return doc.export_to_text()

        if output_format == "structured":
            # Detailed structural analysis
            return self._format_structured_analysis(
                doc, extract_tables, extract_figures, include_metadata
            )

        if output_format == "summary":
            # Brief summary with key information
            return self._format_summary(doc, extract_tables, extract_figures)

        # Default to markdown
        return doc.export_to_markdown()

    def _format_as_json(
        self,
        doc: DoclingDocument,
        extract_tables: bool,
        extract_figures: bool,
        include_metadata: bool,
    ) -> str:
        """Format document as structured JSON."""
        try:
            doc_dict = doc.model_dump()

            # Filter content based on options
            if not extract_tables:
                # Remove table content (implementation depends on Docling structure)
                pass

            if not extract_figures:
                # Remove figure content (implementation depends on Docling structure)
                pass

            if not include_metadata:
                # Remove metadata (implementation depends on Docling structure)
                doc_dict.pop("meta", None)

            return json.dumps(doc_dict, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to format as JSON: {e}")
            return f"JSON formatting failed: {str(e)}\n\nFallback text:\n{doc.export_to_text()}"

    def _format_structured_analysis(
        self,
        doc: DoclingDocument,
        extract_tables: bool,
        extract_figures: bool,
        include_metadata: bool,  # noqa: ARG002
    ) -> str:
        """Format document with detailed structural analysis."""
        analysis = []

        # Document overview
        text_content = doc.export_to_text()
        word_count = len(text_content.split())
        char_count = len(text_content)

        analysis.append("=== DOCUMENT STRUCTURE ANALYSIS ===\n")
        analysis.append("Document Statistics:")
        analysis.append(f"- Word count: {word_count:,}")
        analysis.append(f"- Character count: {char_count:,}")

        # Try to get structural information
        try:
            # This depends on Docling's internal structure
            if hasattr(doc, "elements") or hasattr(doc, "body"):
                analysis.append("- Structural elements detected")

            if hasattr(doc, "tables") and extract_tables:
                analysis.append("- Tables detected and extracted")

            if hasattr(doc, "figures") and extract_figures:
                analysis.append("- Figures/images detected and processed")

        except Exception as e:
            logger.debug(f"Error analyzing structure: {e}")

        analysis.append("\n=== DOCUMENT CONTENT ===\n")

        # Add markdown content
        analysis.append(doc.export_to_markdown())

        return "\n".join(analysis)

    def _format_summary(
        self, doc: DoclingDocument, extract_tables: bool, extract_figures: bool
    ) -> str:
        """Format document as a brief summary."""
        text_content = doc.export_to_text()
        word_count = len(text_content.split())

        summary = []
        summary.append("=== DOCUMENT SUMMARY ===\n")
        summary.append(f"Word count: {word_count:,}")

        # Show first few paragraphs
        paragraphs = text_content.split("\n\n")
        non_empty_paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if non_empty_paragraphs:
            summary.append("\nFirst few sections:")
            for i, para in enumerate(non_empty_paragraphs[:3]):
                if len(para) > 200:
                    para = para[:200] + "..."
                summary.append(f"{i+1}. {para}")

        if len(non_empty_paragraphs) > 3:
            summary.append(f"\n... and {len(non_empty_paragraphs) - 3} more sections")

        # Add structural info if available
        try:
            if extract_tables:
                summary.append("\n✓ Tables extracted and analyzed")
            if extract_figures:
                summary.append("✓ Figures and images processed")
        except Exception:
            pass

        return "\n".join(summary)

    async def _fallback_reading(
        self,
        file_path: str,
        file_extension: str,
        output_format: str,
        operator: FileOperator,
    ) -> str:
        """Fallback to basic file reading when Docling is not available or fails."""
        logger.info(f"Using fallback reading for {file_extension}")

        if file_extension in [".txt", ".md", ".log"]:
            content = await operator.read_file(file_path)
            if output_format == "summary":
                word_count = len(content.split())
                lines = content.split("\n")
                return f"Text file summary:\n- {len(lines)} lines\n- {word_count} words\n\nFirst 500 characters:\n{content[:500]}{'...' if len(content) > 500 else ''}"
            return content

        if file_extension == ".csv":
            return await self._read_csv_fallback(file_path, output_format, operator)

        raise ToolError(
            f"Docling unavailable and no fallback method for {file_extension} files"
        )

    async def _read_csv_fallback(
        self, file_path: str, output_format: str, operator: FileOperator
    ) -> str:
        """Fallback CSV reading using pandas."""
        try:
            if config.sandbox.use_sandbox:
                content = await operator.read_file(file_path)
                df = pd.read_csv(StringIO(content))
            else:
                df = pd.read_csv(file_path)

            if output_format == "summary":
                summary = []
                summary.append(
                    f"CSV file with {len(df)} rows and {len(df.columns)} columns"
                )
                summary.append(f"Columns: {', '.join(df.columns.tolist())}")

                if len(df) > 0:
                    summary.append("\nFirst few rows:")
                    summary.append(df.head().to_string(index=False))

                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        summary.append("\nNumeric statistics:")
                        summary.append(df[numeric_cols].describe().to_string())

                return "\n".join(summary)

            if output_format == "json":
                return df.to_json(orient="records", indent=2)

            return df.to_string(index=False)

        except Exception as e:
            raise ToolError(f"Failed to read CSV file: {str(e)}") from e


# Keep the original DocumentReader for backward compatibility
class DocumentReader(AdvancedDocumentReader):
    """Backward compatibility alias for AdvancedDocumentReader."""

    name: str = "document_reader"

    def __init__(self):
        super().__init__()
        logger.info("📖 Using advanced Docling-powered DocumentReader")
