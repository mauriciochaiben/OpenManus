"""LLM Client module - provides compatibility layer for the main LLM class"""


def _import_llm():
    """Lazy import to avoid circular dependencies"""
    from app.llm import LLM

    return LLM


class LLMClient:
    """Wrapper class for LLM to avoid circular import issues"""

    def __new__(cls, *args, **kwargs):
        # Return an instance of the actual LLM class
        LLM = _import_llm()
        return LLM(*args, **kwargs)
