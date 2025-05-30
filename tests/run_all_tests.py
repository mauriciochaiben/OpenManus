#!/usr/bin/env python
"""
Suite completa de testes integrados para OpenManus
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import logger


async def test_complete_workflow():
    """Testa um workflow completo do OpenManus"""
    print("🔄 Testando workflow completo...")

    try:
        from app.agent.manus import Manus
        from app.flow.flow_factory import FlowFactory, FlowType
        from app.flow.multi_agent import ExecutionMode
        from app.tool.document_reader import DocumentReader
        from main import analyze_task_complexity

        # 1. Análise de complexidade
        print("📊 Testando análise de complexidade...")
        simple_task = "Calculate 10 + 15"
        analysis = analyze_task_complexity(simple_task)
        print(f"   Tarefa simples - Complexo: {analysis['is_complex']}")

        complex_task = "Create a comprehensive project plan with timeline and resources"
        analysis = analyze_task_complexity(complex_task)
        print(f"   Tarefa complexa - Complexo: {analysis['is_complex']}")

        # 2. Criação de agente
        print("🤖 Criando agente Manus...")
        agent = await Manus.create(
            name="integration_test_agent", description="Agent for integration testing"
        )
        print(f"   Agente criado: {agent.name}")

        # 3. Teste de leitura de documento
        print("📄 Testando leitura de documento...")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Este é um documento de teste para integração.\n")
            f.write("Contém informações importantes para o agente processar.")
            temp_file = f.name

        try:
            reader = DocumentReader()
            result = await reader.execute(file_path=temp_file)
            # DocumentReader returns a string, not a ToolResult object
            if isinstance(result, str) and len(result) > 0:
                if "Error:" not in result:
                    print(f"   Documento lido com sucesso: {len(result)} caracteres")
                else:
                    print(f"   Falha na leitura: {result}")
            else:
                print(f"   Resultado inesperado: {result}")
        finally:
            os.unlink(temp_file)

        # 4. Teste de flow factory
        print("⚡ Testando flow factory...")
        flow = FlowFactory.create_flow(
            flow_type=FlowType.SINGLE_AGENT, agents={"main": agent}
        )
        print(f"   Flow criado: {type(flow).__name__}")

        # 5. Teste multi-agent (se possível)
        print("🔀 Testando multi-agent...")
        try:
            multi_flow = FlowFactory.create_flow(
                flow_type=FlowType.MULTI_AGENT, agents={"main": agent, "primary": agent}
            )
            print(f"   Multi-agent flow criado: {type(multi_flow).__name__}")
        except Exception as e:
            print(f"   Multi-agent flow falhou: {e}")

        print("✅ Workflow completo testado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Falha no workflow completo: {e}")
        return False


def run_all_tests():
    """Executa todos os testes disponíveis"""
    print("🧪 INICIANDO SUITE COMPLETA DE TESTES\n")

    test_results = []

    # 1. Testes básicos
    print("=" * 50)
    print("1. TESTES BÁSICOS")
    print("=" * 50)
    try:
        from tests.test_basic_functionality_fixed import (
            test_config_loading,
            test_decision_system,
            test_imports,
        )

        test_imports()
        test_config_loading()
        test_decision_system()
        print("✅ Testes básicos: PASSOU")
        test_results.append(("Básicos", True))
    except Exception as e:
        print(f"❌ Testes básicos: FALHOU - {e}")
        test_results.append(("Básicos", False))

    # 2. Testes de documentos
    print("\n" + "=" * 50)
    print("2. TESTES DE DOCUMENTOS")
    print("=" * 50)
    try:
        from tests.test_document_reading import test_document_reader_imports

        test_document_reader_imports()
        print("✅ Testes de documentos: PASSOU")
        test_results.append(("Documentos", True))
    except Exception as e:
        print(f"❌ Testes de documentos: FALHOU - {e}")
        test_results.append(("Documentos", False))

    # 3. Testes multi-agent
    print("\n" + "=" * 50)
    print("3. TESTES MULTI-AGENT")
    print("=" * 50)
    try:
        from tests.test_multi_agent_fixed import test_multi_agent_imports

        test_multi_agent_imports()
        print("✅ Testes multi-agent: PASSOU")
        test_results.append(("Multi-Agent", True))
    except Exception as e:
        print(f"❌ Testes multi-agent: FALHOU - {e}")
        test_results.append(("Multi-Agent", False))

    # 4. Teste integrado
    print("\n" + "=" * 50)
    print("4. TESTE INTEGRADO")
    print("=" * 50)
    try:
        result = asyncio.run(test_complete_workflow())
        if result:
            print("✅ Teste integrado: PASSOU")
            test_results.append(("Integrado", True))
        else:
            print("❌ Teste integrado: FALHOU")
            test_results.append(("Integrado", False))
    except Exception as e:
        print(f"❌ Teste integrado: FALHOU - {e}")
        test_results.append(("Integrado", False))

    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)

    for test_name, success in test_results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:15} | {status}")

    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
