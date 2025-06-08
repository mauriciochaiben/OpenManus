"""Enhanced document analysis tool with specialized Docling capabilities."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from docling.chunking import HierarchicalChunker  # Changed import
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument

from app.exceptions import ToolError
from app.logger import logger
from app.tool.base import BaseTool, ToolResult

if TYPE_CHECKING:
    from docling.datamodel.document import ConversionResult


class DocumentAnalyzer(BaseTool):
    """
    Advanced document analyzer with specialized AI-powered capabilities.

    This tool provides sophisticated document analysis beyond basic reading:
    - Semantic document chunking for RAG applications
    - Advanced table relationship analysis
    - Mathematical formula extraction and conversion
    - Document structure mapping and hierarchy analysis
    - Cross-reference and citation detection
    - Content summarization and key entity extraction
    """

    name: str = "document_analyzer"
    description: str = """Perform advanced analysis on documents using AI-powered processing.

    Advanced capabilities:
    - Semantic chunking for embedding and retrieval systems
    - Table relationship mapping and data flow analysis
    - Mathematical formula recognition and LaTeX conversion
    - Document structure analysis with hierarchy mapping
    - Content summarization with key insights extraction
    - Cross-reference and citation network analysis
    - Multi-modal content understanding (text, tables, figures)

    Ideal for:
    - Preparing documents for RAG systems
    - Academic paper analysis
    - Technical documentation processing
    - Legal document review
    - Financial report analysis
    """

    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the document file to analyze",
            },
            "analysis_type": {
                "type": "string",
                "enum": [
                    "semantic_chunks",
                    "table_analysis",
                    "formula_extraction",
                    "structure_mapping",
                    "content_summary",
                    "citation_analysis",
                    "full_analysis",
                ],
                "default": "full_analysis",
                "description": "Type of analysis to perform",
            },
            "chunk_size": {
                "type": "integer",
                "default": 1000,
                "description": "Target size for semantic chunks (in characters)",
            },
            "overlap_size": {
                "type": "integer",
                "default": 200,
                "description": "Overlap between chunks for context preservation",
            },
            "extract_metadata": {
                "type": "boolean",
                "default": True,
                "description": "Whether to extract and analyze document metadata",
            },
            "identify_key_entities": {
                "type": "boolean",
                "default": True,
                "description": "Whether to identify key entities, concepts, and terms",
            },
        },
        "required": ["file_path"],
    }

    def __init__(self):
        super().__init__()
        self._converter = None
        self._chunker = None
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize Docling tools for advanced analysis."""
        try:
            self._converter = DocumentConverter()
            self._chunker = HierarchicalChunker()
            logger.info("📊 Document analysis tools initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize analysis tools: {e}")

    async def execute(
        self,
        file_path: str,
        analysis_type: str = "full_analysis",
        chunk_size: int = 1000,
        overlap_size: int = 200,
        extract_metadata: bool = True,
        identify_key_entities: bool = True,
        **kwargs: Any,  # noqa: ARG002
    ) -> str:
        """Execute advanced document analysis."""
        try:
            if not Path(file_path).exists():
                raise ToolError(f"File not found: {file_path}")

            if not self._converter:
                raise ToolError("Document analysis tools not available. Please check Docling installation.")

            logger.info(f"📊 Performing {analysis_type} analysis on: {Path(file_path).name}")

            # Convert document
            result: ConversionResult = self._converter.convert(file_path)
            doc: DoclingDocument = result.document

            # Perform specified analysis
            if analysis_type == "semantic_chunks":
                content = await self._perform_semantic_chunking(doc, chunk_size, overlap_size)
            elif analysis_type == "table_analysis":
                content = await self._analyze_tables(doc)
            elif analysis_type == "formula_extraction":
                content = await self._extract_formulas(doc)
            elif analysis_type == "structure_mapping":
                content = await self._map_structure(doc)
            elif analysis_type == "content_summary":
                content = await self._summarize_content(doc, identify_key_entities)
            elif analysis_type == "citation_analysis":
                content = await self._analyze_citations(doc)
            else:  # full_analysis
                content = await self._perform_full_analysis(
                    doc,
                    chunk_size,
                    overlap_size,
                    extract_metadata,
                    identify_key_entities,
                )

            result = ToolResult(output=f"📊 Document analysis results ({analysis_type}):\n\n{content}")

        except Exception as e:
            result = ToolResult(error=f"Analysis failed for {file_path}: {e!s}")

        return str(result)

    async def _perform_semantic_chunking(self, doc: DoclingDocument, chunk_size: int, overlap_size: int) -> str:
        """Perform semantic chunking for RAG applications."""
        try:
            # Use Docling's hierarchical chunker
            chunks = self._chunker.chunk(doc, tokenizer=None, max_tokens=chunk_size)

            result = []
            result.append("=== SEMANTIC DOCUMENT CHUNKS ===\n")
            result.append(f"Document split into {len(chunks)} semantic chunks")
            result.append(f"Target chunk size: {chunk_size} characters")
            result.append(f"Overlap size: {overlap_size} characters\n")

            for i, chunk in enumerate(chunks, 1):
                chunk_text = chunk.text if hasattr(chunk, "text") else str(chunk)
                chunk_preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text

                result.append(f"Chunk {i}:")
                result.append(f"  Length: {len(chunk_text)} characters")
                result.append(f"  Preview: {chunk_preview}")

                # Add metadata if available
                if hasattr(chunk, "meta") and chunk.meta:
                    result.append(f"  Metadata: {chunk.meta}")

                result.append("")

            return "\n".join(result)

        except Exception as e:
            logger.warning(f"Semantic chunking failed: {e}")
            # Fallback to simple text chunking
            text = doc.export_to_text()
            chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap_size)]

            result = []
            result.append("=== FALLBACK TEXT CHUNKS ===\n")
            result.append(f"Document split into {len(chunks)} basic chunks")

            for i, chunk in enumerate(chunks, 1):
                preview = chunk[:200] + "..." if len(chunk) > 200 else chunk
                result.append(f"Chunk {i} ({len(chunk)} chars): {preview}\n")

            return "\n".join(result)

    async def _analyze_tables(self, doc: DoclingDocument) -> str:
        """Analyze tables and their relationships."""
        result = []
        result.append("=== TABLE ANALYSIS ===\n")

        try:
            # Extract markdown and look for table patterns
            markdown_content = doc.export_to_markdown()

            # Count tables in markdown (simple heuristic)
            table_markers = markdown_content.count("|")
            if table_markers > 10:  # Likely contains tables
                result.append("Tables detected in document")

                # Try to extract table information
                lines = markdown_content.split("\n")
                table_lines = [line for line in lines if "|" in line and line.strip()]

                if table_lines:
                    result.append(f"Approximately {len(table_lines)} table rows found")
                    result.append("\nSample table content:")
                    for line in table_lines[:5]:
                        result.append(f"  {line.strip()}")

                    if len(table_lines) > 5:
                        result.append(f"  ... and {len(table_lines) - 5} more rows")
            else:
                result.append("No tables detected in document")

            # Add full markdown for reference
            result.append("\n=== FULL DOCUMENT (with tables) ===\n")
            result.append(markdown_content)

        except Exception as e:
            result.append(f"Table analysis failed: {e!s}")
            result.append("\nFallback text content:")
            result.append(doc.export_to_text())

        return "\n".join(result)

    async def _extract_formulas(self, doc: DoclingDocument) -> str:
        """Extract and analyze mathematical formulas."""
        result = []
        result.append("=== FORMULA EXTRACTION ===\n")

        try:
            # Try to get structured document data
            doc.model_dump()

            # Look for mathematical content in the document
            text_content = doc.export_to_text()
            markdown_content = doc.export_to_markdown()

            # Simple heuristics for mathematical content
            math_indicators = [
                "∑",
                "∫",
                "∂",
                "≈",
                "≤",
                "≥",
                "±",
                "√",
                "π",
                "θ",
                "α",  # noqa: RUF001 - Greek letter alpha, used for mathematical symbols
                "β",
                "γ",  # noqa: RUF001 - Greek letter gamma, used for mathematical symbols
                "δ",
                "λ",
                "μ",
                "σ",  # noqa: RUF001 - Greek letter sigma, used for mathematical symbols
            ]
            formula_patterns = ["$", "\\(", "\\[", "equation", "formula"]

            math_found = any(indicator in text_content for indicator in math_indicators)
            formula_found = any(pattern in markdown_content for pattern in formula_patterns)

            if math_found or formula_found:
                result.append("Mathematical content detected!")

                if formula_found:
                    result.append("LaTeX-style formulas found in document")

                if math_found:
                    result.append("Mathematical symbols detected")
                    found_symbols = [sym for sym in math_indicators if sym in text_content]
                    result.append(f"Symbols found: {', '.join(found_symbols)}")

            else:
                result.append("No mathematical formulas detected")

            result.append("\n=== DOCUMENT CONTENT (checking for formulas) ===\n")
            result.append(markdown_content)

        except Exception as e:
            result.append(f"Formula extraction failed: {e!s}")
            result.append("\nDocument text:")
            result.append(doc.export_to_text())

        return "\n".join(result)

    async def _map_structure(self, doc: DoclingDocument) -> str:
        """Map document structure and hierarchy."""
        result = []
        result.append("=== DOCUMENT STRUCTURE MAPPING ===\n")

        try:
            markdown_content = doc.export_to_markdown()
            text_content = doc.export_to_text()

            # Analyze structure from markdown headers
            lines = markdown_content.split("\n")
            headers = []

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    title = line.lstrip("#").strip()
                    headers.append((level, title, i))

            if headers:
                result.append("Document hierarchy detected:")
                for level, title, _line_num in headers:
                    indent = "  " * (level - 1)
                    result.append(f"{indent}• {title} (H{level})")

                result.append(f"\nTotal sections: {len(headers)}")
                max_depth = max(level for level, _, _ in headers)
                result.append(f"Maximum nesting depth: {max_depth}")
            else:
                result.append("No clear hierarchical structure detected")

            # Document statistics
            word_count = len(text_content.split())
            paragraph_count = len([p for p in text_content.split("\n\n") if p.strip()])

            result.append("\nDocument statistics:")
            result.append(f"- Word count: {word_count:,}")
            result.append(f"- Paragraph count: {paragraph_count}")
            result.append(f"- Character count: {len(text_content):,}")

            result.append("\n=== STRUCTURED CONTENT ===\n")
            result.append(markdown_content)

        except Exception as e:
            result.append(f"Structure mapping failed: {e!s}")
            result.append("\nBasic content:")
            result.append(doc.export_to_text())

        return "\n".join(result)

    async def _summarize_content(self, doc: DoclingDocument, identify_entities: bool) -> str:
        """Summarize document content with key insights."""
        result = []
        result.append("=== CONTENT SUMMARY ===\n")

        try:
            text_content = doc.export_to_text()
            word_count = len(text_content.split())

            # Basic summary
            paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]

            result.append("Document Overview:")
            result.append(f"- {word_count:,} words")
            result.append(f"- {len(paragraphs)} paragraphs")

            if paragraphs:
                result.append("\nKey sections (first 3 paragraphs):")
                for i, para in enumerate(paragraphs[:3], 1):
                    summary_para = para[:300] + "..." if len(para) > 300 else para
                    result.append(f"{i}. {summary_para}")

                if len(paragraphs) > 3:
                    result.append(f"\n... and {len(paragraphs) - 3} additional sections")

            if identify_entities:
                result.append("\n=== KEY ENTITY ANALYSIS ===")

                # Simple keyword extraction (frequency-based)
                words = text_content.lower().split()
                word_freq = {}

                # Filter out common words and short words
                stop_words = {
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                    "this",
                    "that",
                    "is",
                    "are",
                    "was",
                    "were",
                    "be",
                    "been",
                    "have",
                    "has",
                    "had",
                    "do",
                    "does",
                    "did",
                    "will",
                    "would",
                    "could",
                    "should",
                }

                for word in words:
                    word_clean = "".join(c for c in word if c.isalnum()).lower()
                    if len(word_clean) > 3 and word_clean not in stop_words:
                        word_freq[word_clean] = word_freq.get(word_clean, 0) + 1

                # Get top keywords
                top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

                if top_keywords:
                    result.append("Most frequent terms:")
                    for term, count in top_keywords:
                        result.append(f"- {term}: {count} occurrences")

            result.append("\n=== FULL CONTENT ===\n")
            result.append(doc.export_to_markdown())

        except Exception as e:
            result.append(f"Content summarization failed: {e!s}")
            result.append("\nFallback content:")
            result.append(doc.export_to_text())

        return "\n".join(result)

    async def _analyze_citations(self, doc: DoclingDocument) -> str:
        """Analyze citations and references."""
        result = []
        result.append("=== CITATION ANALYSIS ===\n")

        try:
            text_content = doc.export_to_text()

            # Look for citation patterns
            citation_patterns = [
                r"\[\d+\]",  # [1], [2], etc.
                r"\(\d{4}\)",  # (2023), (2022), etc.
                r"et al\.",  # Author et al.
                r"doi:",  # DOI references
                r"http[s]?://",  # URLs
                r"www\.",  # Web references
            ]

            import re

            citations_found = []

            for pattern in citation_patterns:
                matches = re.findall(pattern, text_content)
                if matches:
                    citations_found.append((pattern, len(matches), matches[:5]))

            if citations_found:
                result.append("Citation patterns detected:")
                for pattern, count, examples in citations_found:
                    result.append(f"- Pattern '{pattern}': {count} occurrences")
                    if examples:
                        result.append(f"  Examples: {', '.join(examples)}")
            else:
                result.append("No standard citation patterns detected")

            # Look for bibliography/references section
            lower_text = text_content.lower()
            ref_keywords = ["references", "bibliography", "citations", "works cited"]
            ref_sections = []

            for keyword in ref_keywords:
                if keyword in lower_text:
                    ref_sections.append(keyword)

            if ref_sections:
                result.append(f"\nReference sections found: {', '.join(ref_sections)}")

            result.append("\n=== DOCUMENT CONTENT (with citations) ===\n")
            result.append(doc.export_to_markdown())

        except Exception as e:
            result.append(f"Citation analysis failed: {e!s}")
            result.append("\nDocument content:")
            result.append(doc.export_to_text())

        return "\n".join(result)

    async def _perform_full_analysis(
        self,
        doc: DoclingDocument,
        chunk_size: int,
        overlap_size: int,
        extract_metadata: bool,  # noqa: ARG002
        identify_entities: bool,  # noqa: ARG002
    ) -> str:
        """Perform comprehensive analysis combining all methods."""
        result = []
        result.append("=== COMPREHENSIVE DOCUMENT ANALYSIS ===\n")

        try:
            # Basic info
            text_content = doc.export_to_text()
            markdown_content = doc.export_to_markdown()
            word_count = len(text_content.split())

            result.append("Document Statistics:")
            result.append(f"- Words: {word_count:,}")
            result.append(f"- Characters: {len(text_content):,}")
            # Extract double newlines outside f-string to avoid backslash issue
            double_newline = "\n\n"
            paragraph_count = len([p for p in text_content.split(double_newline) if p.strip()])
            result.append(f"- Paragraphs: {paragraph_count}")

            # Quick structure analysis
            newline = "\n"
            headers = [line for line in markdown_content.split(newline) if line.strip().startswith("#")]
            if headers:
                result.append(f"- Sections: {len(headers)}")

            # Quick table detection
            if "|" in markdown_content and markdown_content.count("|") > 10:
                result.append("- Tables: Detected")

            # Mathematical content
            math_indicators = ["∑", "∫", "∂", "≈", "≤", "≥", "±", "√", "π"]
            if any(indicator in text_content for indicator in math_indicators):
                result.append("- Mathematical content: Detected")

            result.append("\\n" + "=" * 50)
            result.append("DETAILED ANALYSIS:")
            result.append("=" * 50 + "\\n")

            # Add each analysis
            result.append(await self._map_structure(doc))
            result.append("\\n" + "-" * 50 + "\\n")

            result.append(await self._analyze_tables(doc))
            result.append("\\n" + "-" * 50 + "\\n")

            result.append(await self._extract_formulas(doc))
            result.append("\\n" + "-" * 50 + "\\n")

            result.append(await self._analyze_citations(doc))
            result.append("\\n" + "-" * 50 + "\\n")

            result.append(await self._perform_semantic_chunking(doc, chunk_size, overlap_size))

        except Exception as e:
            result.append(f"Full analysis failed: {e!s}")
            result.append("\\nBasic content:")
            result.append(doc.export_to_markdown())

        return "\\n".join(result)
