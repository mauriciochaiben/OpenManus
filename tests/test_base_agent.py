"""
Teste para validar a implementação da classe abstrata BaseAgent.

Este teste valida que a nova classe BaseAgent está funcionando corretamente
e que implementações concretas seguem a interface definida.
"""

import asyncio

import pytest
pytest.importorskip("openai")
pytest.importorskip("tiktoken")

from app.agent.base_agent import BaseAgent
from app.agent.example_agent import ExampleAgent
from app.logger import logger


class TestBaseAgent:
    """Classe de testes para validar a implementação da BaseAgent abstrata."""

    def test_base_agent_is_abstract(self):
        """Testa que BaseAgent não pode ser instanciada diretamente."""
        with pytest.raises(TypeError):
            # Deve falhar pois BaseAgent é uma classe abstrata
            BaseAgent()

    def test_example_agent_initialization(self):
        """Testa a inicialização do ExampleAgent."""
        # Teste sem configuração
        agent = ExampleAgent()
        assert agent.name == "ExampleAgent"
        assert agent.timeout == 30
        assert agent.debug is False

        # Teste com configuração personalizada
        config = {"name": "TestAgent", "timeout": 60, "debug": True}
        agent_with_config = ExampleAgent(config)
        assert agent_with_config.name == "TestAgent"
        assert agent_with_config.timeout == 60
        assert agent_with_config.debug is True

    @pytest.mark.asyncio
    async def test_example_agent_run_success(self):
        """Testa a execução bem-sucedida de uma tarefa."""
        agent = ExampleAgent({"name": "SuccessTestAgent"})

        task_details = {
            "description": "Tarefa de teste simples",
            "parameters": {"input": "dados de teste", "mode": "test"},
        }

        result = await agent.run(task_details)

        # Validações do resultado
        assert result["success"] is True
        assert "result" in result
        assert "message" in result
        assert "metadata" in result

        # Validações dos dados do resultado
        assert result["result"]["processed_description"] == "Tarefa de teste simples"
        assert result["result"]["agent_name"] == "SuccessTestAgent"
        assert result["result"]["status"] == "completed"

        # Validações dos metadados
        assert "capabilities_used" in result["metadata"]
        assert "agent_config" in result["metadata"]

    @pytest.mark.asyncio
    async def test_example_agent_run_with_empty_task(self):
        """Testa a execução com tarefa vazia."""
        agent = ExampleAgent()

        # Tarefa vazia
        task_details = {}

        result = await agent.run(task_details)

        # Deve executar com sucesso mesmo com tarefa vazia
        assert result["success"] is True
        assert result["result"]["processed_description"] == "No description provided"

    def test_example_agent_capabilities(self):
        """Testa se as capacidades são retornadas corretamente."""
        agent = ExampleAgent()
        capabilities = agent.get_capabilities()

        # Verifica se é uma lista
        assert isinstance(capabilities, list)

        # Verifica se contém as capacidades esperadas
        expected_capabilities = [
            "task_processing",
            "result_formatting",
            "configuration_support",
            "error_handling",
            "logging_integration",
            "demo_execution",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities

    def test_abstract_methods_implementation(self):
        """Testa se todos os métodos abstratos foram implementados."""
        agent = ExampleAgent()

        # Verifica se os métodos abstratos estão implementados
        assert hasattr(agent, "run")
        assert callable(agent.run)
        assert hasattr(agent, "get_capabilities")
        assert callable(agent.get_capabilities)

        # Verifica se __init__ foi implementado (implicitamente testado na criação)
        assert agent is not None


async def run_base_agent_tests():
    """Executa os testes da BaseAgent abstrata."""
    print("🧪 Executando testes da BaseAgent abstrata...")

    test_class = TestBaseAgent()

    try:
        # Testes síncronos
        print("📝 Testando que BaseAgent é abstrata...")
        test_class.test_base_agent_is_abstract()
        print("✅ BaseAgent é corretamente abstrata")

        print("📝 Testando inicialização do ExampleAgent...")
        test_class.test_example_agent_initialization()
        print("✅ Inicialização funcionando corretamente")

        print("📝 Testando capacidades do agente...")
        test_class.test_example_agent_capabilities()
        print("✅ Capacidades retornadas corretamente")

        print("📝 Testando implementação dos métodos abstratos...")
        test_class.test_abstract_methods_implementation()
        print("✅ Métodos abstratos implementados corretamente")

        # Testes assíncronos
        print("📝 Testando execução bem-sucedida...")
        await test_class.test_example_agent_run_success()
        print("✅ Execução bem-sucedida funcionando")

        print("📝 Testando execução com tarefa vazia...")
        await test_class.test_example_agent_run_with_empty_task()
        print("✅ Execução com tarefa vazia funcionando")

        print("🎉 Todos os testes da BaseAgent passaram!")
        return True

    except Exception as e:
        print(f"❌ Erro nos testes da BaseAgent: {e}")
        logger.error(f"Falha nos testes da BaseAgent: {e}")
        return False


if __name__ == "__main__":
    """Executa os testes quando o script é chamado diretamente."""
    print("🚀 Iniciando validação da BaseAgent abstrata...")

    async def main():
        success = await run_base_agent_tests()
        if success:
            print("✨ Validação concluída com sucesso!")
        else:
            print("💥 Validação falhou!")
            exit(1)

    asyncio.run(main())
