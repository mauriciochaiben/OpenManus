"""
Testes unitários para a classe ToolUserAgent.

Este módulo contém testes abrangentes para o ToolUserAgent, incluindo
mock do ToolRegistry e das ferramentas, além de validação de todas as funcionalidades.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importações
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from unittest.mock import AsyncMock, Mock, patch  # noqa: E402

import pytest  # noqa: E402
pytest.importorskip("openai")

from app.roles.tool_user_agent import ToolUserAgent  # noqa: E402
from app.tool.base import ToolResult  # noqa: E402


class MockTool:
    """Mock tool para testes."""

    def __init__(self, name: str = "mock_tool", should_succeed: bool = True):
        self.name = name
        self.description = f"Mock tool: {name}"
        self.should_succeed = should_succeed

    async def execute(self, **kwargs) -> ToolResult:
        """Mock execute method."""
        if self.should_succeed:
            return ToolResult(output=f"Mock result for {self.name} with args: {kwargs}")
        return ToolResult(error="Mock tool execution failed")


class MockToolRegistry:
    """Mock tool registry para testes."""

    def __init__(self):
        self.tools = {}

    def get_tool(self, tool_name: str):
        """Mock get_tool method."""
        return self.tools.get(tool_name)

    def list_tools(self) -> list[str]:
        """Mock list_tools method."""
        return list(self.tools.keys())

    def is_registered(self, tool_name: str) -> bool:
        """Mock is_registered method."""
        return tool_name in self.tools

    def register_tool(self, tool_name: str, tool_instance):
        """Mock register_tool method."""
        self.tools[tool_name] = tool_instance


class TestToolUserAgent:
    """Classe de teste para ToolUserAgent."""

    def test_tool_user_agent_initialization_default(self):
        """Testa a inicialização do ToolUserAgent sem configuração."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            assert agent.tool_registry is not None
            assert agent.config == {}
            mock_registry_class.assert_called_once()

    def test_tool_user_agent_initialization_with_config(self):
        """Testa a inicialização do ToolUserAgent com configuração personalizada."""
        config = {"timeout": 30, "retry_count": 3, "debug": True}

        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent(config=config)

            assert agent.config == config
            assert agent.tool_registry is not None
            mock_registry_class.assert_called_once()

    def test_get_capabilities(self):
        """Testa se o agente retorna as capacidades corretas."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()
            capabilities = agent.get_capabilities()

            assert capabilities == ["tool_execution"]
            assert isinstance(capabilities, list)

    def test_get_available_tools(self):
        """Testa se o agente retorna as ferramentas disponíveis corretamente."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry.tools = {
                "web_search": MockTool("web_search"),
                "file_reader": MockTool("file_reader"),
                "calculator": MockTool("calculator"),
            }
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()
            available_tools = agent.get_available_tools()

            assert len(available_tools) == 3
            assert "web_search" in available_tools
            assert "file_reader" in available_tools
            assert "calculator" in available_tools

    def test_is_tool_available_existing_tool(self):
        """Testa se o agente verifica corretamente a disponibilidade de ferramenta existente."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry.tools = {"web_search": MockTool("web_search")}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()
            is_available = agent.is_tool_available("web_search")

            assert is_available is True

    def test_is_tool_available_nonexistent_tool(self):
        """Testa se o agente verifica corretamente a disponibilidade de ferramenta inexistente."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry.tools = {}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()
            is_available = agent.is_tool_available("nonexistent_tool")

            assert is_available is False

    @pytest.mark.asyncio
    async def test_run_successful_tool_execution(self):
        """Testa a execução bem-sucedida de uma ferramenta."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = MockTool("web_search", should_succeed=True)
            mock_registry.tools = {"web_search": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "tool_name": "web_search",
                "arguments": {"query": "OpenManus framework"},
            }

            with patch("app.roles.tool_user_agent.logger") as mock_logger:
                result = await agent.run(task_details)

            assert result["success"] is True
            assert result["result"] is not None
            assert "web_search" in result["message"]
            assert "executed successfully" in result["message"]
            assert "tool_name" in result["metadata"]
            assert result["metadata"]["tool_name"] == "web_search"
            assert "execution_time" in result["metadata"]
            assert "arguments_provided" in result["metadata"]
            assert result["metadata"]["arguments_provided"] == ["query"]

            # Verifica se o logger foi chamado
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_run_tool_not_found(self):
        """Testa o comportamento quando a ferramenta não é encontrada."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry.tools = {"existing_tool": MockTool("existing_tool")}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "tool_name": "nonexistent_tool",
                "arguments": {"query": "test"},
            }

            result = await agent.run(task_details)

            assert result["success"] is False
            assert result["result"] is None
            assert "not found in registry" in result["message"]
            assert "nonexistent_tool" in result["message"]
            assert "available_tools" in result["metadata"]
            assert "requested_tool" in result["metadata"]
            assert result["metadata"]["requested_tool"] == "nonexistent_tool"
            assert result["metadata"]["available_tools"] == ["existing_tool"]
            assert result["metadata"]["execution_time"] == 0

    @pytest.mark.asyncio
    async def test_run_tool_execution_failure(self):
        """Testa o comportamento quando a execução da ferramenta falha."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = MockTool("failing_tool", should_succeed=False)
            mock_registry.tools = {"failing_tool": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {"tool_name": "failing_tool", "arguments": {"query": "test"}}

            with patch("app.roles.tool_user_agent.logger"):
                result = await agent.run(task_details)

            assert result["success"] is True  # O MockTool retorna ToolResult, não levanta exceção
            assert result["result"] is not None
            assert result["result"].error == "Mock tool execution failed"

    @pytest.mark.asyncio
    async def test_run_tool_execution_exception(self):
        """Testa o comportamento quando a ferramenta levanta uma exceção."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = Mock()
            mock_tool.execute = AsyncMock(side_effect=RuntimeError("Tool crashed"))
            mock_registry.tools = {"crashing_tool": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "tool_name": "crashing_tool",
                "arguments": {"query": "test"},
            }

            with patch("app.roles.tool_user_agent.logger") as mock_logger:
                result = await agent.run(task_details)

            assert result["success"] is False
            assert result["result"] is None
            assert "execution failed" in result["message"]
            assert "Tool crashed" in result["message"]
            assert "error_type" in result["metadata"]
            assert result["metadata"]["error_type"] == "RuntimeError"
            assert "execution_time" in result["metadata"]

            # Verifica se o erro foi logado
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_run_invalid_task_details_not_dict(self):
        """Testa o comportamento com task_details inválido (não é dict)."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            with patch("app.roles.tool_user_agent.logger") as mock_logger:
                result = await agent.run("invalid_string")

            assert result["success"] is False
            assert result["result"] is None
            assert "task_details must be a dictionary" in result["message"]
            assert "error_type" in result["metadata"]
            assert result["metadata"]["error_type"] == "ValueError"
            assert result["metadata"]["execution_time"] == 0

            # Verifica se o erro foi logado
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_run_missing_tool_name(self):
        """Testa o comportamento quando tool_name está ausente."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "arguments": {"query": "test"}
                # tool_name ausente
            }

            with patch("app.roles.tool_user_agent.logger"):
                result = await agent.run(task_details)

            assert result["success"] is False
            assert result["result"] is None
            assert "tool_name is required" in result["message"]
            assert "error_type" in result["metadata"]
            assert result["metadata"]["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_run_empty_tool_name(self):
        """Testa o comportamento quando tool_name está vazio."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {"tool_name": "", "arguments": {"query": "test"}}

            with patch("app.roles.tool_user_agent.logger"):
                result = await agent.run(task_details)

            assert result["success"] is False
            assert result["result"] is None
            assert "tool_name is required" in result["message"]

    @pytest.mark.asyncio
    async def test_run_invalid_arguments_not_dict(self):
        """Testa o comportamento quando arguments não é um dicionário."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {"tool_name": "web_search", "arguments": "invalid_arguments"}

            with patch("app.roles.tool_user_agent.logger"):
                result = await agent.run(task_details)

            assert result["success"] is False
            assert result["result"] is None
            assert "arguments must be a dictionary" in result["message"]
            assert "error_type" in result["metadata"]
            assert result["metadata"]["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_run_missing_arguments_defaults_to_empty_dict(self):
        """Testa o comportamento quando arguments está ausente (deve usar dict vazio)."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = MockTool("web_search", should_succeed=True)
            mock_registry.tools = {"web_search": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "tool_name": "web_search"
                # arguments ausente, deve usar {}
            }

            with patch("app.roles.tool_user_agent.logger"):
                result = await agent.run(task_details)

            assert result["success"] is True
            assert result["result"] is not None
            assert "executed successfully" in result["message"]
            assert result["metadata"]["arguments_provided"] == []

    @pytest.mark.asyncio
    async def test_run_execution_time_tracking(self):
        """Testa se o tempo de execução é rastreado corretamente."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = MockTool("slow_tool", should_succeed=True)
            mock_registry.tools = {"slow_tool": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {"tool_name": "slow_tool", "arguments": {"query": "test"}}

            # Mock time.time para simular tempo de execução
            with patch("time.time") as mock_time:
                mock_time.side_effect = [0.0, 1.5]  # Start and end time

                result = await agent.run(task_details)

            assert result["success"] is True
            assert "execution_time" in result["metadata"]
            assert result["metadata"]["execution_time"] == 1.5

    @pytest.mark.asyncio
    async def test_run_with_complex_arguments(self):
        """Testa a execução com argumentos complexos."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_tool = MockTool("complex_tool", should_succeed=True)
            mock_registry.tools = {"complex_tool": mock_tool}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            complex_arguments = {
                "query": "OpenManus framework",
                "max_results": 10,
                "filters": {"type": "documentation", "language": "python"},
                "options": ["include_examples", "verbose"],
            }

            task_details = {"tool_name": "complex_tool", "arguments": complex_arguments}

            result = await agent.run(task_details)

            assert result["success"] is True
            assert result["result"] is not None
            expected_args = ["query", "max_results", "filters", "options"]
            assert set(result["metadata"]["arguments_provided"]) == set(expected_args)

    @pytest.mark.asyncio
    async def test_run_unexpected_exception(self):
        """Testa o comportamento com exceção inesperada durante validação."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            # Simula uma exceção inesperada durante a execução
            with patch.object(
                agent.tool_registry,
                "get_tool",
                side_effect=RuntimeError("Unexpected error"),
            ):
                task_details = {
                    "tool_name": "web_search",
                    "arguments": {"query": "test"},
                }

                with patch("app.roles.tool_user_agent.logger") as mock_logger:
                    result = await agent.run(task_details)

                assert result["success"] is False
                assert result["result"] is None
                assert "Unexpected error during tool execution" in result["message"]
                assert "error_type" in result["metadata"]
                assert result["metadata"]["error_type"] == "RuntimeError"
                assert result["metadata"]["execution_time"] == 0

                # Verifica se o erro foi logado
                mock_logger.error.assert_called()

    def test_tool_user_agent_inherits_from_base_agent(self):
        """Testa se ToolUserAgent herda corretamente de BaseAgent."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            # Verifica se tem os métodos abstratos implementados
            assert hasattr(agent, "run")
            assert hasattr(agent, "get_capabilities")
            assert callable(agent.run)
            assert callable(agent.get_capabilities)

    @pytest.mark.asyncio
    async def test_integration_with_web_search_tool_simulation(self):
        """Testa integração simulada com WebSearchTool."""
        with patch("app.roles.tool_user_agent.ToolRegistry") as mock_registry_class:
            mock_registry = MockToolRegistry()

            # Simula WebSearchTool
            mock_web_search = Mock()
            mock_web_search.execute = AsyncMock(
                return_value=ToolResult(output="Search results for 'OpenManus': 1. OpenManus Documentation...")
            )
            mock_registry.tools = {"web_search": mock_web_search}
            mock_registry_class.return_value = mock_registry

            agent = ToolUserAgent()

            task_details = {
                "tool_name": "web_search",
                "arguments": {"query": "OpenManus"},
            }

            result = await agent.run(task_details)

            assert result["success"] is True
            assert result["result"] is not None
            assert result["result"].output is not None
            assert "Search results" in result["result"].output
            assert "OpenManus" in result["result"].output

            # Verifica se o método execute foi chamado com os argumentos corretos
            mock_web_search.execute.assert_called_once_with(query="OpenManus")
