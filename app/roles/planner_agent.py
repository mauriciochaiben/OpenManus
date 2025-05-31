"""
Agente Planejador para decomposição de tarefas do OpenManus.

Este módulo implementa o PlannerAgent, responsável por decompor tarefas complexas
em uma sequência de passos executáveis menores, facilitando a execução distribuída
por outros agentes especializados.
"""

import asyncio
from typing import Dict, List, Optional

from app.agent.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agente especializado em decomposição e planejamento de tarefas.

    O PlannerAgent recebe uma tarefa complexa e a decompõe em uma sequência
    de passos menores e mais específicos que podem ser executados por outros
    agentes do sistema OpenManus.

    Attributes:
        llm_config: Configuração opcional para o cliente LLM usado na decomposição.
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Inicializa o PlannerAgent com configurações opcionais.

        Args:
            config: Dicionário opcional contendo configurações específicas
                   do agente planejador. Pode incluir:
                   - llm_config: Configurações para o cliente LLM
                   - max_steps: Número máximo de passos na decomposição
                   - planning_strategy: Estratégia de planejamento a usar

        Note:
            Se não fornecido, o agente usará configurações padrão para
            decomposição de tarefas.
        """
        self.llm_config = config.get("llm_config") if config else None
        self.max_steps = config.get("max_steps", 10) if config else 10
        self.planning_strategy = (
            config.get("planning_strategy", "sequential") if config else "sequential"
        )

    async def run(self, task_details: Dict) -> Dict:
        """Executa a decomposição de uma tarefa em passos sequenciais.

        Args:
            task_details: Dicionário contendo os detalhes da tarefa a ser decomposta.
                         Deve incluir:
                         - input: Descrição da tarefa principal a ser decomposta
                         - context: Contexto adicional opcional
                         - complexity: Nível de complexidade esperado (opcional)

        Returns:
            Dict: Resultado da decomposição contendo:
                 - status: "success" se a decomposição foi bem-sucedida
                 - steps: Lista de strings com os passos sequenciais
                 - metadata: Informações sobre o processo de decomposição

        Raises:
            KeyError: Quando 'input' não está presente em task_details.
            Exception: Quando ocorre erro durante a decomposição.
        """
        try:
            # Extrair a descrição da tarefa principal
            main_task = task_details.get("input")
            if not main_task:
                return {
                    "status": "error",
                    "message": "Campo 'input' com a descrição da tarefa é obrigatório",
                    "steps": [],
                }

            # Extrair contexto adicional se disponível
            context = task_details.get("context", "")
            complexity = task_details.get("complexity", "medium")

            # Formular prompt para decomposição (simulado por enquanto)
            prompt = self._create_decomposition_prompt(main_task, context, complexity)

            # Simular chamada ao LLM (será refatorado depois)
            steps = await self._simulate_llm_decomposition(main_task, prompt)

            return {
                "status": "success",
                "steps": steps,
                "metadata": {
                    "original_task": main_task,
                    "num_steps": len(steps),
                    "planning_strategy": self.planning_strategy,
                    "complexity": complexity,
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro na decomposição da tarefa: {str(e)}",
                "steps": [],
            }

    def get_capabilities(self) -> List[str]:
        """Retorna as capacidades do agente planejador.

        Returns:
            List[str]: Lista contendo as capacidades específicas do PlannerAgent:
                      - "task_decomposition": Decomposição de tarefas complexas
        """
        return ["task_decomposition"]

    def _create_decomposition_prompt(
        self, task: str, context: str, complexity: str
    ) -> str:
        """Cria o prompt para decomposição da tarefa pelo LLM.

        Args:
            task: Descrição da tarefa principal
            context: Contexto adicional da tarefa
            complexity: Nível de complexidade (low, medium, high)

        Returns:
            str: Prompt formatado para o LLM
        """
        base_prompt = f"""
        Decompor a seguinte tarefa em passos sequenciais simples e executáveis:

        Tarefa: {task}
        """

        if context:
            base_prompt += f"\nContexto: {context}"

        base_prompt += f"""

        Nível de complexidade: {complexity}
        Máximo de {self.max_steps} passos.

        Retorne uma lista de passos claros e específicos, onde cada passo é uma ação concreta.
        """

        return base_prompt

    async def _simulate_llm_decomposition(self, task: str, prompt: str) -> List[str]:
        """Simula a chamada ao LLM para decomposição da tarefa.

        Args:
            task: Descrição da tarefa original
            prompt: Prompt formatado para o LLM

        Returns:
            List[str]: Lista de passos decompostos (simulados)

        Note:
            Esta é uma implementação temporária. Será substituída por
            integração real com LLM posteriormente.
        """
        # Simular delay de processamento do LLM
        await asyncio.sleep(0.1)

        # Decomposição simulada baseada em padrões comuns
        if "criar" in task.lower() or "develop" in task.lower():
            return [
                "Passo 1: Analisar os requisitos da tarefa",
                "Passo 2: Definir a arquitetura da solução",
                "Passo 3: Implementar a funcionalidade principal",
                "Passo 4: Criar testes para validação",
                "Passo 5: Documentar a implementação",
            ]
        elif "análise" in task.lower() or "analyze" in task.lower():
            return [
                "Passo 1: Coletar os dados necessários",
                "Passo 2: Processar e limpar os dados",
                "Passo 3: Aplicar métodos de análise",
                "Passo 4: Interpretar os resultados",
                "Passo 5: Gerar relatório de conclusões",
            ]
        elif "integrar" in task.lower() or "integrate" in task.lower():
            return [
                "Passo 1: Mapear as interfaces existentes",
                "Passo 2: Definir protocolo de comunicação",
                "Passo 3: Implementar adaptadores necessários",
                "Passo 4: Testar a integração",
                "Passo 5: Validar o funcionamento completo",
            ]
        else:
            # Decomposição genérica
            return [
                "Passo 1: Entender os requisitos da tarefa",
                "Passo 2: Planejar a abordagem de execução",
                "Passo 3: Executar a tarefa principal",
                "Passo 4: Verificar e validar resultados",
                "Passo 5: Finalizar e documentar",
            ]
