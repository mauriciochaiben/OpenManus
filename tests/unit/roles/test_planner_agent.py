"""
Testes unitários para a classe PlannerAgent.

Este módulo contém testes abrangentes para o PlannerAgent, incluindo
mock das chamadas LLM e validação de todas as funcionalidades.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importações
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from unittest.mock import AsyncMock, patch  # noqa: E402

import pytest  # noqa: E402

from app.roles.planner_agent import PlannerAgent  # noqa: E402


class TestPlannerAgent:
    """Classe de teste para PlannerAgent."""

    def test_planner_agent_initialization_with_config(self):
        """Testa a inicialização do PlannerAgent com configuração personalizada."""
        config = {
            "llm_config": {"model": "gpt-4", "temperature": 0.7},
            "max_steps": 8,
            "planning_strategy": "parallel",
        }

        planner = PlannerAgent(config)

        assert planner.llm_config == config["llm_config"]
        assert planner.max_steps == 8
        assert planner.planning_strategy == "parallel"

    def test_planner_agent_initialization_without_config(self):
        """Testa a inicialização do PlannerAgent sem configuração (valores padrão)."""
        planner = PlannerAgent()

        assert planner.llm_config is None
        assert planner.max_steps == 10
        assert planner.planning_strategy == "sequential"

    def test_planner_agent_initialization_with_empty_config(self):
        """Testa a inicialização do PlannerAgent com configuração vazia."""
        planner = PlannerAgent({})

        assert planner.llm_config is None
        assert planner.max_steps == 10
        assert planner.planning_strategy == "sequential"

    def test_get_capabilities(self):
        """Testa se get_capabilities retorna a lista correta de capacidades."""
        planner = PlannerAgent()
        capabilities = planner.get_capabilities()

        assert isinstance(capabilities, list)
        assert capabilities == ["task_decomposition"]
        assert len(capabilities) == 1

    @pytest.mark.asyncio
    async def test_run_success_with_development_task(self):
        """Testa execução bem-sucedida com tarefa de desenvolvimento."""
        planner = PlannerAgent()

        task_details = {
            "input": "Criar uma API REST para gerenciamento de usuários",
            "context": "Sistema web moderno",
            "complexity": "medium",
        }

        # Mock da função de simulação LLM
        expected_steps = [
            "Passo 1: Analisar os requisitos da tarefa",
            "Passo 2: Definir a arquitetura da solução",
            "Passo 3: Implementar a funcionalidade principal",
            "Passo 4: Criar testes para validação",
            "Passo 5: Documentar a implementação",
        ]

        with patch.object(planner, "_simulate_llm_decomposition", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = expected_steps

            result = await planner.run(task_details)

            # Verificar estrutura do resultado
            assert isinstance(result, dict)
            assert result["status"] == "success"
            assert isinstance(result["steps"], list)
            assert result["steps"] == expected_steps

            # Verificar metadata
            assert "metadata" in result
            metadata = result["metadata"]
            assert metadata["original_task"] == task_details["input"]
            assert metadata["num_steps"] == len(expected_steps)
            assert metadata["planning_strategy"] == "sequential"
            assert metadata["complexity"] == "medium"

            # Verificar que o mock foi chamado
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_success_with_analysis_task(self):
        """Testa execução bem-sucedida com tarefa de análise."""
        planner = PlannerAgent()

        task_details = {
            "input": "Análise de performance do sistema de pagamentos",
            "context": "E-commerce com alto volume",
            "complexity": "high",
        }

        expected_steps = [
            "Passo 1: Coletar os dados necessários",
            "Passo 2: Processar e limpar os dados",
            "Passo 3: Aplicar métodos de análise",
            "Passo 4: Interpretar os resultados",
            "Passo 5: Gerar relatório de conclusões",
        ]

        with patch.object(planner, "_simulate_llm_decomposition", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = expected_steps

            result = await planner.run(task_details)

            assert result["status"] == "success"
            assert result["steps"] == expected_steps
            assert result["metadata"]["complexity"] == "high"

    @pytest.mark.asyncio
    async def test_run_missing_input_field(self):
        """Testa comportamento quando campo 'input' está ausente."""
        planner = PlannerAgent()

        task_details = {"context": "Contexto sem input", "complexity": "medium"}

        result = await planner.run(task_details)

        assert result["status"] == "error"
        assert "Campo 'input'" in result["message"]
        assert result["steps"] == []

    @pytest.mark.asyncio
    async def test_run_empty_input_field(self):
        """Testa comportamento quando campo 'input' está vazio."""
        planner = PlannerAgent()

        task_details = {"input": "", "context": "Contexto válido", "complexity": "low"}

        result = await planner.run(task_details)

        assert result["status"] == "error"
        assert "Campo 'input'" in result["message"]
        assert result["steps"] == []

    @pytest.mark.asyncio
    async def test_run_with_minimal_task_details(self):
        """Testa execução com apenas o campo obrigatório 'input'."""
        planner = PlannerAgent()

        task_details = {"input": "Tarefa simples sem contexto"}

        expected_steps = ["Passo 1: Executar tarefa"]

        with patch.object(planner, "_simulate_llm_decomposition", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = expected_steps

            result = await planner.run(task_details)

            assert result["status"] == "success"
            assert result["steps"] == expected_steps
            assert result["metadata"]["complexity"] == "medium"  # valor padrão

    @pytest.mark.asyncio
    async def test_run_exception_handling(self):
        """Testa tratamento de exceções durante a execução."""
        planner = PlannerAgent()

        task_details = {"input": "Tarefa que gera exceção"}

        # Simular exceção na função de decomposição
        with patch.object(planner, "_simulate_llm_decomposition", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("Erro simulado na decomposição")

            result = await planner.run(task_details)

            assert result["status"] == "error"
            assert "Erro na decomposição da tarefa" in result["message"]
            assert "Erro simulado na decomposição" in result["message"]
            assert result["steps"] == []

    def test_create_decomposition_prompt_with_context(self):
        """Testa criação de prompt com contexto."""
        planner = PlannerAgent()

        task = "Criar API"
        context = "Sistema web"
        complexity = "high"

        prompt = planner._create_decomposition_prompt(task, context, complexity)

        assert "Criar API" in prompt
        assert "Sistema web" in prompt
        assert "high" in prompt
        assert "Máximo de 10 passos" in prompt

    def test_create_decomposition_prompt_without_context(self):
        """Testa criação de prompt sem contexto."""
        planner = PlannerAgent()

        task = "Tarefa simples"
        context = ""
        complexity = "low"

        prompt = planner._create_decomposition_prompt(task, context, complexity)

        assert "Tarefa simples" in prompt
        assert "low" in prompt
        assert "Contexto:" not in prompt  # Não deve incluir contexto vazio

    def test_create_decomposition_prompt_with_custom_max_steps(self):
        """Testa criação de prompt com max_steps personalizado."""
        config = {"max_steps": 5}
        planner = PlannerAgent(config)

        task = "Tarefa teste"
        context = "Contexto teste"
        complexity = "medium"

        prompt = planner._create_decomposition_prompt(task, context, complexity)

        assert "Máximo de 5 passos" in prompt

    @pytest.mark.asyncio
    async def test_simulate_llm_decomposition_development_pattern(self):
        """Testa padrão de decomposição para tarefas de desenvolvimento."""
        planner = PlannerAgent()

        task = "criar nova funcionalidade"
        prompt = "prompt teste"

        steps = await planner._simulate_llm_decomposition(task, prompt)

        assert isinstance(steps, list)
        assert len(steps) == 5
        assert "Analisar os requisitos" in steps[0]
        assert "Definir a arquitetura" in steps[1]
        assert "Implementar a funcionalidade" in steps[2]
        assert "Criar testes" in steps[3]
        assert "Documentar a implementação" in steps[4]

    @pytest.mark.asyncio
    async def test_simulate_llm_decomposition_analysis_pattern(self):
        """Testa padrão de decomposição para tarefas de análise."""
        planner = PlannerAgent()

        task = "análise de dados de vendas"
        prompt = "prompt teste"

        steps = await planner._simulate_llm_decomposition(task, prompt)

        assert isinstance(steps, list)
        assert len(steps) == 5
        assert "Coletar os dados" in steps[0]
        assert "Processar e limpar" in steps[1]
        assert "Aplicar métodos de análise" in steps[2]
        assert "Interpretar os resultados" in steps[3]
        assert "Gerar relatório" in steps[4]

    @pytest.mark.asyncio
    async def test_simulate_llm_decomposition_integration_pattern(self):
        """Testa padrão de decomposição para tarefas de integração."""
        planner = PlannerAgent()

        task = "integrar sistema de pagamento"
        prompt = "prompt teste"

        steps = await planner._simulate_llm_decomposition(task, prompt)

        assert isinstance(steps, list)
        assert len(steps) == 5
        assert "Mapear as interfaces" in steps[0]
        assert "Definir protocolo" in steps[1]
        assert "Implementar adaptadores" in steps[2]
        assert "Testar a integração" in steps[3]
        assert "Validar o funcionamento" in steps[4]

    @pytest.mark.asyncio
    async def test_simulate_llm_decomposition_generic_pattern(self):
        """Testa padrão de decomposição genérico."""
        planner = PlannerAgent()

        task = "tarefa genérica qualquer"
        prompt = "prompt teste"

        steps = await planner._simulate_llm_decomposition(task, prompt)

        assert isinstance(steps, list)
        assert len(steps) == 5
        assert "Entender os requisitos" in steps[0]
        assert "Planejar a abordagem" in steps[1]
        assert "Executar a tarefa" in steps[2]
        assert "Verificar e validar" in steps[3]
        assert "Finalizar e documentar" in steps[4]

    @pytest.mark.asyncio
    async def test_run_with_mock_delay_simulation(self):
        """Testa que a simulação de delay não afeta o resultado."""
        planner = PlannerAgent()

        task_details = {"input": "Tarefa para testar delay"}

        import time

        start_time = time.time()

        result = await planner.run(task_details)

        end_time = time.time()
        execution_time = end_time - start_time

        # Verificar que executou rapidamente (menos de 1 segundo)
        assert execution_time < 1.0
        assert result["status"] == "success"
        assert len(result["steps"]) > 0

    def test_planner_agent_inheritance(self):
        """Testa se PlannerAgent herda corretamente de BaseAgent."""
        from app.agent.base_agent import BaseAgent

        planner = PlannerAgent()

        assert isinstance(planner, BaseAgent)
        assert hasattr(planner, "run")
        assert hasattr(planner, "get_capabilities")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("complexity", ["low", "medium", "high"])
    async def test_run_with_different_complexity_levels(self, complexity):
        """Testa execução com diferentes níveis de complexidade."""
        planner = PlannerAgent()

        task_details = {
            "input": f"Tarefa com complexidade {complexity}",
            "complexity": complexity,
        }

        result = await planner.run(task_details)

        assert result["status"] == "success"
        assert result["metadata"]["complexity"] == complexity

    @pytest.mark.parametrize("strategy", ["sequential", "parallel", "adaptive"])
    def test_initialization_with_different_strategies(self, strategy):
        """Testa inicialização com diferentes estratégias de planejamento."""
        config = {"planning_strategy": strategy}
        planner = PlannerAgent(config)

        assert planner.planning_strategy == strategy


# Fixture para teste de integração (se necessário)
@pytest.fixture
def sample_planner():
    """Fixture que fornece uma instância configurada do PlannerAgent."""
    config = {
        "llm_config": {"model": "test-model"},
        "max_steps": 7,
        "planning_strategy": "test-strategy",
    }
    return PlannerAgent(config)


class TestPlannerAgentIntegration:
    """Testes de integração para PlannerAgent."""

    @pytest.mark.asyncio
    async def test_end_to_end_task_decomposition(self, sample_planner):
        """Teste de integração completo do processo de decomposição."""
        task_details = {
            "input": "Implementar sistema de autenticação completo",
            "context": "Aplicação web com múltiplos tipos de usuário",
            "complexity": "high",
        }

        result = await sample_planner.run(task_details)

        # Verificações completas
        assert result["status"] == "success"
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) > 0
        assert all(isinstance(step, str) for step in result["steps"])

        # Verificar metadata completa
        metadata = result["metadata"]
        assert metadata["original_task"] == task_details["input"]
        assert metadata["planning_strategy"] == "test-strategy"
        assert metadata["complexity"] == "high"
        assert metadata["num_steps"] == len(result["steps"])

    def test_configuration_persistence(self, sample_planner):
        """Testa se a configuração persiste após a inicialização."""
        assert sample_planner.llm_config == {"model": "test-model"}
        assert sample_planner.max_steps == 7
        assert sample_planner.planning_strategy == "test-strategy"
        assert sample_planner.get_capabilities() == ["task_decomposition"]
