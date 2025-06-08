from typing import Any, ClassVar

from app.tool.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """A basic web search tool that simulates search functionality."""

    name: str = "web_search"
    description: str = "Performs a web search for the given query and returns simulated search results"
    parameters: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The search query to execute"}},
        "required": ["query"],
    }

    def _simulate_search(self, query: str) -> str:
        """
        Simulate a web search for the given query.

        Args:
            query (str): The search query to execute

        Returns:
            str: A simulated search result string containing mock search results

        """
        # Simulate search results based on the query
        return f"""Search results for "{query}":

1. Example Article - Best Practices for {query}
   URL: https://example.com/article1
   Description: Comprehensive guide covering the fundamentals and advanced techniques for {query}. Learn from industry experts and practical examples.

2. {query} Documentation - Official Guide
   URL: https://docs.example.com/{query.lower().replace(" ", "-")}
   Description: Official documentation and reference material for {query}. Includes API references, tutorials, and best practices.

3. Stack Overflow - Common {query} Questions
   URL: https://stackoverflow.com/questions/tagged/{query.lower().replace(" ", "-")}
   Description: Community-driven Q&A platform with thousands of questions and answers related to {query}. Find solutions to common problems.

4. GitHub - {query} Open Source Projects
   URL: https://github.com/search?q={query.lower().replace(" ", "+")}
   Description: Discover open source projects, libraries, and tools related to {query}. Contribute to the community or find ready-to-use solutions.

5. Tutorial: Getting Started with {query}
   URL: https://tutorial.example.com/{query.lower().replace(" ", "-")}-guide
   Description: Step-by-step tutorial for beginners to learn {query} from scratch. Includes practical exercises and real-world examples.

Total results found: 5
Search completed successfully."""

    async def execute(self, **kwargs) -> ToolResult:
        """
        Async execute method required by BaseTool.

        Args:
            **kwargs: Keyword arguments containing the query parameter

        Returns:
            ToolResult: Tool execution result containing the search output

        """
        query = kwargs.get("query", "")
        if not query:
            return ToolResult(error="Query parameter is required")

        try:
            result = self._simulate_search(query)
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(error=f"Search execution failed: {e!s}")
