import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
import pytest
pytest.importorskip("chromadb")

from app.services.transformation_service import TransformationService

class DummyRagService:
    async def retrieve_relevant_context(self, query: str, source_ids=None, k=5):
        return ["dummy context"]

class DummySourceService:
    async def get_source(self, source_id: str):
        class Source:
            filename = "file.txt"
            file_type = "text"
            chunk_count = 1
            upload_date = __import__('datetime').datetime.utcnow()
        return Source()

    async def get_full_content(self, source_id: str):
        return "full content"

class DummyLLMClient:
    async def generate_response(self, prompt: str, system_prompt: str, **kwargs):
        return "generated response"

@pytest.mark.asyncio
async def test_get_system_prompt_text():
    service = TransformationService(DummyRagService(), DummySourceService(), DummyLLMClient())
    prompt = service._get_system_prompt("text")
    assert "helpful assistant" in prompt
