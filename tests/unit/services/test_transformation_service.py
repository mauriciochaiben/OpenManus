import pytest

# Check dependencies early
pytest.importorskip("chromadb")

# Standard library imports
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "../../../"))

# Application imports
from app.services.transformation_service import TransformationService


class DummyRagService:
    async def retrieve_relevant_context(
        self,
        query: str,  # noqa: ARG002
        source_ids=None,  # noqa: ARG002
        k=5,  # noqa: ARG002
    ):
        return ["dummy context"]


class DummySourceService:
    async def get_source(self, source_id: str):  # noqa: ARG002
        class Source:
            filename = "file.txt"
            file_type = "text"
            chunk_count = 1
            upload_date = __import__("datetime").datetime.utcnow()

        return Source()

    async def get_full_content(self, source_id: str):  # noqa: ARG002
        return "full content"


class DummyLLMClient:
    async def generate_response(
        self,
        prompt: str,  # noqa: ARG002
        system_prompt: str,  # noqa: ARG002
        **kwargs,  # noqa: ARG002
    ):
        return "generated response"


@pytest.mark.asyncio
async def test_get_system_prompt_text():
    service = TransformationService(DummyRagService(), DummySourceService(), DummyLLMClient())
    prompt = service._get_system_prompt("text")
    assert "helpful assistant" in prompt
