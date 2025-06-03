# ...existing code...

import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    # ...existing code...

    @classmethod
    def register_default_tools(cls):
        """Register all default tools."""
        from app.tool.code_execution import register_code_execution_tool
        from app.tool.file_manager import register_file_manager_tool
        from app.tool.web_scraper import register_web_scraper_tool

        # Register tools
        register_file_manager_tool()
        register_web_scraper_tool()
        register_code_execution_tool()

        logger.info(f"Registered {len(cls._tools)} default tools")


# ...existing code...
