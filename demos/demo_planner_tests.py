#!/usr/bin/env python3
"""
Script de demonstração dos testes unitários do PlannerAgent.

Este script executa os testes e demonstra como eles validam
a funcionalidade do PlannerAgent usando mocks e pytest.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_tests():
    """Executa os testes do PlannerAgent com relatório detalhado."""

    print("🧪 Demonstração dos Testes Unitários do PlannerAgent")
    print("=" * 60)

    print("\n📋 Executando suite completa de testes...")
    print("-" * 40)

    # Definir comando de teste
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/roles/test_planner_agent.py",
        "-v",
        "--tb=short",
        "--no-header",
    ]

    # Configurar ambiente
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    try:
        # Executar testes
        result = subprocess.run(
            test_command,
            cwd="/Users/mauriciochaiben/OpenManus",
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

        print("📊 Resultado dos Testes:")
        print(f"   • Código de retorno: {result.returncode}")

        if result.returncode == 0:
            print("   • Status: ✅ SUCESSO")
        else:
            print("   • Status: ❌ FALHA")

        # Mostrar saída dos testes
        if result.stdout:
            print("\n📝 Saída dos Testes:")
            print("-" * 30)
            lines = result.stdout.split("\n")
            for line in lines:
                if "PASSED" in line:
                    print(f"   ✅ {line.strip()}")
                elif "FAILED" in line:
                    print(f"   ❌ {line.strip()}")
                elif "=====" in line and "passed" in line:
                    print(f"   🎉 {line.strip()}")

        if result.stderr and result.returncode != 0:
            print("\n⚠️ Erros:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("⏰ Timeout: Testes demoram mais que 60 segundos")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")


def show_test_structure():
    """Mostra a estrutura dos testes implementados."""

    print("\n🏗️ Estrutura dos Testes Implementados:")
    print("-" * 40)

    test_categories = {
        "Inicialização": [
            "test_planner_agent_initialization_with_config",
            "test_planner_agent_initialization_without_config",
            "test_planner_agent_initialization_with_empty_config",
        ],
        "Capacidades": ["test_get_capabilities"],
        "Método run()": [
            "test_run_success_with_development_task",
            "test_run_success_with_analysis_task",
            "test_run_missing_input_field",
            "test_run_empty_input_field",
            "test_run_with_minimal_task_details",
            "test_run_exception_handling",
            "test_run_with_different_complexity_levels",
        ],
        "Métodos Internos": [
            "test_create_decomposition_prompt_with_context",
            "test_create_decomposition_prompt_without_context",
            "test_simulate_llm_decomposition_*_pattern",
        ],
        "Integração": [
            "test_end_to_end_task_decomposition",
            "test_configuration_persistence",
            "test_planner_agent_inheritance",
        ],
    }

    for category, tests in test_categories.items():
        print(f"\n   🎯 {category}:")
        for test in tests:
            print(f"      • {test}")


def show_mock_example():
    """Mostra exemplo de como os mocks são usados nos testes."""

    print("\n🎭 Exemplo de Mock Implementation:")
    print("-" * 40)

    mock_example = """
@pytest.mark.asyncio
async def test_run_success_with_development_task(self):
    planner = PlannerAgent()

    task_details = {
        "input": "Criar uma API REST",
        "context": "Sistema web moderno",
        "complexity": "medium"
    }

    expected_steps = [
        "Passo 1: Analisar os requisitos",
        "Passo 2: Definir a arquitetura",
        "Passo 3: Implementar funcionalidade"
    ]

    # Mock da função LLM
    with patch.object(planner, '_simulate_llm_decomposition',
                      new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = expected_steps

        result = await planner.run(task_details)

        # Validações
        assert result["status"] == "success"
        assert result["steps"] == expected_steps
        assert mock_llm.called
    """

    print(mock_example)


def show_benefits():
    """Mostra os benefícios da implementação de testes."""

    print("\n🌟 Benefícios dos Testes Implementados:")
    print("-" * 40)

    benefits = [
        "✅ Validação automática de funcionalidades",
        "✅ Detecção precoce de regressões",
        "✅ Documentação viva do comportamento esperado",
        "✅ Facilita refatoração com segurança",
        "✅ Mock de dependências externas (LLM)",
        "✅ Cobertura completa de cenários de uso",
        "✅ Integração com CI/CD pipeline",
        "✅ Base para testes de outros agentes",
    ]

    for benefit in benefits:
        print(f"   {benefit}")


def main():
    """Função principal da demonstração."""

    # Verificar se estamos no diretório correto
    if not Path("app/roles/planner_agent.py").exists():
        print("❌ Execute este script no diretório raiz do OpenManus")
        return

    # Executar demonstração
    run_tests()
    show_test_structure()
    show_mock_example()
    show_benefits()

    print("\n🎉 Demonstração Concluída!")
    print("📋 Para executar os testes manualmente:")
    print("   cd /Users/mauriciochaiben/OpenManus")
    print("   PYTHONPATH=. python -m pytest tests/unit/roles/test_planner_agent.py -v")


if __name__ == "__main__":
    main()
