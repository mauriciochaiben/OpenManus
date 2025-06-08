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
        query: str,
        source_ids=None,
        k=5,
    ):
        return ["dummy context"]


class DummySourceService:
    async def get_source(self, source_id: str):
        class Source:
            filename = "file.txt"
            file_type = "text"
            chunk_count = 1
            upload_date = __import__("datetime").datetime.utcnow()

        return Source()

    async def get_full_content(self, source_id: str):
        return "full content"


class DummyLLMClient:
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs,
    ):
        return "generated response"


@pytest.mark.asyncio
async def test_get_system_prompt_text():
    service = TransformationService(DummyRagService(), DummySourceService(), DummyLLMClient())
    prompt = service._get_system_prompt("text")
    assert "helpful assistant" in prompt
