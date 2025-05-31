"""
Teste simples para validar a BaseAgent abstrata.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class SimpleBaseAgent(ABC):
    """Versão simplificada da BaseAgent para teste."""

    @abstractmethod
    def __init__(self, config: Optional[Dict] = None) -> None:
        pass

    @abstractmethod
    async def run(self, task_details: Dict) -> Dict:
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass


class SimpleExampleAgent(SimpleBaseAgent):
    """Implementação simples para teste."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.name = self.config.get("name", "SimpleAgent")

    async def run(self, task_details: Dict) -> Dict:
        return {
            "success": True,
            "result": f"Processado: {task_details.get('description', 'N/A')}",
            "message": "Sucesso",
            "metadata": {"agent": self.name},
        }

    def get_capabilities(self) -> List[str]:
        return ["test_capability", "simple_processing"]


async def test_simple_implementation():
    """Testa a implementação simples."""
    print("🧪 Testando implementação simples...")

    # Teste 1: BaseAgent é abstrata
    try:
        SimpleBaseAgent()
        print("❌ SimpleBaseAgent deveria ser abstrata!")
    except TypeError:
        print("✅ SimpleBaseAgent é corretamente abstrata")

    # Teste 2: ExampleAgent funciona
    try:
        agent = SimpleExampleAgent({"name": "TestAgent"})
        print(f"✅ SimpleExampleAgent criado: {agent.name}")

        # Teste 3: Capacidades
        caps = agent.get_capabilities()
        print(f"✅ Capacidades: {caps}")

        # Teste 4: Execução
        result = await agent.run({"description": "teste"})
        print(f"✅ Execução: {result['success']}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_implementation())
