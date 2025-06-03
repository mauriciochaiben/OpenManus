"""
Demonstração da implementação da BaseAgent abstrata no OpenManus.

Este script demonstra como a nova classe BaseAgent pode ser usada
para criar agentes especializados seguindo a arquitetura do projeto.
"""

from abc import ABC, abstractmethod


# Nossa implementação da BaseAgent (copiada para demonstração)
class BaseAgent(ABC):
    """Classe abstrata base para todos os agentes do OpenManus."""

    @abstractmethod
    def __init__(self, config: dict | None = None) -> None:
        """Inicializa o agente com configurações opcionais."""
        pass

    @abstractmethod
    async def run(self, task_details: dict) -> dict:
        """Executa uma tarefa específica de forma assíncrona."""
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Retorna uma lista das capacidades do agente."""
        pass


# Exemplo de implementação concreta
class CalculatorAgent(BaseAgent):
    """Agente especializado em cálculos matemáticos."""

    def __init__(self, config: dict | None = None) -> None:
        """Inicializa o agente calculadora."""
        self.config = config or {}
        self.name = self.config.get("name", "CalculatorAgent")
        self.precision = self.config.get("precision", 10)
        print(f"🧮 {self.name} inicializado com precisão {self.precision}")

    async def run(self, task_details: dict) -> dict:
        """Executa cálculos matemáticos."""
        try:
            operation = task_details.get("operation", "")
            numbers = task_details.get("numbers", [])

            if operation == "sum":
                result = sum(numbers)
            elif operation == "multiply":
                result = 1
                for num in numbers:
                    result *= num
            elif operation == "average":
                result = sum(numbers) / len(numbers) if numbers else 0
            else:
                raise ValueError(f"Operação não suportada: {operation}")

            return {
                "success": True,
                "result": round(result, self.precision),
                "message": f"Operação {operation} executada com sucesso",
                "metadata": {
                    "operation": operation,
                    "input_numbers": numbers,
                    "agent": self.name,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "result": None,
                "message": f"Erro no cálculo: {str(e)}",
                "metadata": {"error_type": type(e).__name__, "agent": self.name},
            }

    def get_capabilities(self) -> list[str]:
        """Retorna as capacidades do agente calculadora."""
        return [
            "mathematical_operations",
            "sum_calculation",
            "multiplication",
            "average_calculation",
            "precision_control",
        ]


# Exemplo de uso da arquitetura
async def demonstrate_base_agent():
    """Demonstra o uso da BaseAgent abstrata."""
    print("🚀 Demonstração da BaseAgent do OpenManus")
    print("=" * 50)

    # 1. Tentar instanciar BaseAgent diretamente (deve falhar)
    print("\n1️⃣ Testando que BaseAgent é abstrata...")
    try:
        BaseAgent()
        print("❌ ERRO: BaseAgent deveria ser abstrata!")
    except TypeError:
        print("✅ BaseAgent é corretamente abstrata")

    # 2. Criar implementação concreta
    print("\n2️⃣ Criando agente especializado...")
    config = {"name": "SuperCalculator", "precision": 3}
    calc_agent = CalculatorAgent(config)

    # 3. Verificar capacidades
    print("\n3️⃣ Verificando capacidades...")
    capabilities = calc_agent.get_capabilities()
    print(f"✅ Capacidades: {len(capabilities)} itens")
    for cap in capabilities:
        print(f"   • {cap}")

    # 4. Executar tarefas
    print("\n4️⃣ Executando tarefas...")

    # Tarefa de soma
    soma_task = {"operation": "sum", "numbers": [10, 20, 30, 40]}
    resultado_soma = await calc_agent.run(soma_task)
    print(f"✅ Soma: {resultado_soma['result']} (sucesso: {resultado_soma['success']})")

    # Tarefa de média
    media_task = {"operation": "average", "numbers": [100, 200, 300]}
    resultado_media = await calc_agent.run(media_task)
    print(
        f"✅ Média: {resultado_media['result']} (sucesso: {resultado_media['success']})"
    )

    # Tarefa com erro
    erro_task = {"operation": "division", "numbers": [10, 2]}  # operação não suportada
    resultado_erro = await calc_agent.run(erro_task)
    print(f"✅ Erro tratado: {resultado_erro['success']} - {resultado_erro['message']}")

    print("\n🎉 Demonstração concluída com sucesso!")
    print("\n📋 Resumo da implementação:")
    print("   ✅ Classe abstrata BaseAgent criada")
    print("   ✅ Métodos abstratos implementados (__init__, run, get_capabilities)")
    print("   ✅ Type hints aplicados")
    print("   ✅ Docstrings no formato Google Style")
    print("   ✅ Exemplo de agente concreto funcional")
    print("   ✅ Tratamento de erros implementado")
    print("   ✅ Arquitetura compatível com OpenManus")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demonstrate_base_agent())
