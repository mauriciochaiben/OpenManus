from app.agent.base import BaseAgent
from app.agent.base_agent import BaseAgent as AbstractBaseAgent

try:
    from app.agent.browser import BrowserAgent
    from app.agent.mcp import MCPAgent
    from app.agent.react import ReActAgent
    from app.agent.swe import SWEAgent
    from app.agent.toolcall import ToolCallAgent
except Exception:  # pragma: no cover - optional dependency missing
    BrowserAgent = MCPAgent = ReActAgent = SWEAgent = ToolCallAgent = None

__all__ = [
    "BaseAgent",
    "AbstractBaseAgent",
    "BrowserAgent",
    "ReActAgent",
    "SWEAgent",
    "ToolCallAgent",
    "MCPAgent",
]
