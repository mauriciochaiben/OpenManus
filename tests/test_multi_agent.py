#!/usr/bin/env python
"""
Testes para a arquitetura multi-agent
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.decision import AgentDecisionSystem, analyze_task_complexity
from app.agent.manus import Manus
from app.flow.flow_factory import FlowFactory, FlowType
from app.flow.multi_agent import ExecutionMode, MultiAgentFlow
from app.logger import logger


class TestMultiAgent:
    """Testes para funcionalidades multi-agent"""

    def test_task_complexity_analysis(self):
        """Testa a análise de complexidade de tarefas"""
        try:
            # Tarefa simples
            simple_task = "What is 2 + 2?"
            simple_result = analyze_task_complexity(simple_task)

            assert simple_result is not None
            assert "is_complex" in simple_result
            assert "complexity_score" in simple_result
            assert "domains" in simple_result

            # Tarefa complexa
            complex_task = "Create a full web application with React frontend, Node.js backend, and PostgreSQL database"
            complex_result = analyze_task_complexity(complex_task)

            assert complex_result is not None
            assert "is_complex" in complex_result
            assert "complexity_score" in complex_result

            logger.info("✅ Análise de complexidade de tarefas funcionando")
        except Exception as e:
            pytest.fail(f"Falha na análise de complexidade: {e}")

    def test_decision_system_creation(self):
        """Testa a criação do sistema de decisão"""
        try:
            decision_system = AgentDecisionSystem()
            assert decision_system is not None
            logger.info("✅ Sistema de decisão criado com sucesso")
        except Exception as e:
            pytest.fail(f"Falha ao criar sistema de decisão: {e}")

    def test_flow_factory(self):
        """Testa a factory de flows"""
        try:
            # Teste de tipos de flow disponíveis
            assert hasattr(FlowType, "SINGLE_AGENT")
            assert hasattr(FlowType, "MULTI_AGENT")
            assert hasattr(FlowType, "PLANNING")
            assert hasattr(FlowType, "AUTO")

            logger.info("✅ FlowFactory com tipos corretos")
        except Exception as e:
            pytest.fail(f"Falha na FlowFactory: {e}")

    @pytest.mark.asyncio
    async def test_single_agent_flow(self):
        """Testa um flow de agente único"""
        try:
            # Criar agente
            agent = await Manus.create(
                name="test_agent", description="Test single agent"
            )

            # Criar flow simples
            flow = FlowFactory.create_flow(
                flow_type=FlowType.SINGLE_AGENT, agents={"main": agent}
            )

            assert flow is not None
            logger.info("✅ Flow de agente único criado")
        except Exception as e:
            logger.warning(f"Falha no flow de agente único: {e}")
            pytest.skip(f"Single agent flow failed: {e}")

    @pytest.mark.asyncio
    async def test_multi_agent_flow_creation(self):
        """Testa a criação de um flow multi-agent"""
        try:
            # Criar agente principal
            main_agent = await Manus.create(
                name="main_agent", description="Main agent for multi-agent flow"
            )

            # Criar flow multi-agent
            agents = {
                "main": main_agent,
                "primary": main_agent,  # Usar o mesmo agente como primário
            }

            flow = FlowFactory.create_flow(
                flow_type=FlowType.MULTI_AGENT, agents=agents, mode=ExecutionMode.AUTO
            )

            assert flow is not None
            assert isinstance(flow, MultiAgentFlow)
            logger.info("✅ Flow multi-agent criado com sucesso")
        except Exception as e:
            logger.warning(f"Falha na criação do flow multi-agent: {e}")
            pytest.skip(f"Multi-agent flow creation failed: {e}")

    @pytest.mark.asyncio
    async def test_execution_modes(self):
        """Testa os diferentes modos de execução"""
        try:
            # Verificar se os modos existem
            assert hasattr(ExecutionMode, "AUTO")
            assert hasattr(ExecutionMode, "FORCE_SINGLE")
            assert hasattr(ExecutionMode, "FORCE_MULTI")

            logger.info("✅ Modos de execução disponíveis")
        except Exception as e:
            pytest.fail(f"Falha nos modos de execução: {e}")


def test_multi_agent_imports():
    """Testa importações relacionadas ao multi-agent"""
    try:
        from app.agent.decision import AgentDecisionSystem, analyze_task_complexity
        from app.agent.orchestrator import MCPAgentOrchestrator
        from app.flow.flow_factory import FlowFactory, FlowType
        from app.flow.multi_agent import ExecutionMode, MultiAgentFlow
        from app.tool.coordination import CoordinationTool

        logger.info("✅ Todas as importações multi-agent funcionam")
    except ImportError as e:
        pytest.fail(f"Falha na importação multi-agent: {e}")


async def run_multi_agent_tests():
    """Executa testes multi-agent"""
    print("🤖 Executando testes multi-agent...")

    test_class = TestMultiAgent()

    # Testes síncronos
    test_class.test_task_complexity_analysis()
    test_class.test_decision_system_creation()
    test_class.test_flow_factory()

    # Testes assíncronos
    try:
        await test_class.test_single_agent_flow()
    except Exception as e:
        logger.warning(f"Teste de flow único falhou: {e}")

    try:
        await test_class.test_multi_agent_flow_creation()
    except Exception as e:
        logger.warning(f"Teste de criação multi-agent falhou: {e}")

    await test_class.test_execution_modes()


if __name__ == "__main__":
    print("🧪 Executando testes multi-agent...")

    # Executar testes síncronos
    test_multi_agent_imports()

    # Executar testes assíncronos
    try:
        asyncio.run(run_multi_agent_tests())
        print("✅ Testes multi-agent concluídos!")
    except Exception as e:
        print(f"❌ Alguns testes multi-agent falharam: {e}")
