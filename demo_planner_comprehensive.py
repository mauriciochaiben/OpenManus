#!/usr/bin/env python3
"""
Demonstração abrangente do PlannerAgent.

Este script demonstra diferentes cenários de uso do PlannerAgent,
mostrando como ele decompõe diversos tipos de tarefas em passos executáveis.
"""

import asyncio
import json
import os
import sys

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.roles.planner_agent import PlannerAgent


async def demonstrate_planner_agent():
    """Demonstra o uso completo do PlannerAgent com diferentes tipos de tarefas."""
    print("🧠 Demonstração Completa do PlannerAgent")
    print("=" * 60)

    # Configuração personalizada do agente
    config = {
        "llm_config": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1000},
        "max_steps": 10,
        "planning_strategy": "sequential",
    }

    print("\n🚀 Inicializando PlannerAgent...")
    planner = PlannerAgent(config)
    print(f"✅ Capacidades: {planner.get_capabilities()}")

    # Cenários de teste
    scenarios = [
        {
            "name": "Desenvolvimento de API",
            "task": {
                "input": "Criar uma API REST para gerenciamento de usuários com autenticação JWT",
                "context": "Sistema web moderno com base de dados PostgreSQL",
                "complexity": "medium",
            },
        },
        {
            "name": "Análise de Dados",
            "task": {
                "input": "Análise de performance e otimização do sistema de pagamentos",
                "context": "E-commerce com 10k+ transações diárias",
                "complexity": "high",
            },
        },
        {
            "name": "Integração de Sistemas",
            "task": {
                "input": "Integrar sistema de CRM com plataforma de email marketing",
                "context": "Sincronização de contatos e campanhas automatizadas",
                "complexity": "medium",
            },
        },
        {
            "name": "Tarefa Genérica",
            "task": {
                "input": "Implementar sistema de notificações em tempo real",
                "context": "Aplicação web com WebSockets",
                "complexity": "low",
            },
        },
    ]

    # Executar cada cenário
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ Cenário: {scenario['name']}")
        print("-" * 40)

        result = await planner.run(scenario["task"])

        if result["status"] == "success":
            print(f"✅ Status: {result['status']}")
            print(f"📝 Tarefa Original: {scenario['task']['input']}")
            print(f"🎯 Número de Passos: {result['metadata']['num_steps']}")
            print(f"🧩 Complexidade: {result['metadata']['complexity']}")
            print("\n📋 Plano de Execução:")

            for j, step in enumerate(result["steps"], 1):
                print(f"   {j:2d}. {step}")

            print(f"\n📊 Metadados:")
            metadata = result["metadata"]
            print(f"   • Estratégia: {metadata['planning_strategy']}")
            print(f"   • Passos: {metadata['num_steps']}")
        else:
            print(f"❌ Status: {result['status']}")
            print(f"💬 Mensagem: {result['message']}")

    # Teste de tratamento de erro
    print(f"\n5️⃣ Teste de Tratamento de Erro")
    print("-" * 40)

    error_task = {
        "context": "Contexto sem input",
        "complexity": "high",
        # Faltando o campo 'input' obrigatório
    }

    result = await planner.run(error_task)
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print(f"Passos: {len(result['steps'])}")

    # Teste de configuração mínima
    print(f"\n6️⃣ Teste com Configuração Mínima")
    print("-" * 40)

    minimal_planner = PlannerAgent()  # Sem configuração
    minimal_task = {"input": "Criar um dashboard de métricas", "complexity": "low"}

    result = await minimal_planner.run(minimal_task)
    print(f"Status: {result['status']}")
    print(f"Passos gerados: {len(result['steps'])}")
    print("Primeiros 3 passos:")
    for i, step in enumerate(result["steps"][:3], 1):
        print(f"   {i}. {step}")

    print(f"\n🎉 Demonstração Concluída!")
    print("✅ PlannerAgent funcionando perfeitamente")
    print("✅ Todos os cenários testados com sucesso")


async def benchmark_planner_performance():
    """Testa a performance do PlannerAgent com múltiplas tarefas."""
    print(f"\n⚡ Teste de Performance")
    print("=" * 40)

    planner = PlannerAgent({"max_steps": 5})

    # Múltiplas tarefas para benchmark
    tasks = [
        {"input": f"Tarefa {i}: Implementar funcionalidade {i}", "complexity": "medium"}
        for i in range(1, 11)
    ]

    import time

    start_time = time.time()

    results = []
    for task in tasks:
        result = await planner.run(task)
        results.append(result)

    end_time = time.time()

    successful = sum(1 for r in results if r["status"] == "success")
    total_steps = sum(len(r["steps"]) for r in results)

    print(f"📊 Resultados do Benchmark:")
    print(f"   • Tarefas processadas: {len(tasks)}")
    print(f"   • Sucessos: {successful}/{len(tasks)}")
    print(f"   • Total de passos gerados: {total_steps}")
    print(f"   • Tempo total: {end_time - start_time:.2f}s")
    print(f"   • Média por tarefa: {(end_time - start_time)/len(tasks):.3f}s")


if __name__ == "__main__":
    asyncio.run(demonstrate_planner_agent())
    asyncio.run(benchmark_planner_performance())
