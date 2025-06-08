"""
Agente de exemplo demonstrando a implementação da classe BaseAgent abstrata.

Este arquivo serve como exemplo de como implementar um agente seguindo
a interface definida em base_agent.py.
"""

from app.agent.base_agent import BaseAgent
from app.logger import logger


class ExampleAgent(BaseAgent):
    """
    Agente de exemplo que implementa a interface BaseAgent.

    Este agente demonstra como implementar corretamente todos os métodos
    abstratos definidos na classe BaseAgent, seguindo as convenções
    do projeto OpenManus.
    """

    def __init__(self, config: dict | None = None) -> None:
        """
        Inicializa o agente de exemplo.

        Args:
            config: Configurações opcionais para o agente.
                   Pode conter campos como:
                   - name: Nome do agente
                   - timeout: Timeout para operações
                   - debug: Flag para modo debug

        """
        self.config = config or {}
        self.name = self.config.get("name", "ExampleAgent")
        self.timeout = self.config.get("timeout", 30)
        self.debug = self.config.get("debug", False)

        logger.info(f"Inicializando {self.name} com configurações: {self.config}")

    async def run(self, task_details: dict) -> dict:
        """
        Executa uma tarefa de demonstração.

        Args:
            task_details: Detalhes da tarefa a ser executada.

        Returns:
            Dict: Resultado da execução com informações sobre o processamento.

        """
        try:
            task_description = task_details.get("description", "No description provided")
            task_params = task_details.get("parameters", {})

            logger.info(f"{self.name} executando tarefa: {task_description}")

            if self.debug:
                logger.debug(f"Parâmetros da tarefa: {task_params}")

            # Simulação de processamento da tarefa
            # Em um agente real, aqui seria implementada a lógica específica
            result_data = {
                "processed_description": task_description,
                "processed_params": task_params,
                "agent_name": self.name,
                "status": "completed",
            }

            return {
                "success": True,
                "result": result_data,
                "message": f"Tarefa executada com sucesso pelo {self.name}",
                "metadata": {
                    "execution_time": "simulated",
                    "agent_config": self.config,
                    "capabilities_used": ["task_processing", "result_formatting"],
                },
            }

        except Exception as e:
            logger.error(f"Erro durante execução da tarefa no {self.name}: {e!s}")
            return {
                "success": False,
                "result": None,
                "message": f"Erro durante execução: {e!s}",
                "metadata": {"error_type": type(e).__name__, "agent_name": self.name},
            }

    def get_capabilities(self) -> list[str]:
        """
        Retorna as capacidades do agente de exemplo.

        Returns:
            List[str]: Lista das capacidades disponíveis.

        """
        return [
            "task_processing",  # Processamento básico de tarefas
            "result_formatting",  # Formatação de resultados
            "configuration_support",  # Suporte a configurações personalizadas
            "error_handling",  # Tratamento de erros
            "logging_integration",  # Integração com sistema de logs
            "demo_execution",  # Execução de demonstrações
        ]
