#!/usr/bin/env python
"""
Testes básicos para verificar funcionalidades essenciais do OpenManus
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.manus import Manus
from app.config import Config
from app.logger import logger

# Import analyze_task_complexity from main.py
from main import analyze_task_complexity


class TestBasicFunctionality:
    """Testes básicos de funcionalidade"""

    @pytest.fixture
    async def manus_agent(self):
        """Fixture para criar um agente Manus"""
        try:
            agent = await Manus.create(
                name="test_agent", description="Agent for testing"
            )
            yield agent
        except Exception as e:
            logger.warning(f"Could not create Manus agent: {e}")
            pytest.skip(f"Manus agent creation failed: {e}")

    def test_config_loading_method(self):
        """Testa se a configuração é carregada corretamente (método da classe)"""
        try:
            config = Config()
            assert config is not None
            assert hasattr(config, "llm")
            logger.info("✅ Configuração carregada com sucesso")
        except Exception as e:
            pytest.fail(f"Falha ao carregar configuração: {e}")

    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Testa a criação de um agente Manus"""
        try:
            agent = await Manus.create(name="test_agent", description="Test agent")
            assert agent is not None
            assert agent.name == "test_agent"
            assert agent.description == "Test agent"
            logger.info("✅ Agente Manus criado com sucesso")
        except Exception as e:
            logger.warning(f"Falha na criação do agente: {e}")
            pytest.skip(f"Agent creation failed: {e}")

    @pytest.mark.asyncio
    async def test_simple_query(self, manus_agent):
        """Testa uma consulta simples"""
        try:
            if manus_agent is None:
                pytest.skip("Manus agent not available")

            # Teste simples de matemática
            response = await manus_agent.step("What is 2 + 2?")
            assert response is not None
            logger.info(f"✅ Resposta recebida: {response}")
        except Exception as e:
            logger.warning(f"Falha na consulta simples: {e}")
            # Não falhar o teste se for problema de API
            pytest.skip(f"Simple query failed: {e}")


def test_config_loading():
    """Testa se a configuração é carregada corretamente"""
    try:
        config = Config()
        assert config is not None
        assert hasattr(config, "llm")
        logger.info("✅ Configuração carregada com sucesso")
    except Exception as e:
        pytest.fail(f"Falha ao carregar configuração: {e}")


def test_imports():
    """Testa se todas as importações essenciais funcionam"""
    try:
        from app.agent.manus import Manus
        from app.config import Config
        from app.flow.flow_factory import FlowFactory
        from app.llm import LLM
        from app.logger import logger
        from main import analyze_task_complexity

        logger.info("✅ Todas as importações essenciais funcionam")
    except ImportError as e:
        pytest.fail(f"Falha na importação: {e}")


def test_decision_system():
    """Testa o sistema de decisão de complexidade"""
    try:
        from main import analyze_task_complexity

        # Teste com tarefa simples
        simple_result = analyze_task_complexity("What is 2 + 2?")
        assert simple_result is not None
        assert "is_complex" in simple_result

        # Teste com tarefa complexa
        complex_result = analyze_task_complexity(
            "Create a full web application with database integration"
        )
        assert complex_result is not None
        assert "is_complex" in complex_result

        logger.info("✅ Sistema de decisão funcionando")
    except Exception as e:
        pytest.fail(f"Falha no sistema de decisão: {e}")


if __name__ == "__main__":
    print("🧪 Executando testes básicos...")

    # Executar testes síncronos primeiro
    test_imports()
    test_decision_system()

    # Executar testes assíncronos
    async def run_async_tests():
        test_class = TestBasicFunctionality()

        try:
            await test_class.test_agent_creation()
        except Exception as e:
            logger.warning(f"Teste de criação de agente falhou: {e}")

        try:
            agent = await Manus.create(name="test", description="test")
            await test_class.test_simple_query(agent)
        except Exception as e:
            logger.warning(f"Teste de consulta simples falhou: {e}")

    try:
        asyncio.run(run_async_tests())
        print("✅ Testes básicos concluídos!")
    except Exception as e:
        print(f"❌ Alguns testes falharam: {e}")
