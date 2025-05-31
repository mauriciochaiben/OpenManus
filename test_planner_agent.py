#!/usr/bin/env python3
"""
Teste simples para validar a implementação do PlannerAgent.

Este script testa a criação e funcionamento básico do PlannerAgent,
verificando se herda corretamente da BaseAgent e implementa os métodos necessários.
"""

import asyncio
import os
import sys

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.roles.planner_agent import PlannerAgent


async def test_planner_agent():
    """Testa a funcionalidade básica do PlannerAgent."""
    print("🧠 Teste do PlannerAgent")
    print("=" * 50)

    # Teste 1: Criação do agente
    print("\n1️⃣ Criando PlannerAgent...")
    config = {
        "llm_config": {"model": "gpt-4", "temperature": 0.7},
        "max_steps": 8,
        "planning_strategy": "sequential",
    }
    planner = PlannerAgent(config)
    print("✅ PlannerAgent criado com sucesso")

    # Teste 2: Verificar capacidades
    print("\n2️⃣ Verificando capacidades...")
    capabilities = planner.get_capabilities()
    print(f"✅ Capacidades: {capabilities}")
    assert (
        "task_decomposition" in capabilities
    ), "Capacidade 'task_decomposition' não encontrada"

    # Teste 3: Testar decomposição de tarefa de desenvolvimento
    print("\n3️⃣ Testando decomposição de tarefa de desenvolvimento...")
    task_details = {
        "input": "Criar uma API REST para gerenciamento de usuários",
        "context": "Sistema web com autenticação JWT",
        "complexity": "medium",
    }

    result = await planner.run(task_details)
    print(f"Status: {result['status']}")
    print(f"Número de passos: {len(result['steps'])}")
    print("Passos decompostos:")
    for i, step in enumerate(result["steps"], 1):
        print(f"  {i}. {step}")

    assert result["status"] == "success", "Decomposição falhou"
    assert len(result["steps"]) > 0, "Nenhum passo foi gerado"

    # Teste 4: Testar decomposição de tarefa de análise
    print("\n4️⃣ Testando decomposição de tarefa de análise...")
    task_details = {
        "input": "Análise de performance do sistema de pagamentos",
        "context": "E-commerce com alto volume de transações",
        "complexity": "high",
    }

    result = await planner.run(task_details)
    print(f"Status: {result['status']}")
    print(f"Número de passos: {len(result['steps'])}")
    print("Passos decompostos:")
    for i, step in enumerate(result["steps"], 1):
        print(f"  {i}. {step}")

    # Teste 5: Testar tratamento de erro
    print("\n5️⃣ Testando tratamento de erro...")
    task_details = {}  # Sem campo 'input'

    result = await planner.run(task_details)
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")

    assert result["status"] == "error", "Erro não foi tratado corretamente"

    print("\n🎉 Todos os testes passaram!")
    print("✅ PlannerAgent está funcionando corretamente")


if __name__ == "__main__":
    asyncio.run(test_planner_agent())
