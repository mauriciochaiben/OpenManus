import json
from typing import TYPE_CHECKING

from app.agent.toolcall import ToolCallAgent
from app.compat import Field, model_validator
from app.logger import logger
from app.prompt.browser import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import Message, ToolChoice
from app.tool import Terminate, ToolCollection

try:
    from app.tool import BrowserUseTool

    BROWSER_USE_AVAILABLE = True
except ImportError:
    BrowserUseTool = None
    BROWSER_USE_AVAILABLE = False

# Avoid circular import if BrowserAgent needs BrowserContextHelper
if TYPE_CHECKING:
    from app.agent.base import BaseAgent  # Or wherever memory is defined


class BrowserContextHelper:
    def __init__(self, agent: "BaseAgent"):
        self.agent = agent
        self._current_base64_image: str | None = None

    async def get_browser_state(self) -> dict | None:
        if not BROWSER_USE_AVAILABLE:
            logger.warning("BrowserUseTool not available - browser_use package not installed")
            return None

        browser_tool_name = "browser_use"  # Default name
        if BrowserUseTool:
            try:
                browser_tool_name = BrowserUseTool().name
            except Exception:
                browser_tool_name = "browser_use"
        browser_tool = self.agent.available_tools.get_tool(browser_tool_name)
        if not browser_tool or not hasattr(browser_tool, "get_current_state"):
            logger.warning("BrowserUseTool not found or doesn't have get_current_state")
            return None
        try:
            result = await browser_tool.get_current_state()
            if result.error:
                logger.debug(f"Browser state error: {result.error}")
                return None
            if hasattr(result, "base64_image") and result.base64_image:
                self._current_base64_image = result.base64_image
            else:
                self._current_base64_image = None
            return json.loads(result.output)
        except Exception as e:
            logger.debug(f"Failed to get browser state: {e!s}")
            return None

    async def format_next_step_prompt(self) -> str:
        """Gets browser state and formats the browser prompt."""
        browser_state = await self.get_browser_state()
        url_info, tabs_info, content_above_info, content_below_info = "", "", "", ""
        results_info = ""  # Or get from agent if needed elsewhere

        if browser_state and not browser_state.get("error"):
            url = browser_state.get("url", "N/A")
            title = browser_state.get("title", "N/A")
            url_info = f"\n   URL: {url}\n   Title: {title}"
            tabs = browser_state.get("tabs", [])
            if tabs:
                tabs_info = f"\n   {len(tabs)} tab(s) available"
            pixels_above = browser_state.get("pixels_above", 0)
            pixels_below = browser_state.get("pixels_below", 0)
            if pixels_above > 0:
                content_above_info = f" ({pixels_above} pixels)"
            if pixels_below > 0:
                content_below_info = f" ({pixels_below} pixels)"

            if self._current_base64_image:
                image_message = Message.user_message(
                    content="Current browser screenshot:",
                    base64_image=self._current_base64_image,
                )
                self.agent.memory.add_message(image_message)
                self._current_base64_image = None  # Consume the image after adding

        return NEXT_STEP_PROMPT.format(
            url_placeholder=url_info,
            tabs_placeholder=tabs_info,
            content_above_placeholder=content_above_info,
            content_below_placeholder=content_below_info,
            results_placeholder=results_info,
        )

    async def cleanup_browser(self):
        if not BROWSER_USE_AVAILABLE:
            return

        browser_tool_name = "browser_use"  # Default name
        if BrowserUseTool:
            try:
                browser_tool_name = BrowserUseTool().name
            except Exception:
                browser_tool_name = "browser_use"
        browser_tool = self.agent.available_tools.get_tool(browser_tool_name)
        if browser_tool and hasattr(browser_tool, "cleanup"):
            await browser_tool.cleanup()


class BrowserAgent(ToolCallAgent):
    """
    A browser agent that uses the browser_use library to control a browser.

    This agent can navigate web pages, interact with elements, fill forms,
    extract content, and perform other browser-based actions to accomplish tasks.
    """

    name: str = "browser"
    description: str = "A browser agent that can control a browser to accomplish tasks"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # Configure the available tools
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(*([BrowserUseTool()] if BROWSER_USE_AVAILABLE else []), Terminate())
    )

    # Use Auto for tool choice to allow both tool usage and free-form responses
    tool_choices: ToolChoice = ToolChoice.AUTO
    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    browser_context_helper: BrowserContextHelper | None = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "BrowserAgent":
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    async def think(self) -> bool:
        """
        Process current state and decide next actions using tools.

        Browser state info is added to the prompt.
        """
        self.next_step_prompt = await self.browser_context_helper.format_next_step_prompt()
        return await super().think()

    async def cleanup(self):
        """Clean up browser agent resources by calling parent cleanup."""
        await self.browser_context_helper.cleanup_browser()
