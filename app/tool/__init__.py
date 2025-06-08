from app.tool.base import BaseTool
from app.tool.bash import Bash
from app.tool.basic_tools import WebSearchTool
from app.tool.create_chat_completion import CreateChatCompletion
from app.tool.document_analyzer import DocumentAnalyzer
from app.tool.document_reader import DocumentReader
from app.tool.planning import PlanningTool
from app.tool.registry import ToolRegistry, tool_registry
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection
from app.tool.web_search import WebSearch

# Optional imports - only available if dependencies are installed
try:
    from app.tool.browser_use_tool import BrowserUseTool
except ImportError:
    BrowserUseTool = None

# Import tools to trigger registration
from . import code_execution

__all__ = [
    "BaseTool",
    "Bash",
    "CreateChatCompletion",
    "DocumentAnalyzer",
    "DocumentReader",
    "PlanningTool",
    "StrReplaceEditor",
    "Terminate",
    "ToolCollection",
    "ToolRegistry",
    "WebSearch",
    "WebSearchTool",
    "code_execution",  # Module import for registration
    "tool_registry",
]

# Add optional tools to __all__ if available
if BrowserUseTool is not None:
    __all__.append("BrowserUseTool")
