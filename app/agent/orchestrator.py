"""
Orquestrador de agentes MCP especializados
"""

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.agent.decision import AgentApproach, AgentDecisionSystem, TaskAnalysis
from app.agent.manus import Manus
from app.agent.mcp import MCPAgent
from app.infrastructure.messaging.progress_broadcaster import progress_broadcaster
from app.logger import logger

if TYPE_CHECKING:
    from app.agent.base import BaseAgent


@dataclass
class Task:
    """Representação de uma tarefa"""

    description: str
    priority: int = 1
    dependencies: list[str] = None
    assigned_agent: str | None = None
    status: str = "pending"  # pending, running, completed, failed
    result: str | None = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class MCPToolRouter:
    """Roteador inteligente que distribui ferramentas MCP entre agentes"""

    def __init__(self):
        self.tool_specializations = {
            "bash": ["system", "development"],
            "browser": ["browser_automation", "research"],
            "editor": ["development", "document_processing"],
            "python": ["development", "data_analysis"],
            "search": ["research"],
            "document_reader": ["document_processing", "research"],
            "planning": ["all"],  # Planning disponível para todos
        }

        # Mapeamento de especializações para tipos de agente
        self.specialization_agents = {
            "development": "code",
            "research": "research",
            "data_analysis": "analysis",
            "browser_automation": "browser",
            "system_admin": "system",
            "document_processing": "analysis",
        }

    def get_optimal_agent_for_tool(self, tool_name: str) -> list[str]:
        """Retorna agentes especializados para a ferramenta"""
        specializations = self.tool_specializations.get(tool_name, [])

        if "all" in specializations:
            return list(self.specialization_agents.values())

        agents = []
        for spec in specializations:
            if spec in self.specialization_agents:
                agents.append(self.specialization_agents[spec])

        return agents or ["default"]

    def get_optimal_agent_for_domain(self, domain: str) -> str:
        """Retorna o agente ótimo para um domínio"""
        return self.specialization_agents.get(domain, "default")

    def distribute_mcp_connections(self) -> dict[str, list[str]]:
        """Distribui conexões MCP baseado na especialização"""
        distribution = {}

        for tool, specializations in self.tool_specializations.items():
            for spec in specializations:
                if spec == "all":
                    for agent in self.specialization_agents.values():
                        if agent not in distribution:
                            distribution[agent] = []
                        if tool not in distribution[agent]:
                            distribution[agent].append(tool)
                else:
                    agent = self.specialization_agents.get(spec, "default")
                    if agent not in distribution:
                        distribution[agent] = []
                    if tool not in distribution[agent]:
                        distribution[agent].append(tool)

        return distribution


class MCPAgentOrchestrator:
    """Orquestrador que gerencia múltiplos agentes MCP especializados"""

    def __init__(self):
        self.specialized_agents: dict[str, BaseAgent] = {}
        self.mcp_tool_router = MCPToolRouter()
        self.decision_system = AgentDecisionSystem()
        self.active_tasks: dict[str, Task] = {}
        self.task_counter = 0

        # Configuração padrão de agentes especializados
        self.agent_configs = {
            "code": {
                "class": MCPAgent,
                "specialization": "development",
                "tools": ["bash", "editor", "python"],
                "description": "Specialized in code development and programming tasks",
            },
            "research": {
                "class": MCPAgent,
                "specialization": "research",
                "tools": ["browser", "search", "document_reader"],
                "description": "Specialized in research and information gathering",
            },
            "analysis": {
                "class": MCPAgent,
                "specialization": "data_analysis",
                "tools": ["python", "editor", "document_reader"],
                "description": "Specialized in data analysis and document processing",
            },
            "browser": {
                "class": MCPAgent,
                "specialization": "web_automation",
                "tools": ["browser"],
                "description": "Specialized in browser automation and web interactions",
            },
            "system": {
                "class": MCPAgent,
                "specialization": "system_admin",
                "tools": ["bash"],
                "description": "Specialized in system administration tasks",
            },
            "default": {
                "class": Manus,
                "specialization": "general",
                "tools": ["all"],
                "description": "General purpose agent with access to all tools",
            },
        }

    async def initialize(self):
        """Inicializa todos os agentes especializados"""
        logger.info("Initializing MCP Agent Orchestrator...")

        for agent_id, config in self.agent_configs.items():
            try:
                if config["class"] == Manus:
                    # Usar factory method para Manus
                    agent = await Manus.create()
                else:
                    # Criar agente MCP especializado
                    agent = config["class"]()
                    # Configurar especialização se necessário
                    if hasattr(agent, "specialization"):
                        agent.specialization = config["specialization"]

                self.specialized_agents[agent_id] = agent
                logger.info(f"Initialized {agent_id} agent: {config['description']}")

            except Exception as e:
                logger.error(f"Failed to initialize {agent_id} agent: {e}")
                # Usar agente padrão como fallback
                if agent_id != "default":
                    self.specialized_agents[agent_id] = await Manus.create()

    async def route_task_to_agent(self, task: Task) -> str:
        """Roteia tarefa para o agente mais adequado baseado nas ferramentas MCP necessárias"""
        logger.info(f"Routing task: {task.description[:100]}...")

        # Analisar a tarefa
        analysis = self.decision_system.analyze_task_complexity(task.description)
        approach = self.decision_system.recommend_approach(analysis)

        # Escolher estratégia baseada na abordagem recomendada
        if approach == AgentApproach.SINGLE_AGENT:
            return await self._execute_single_agent(task, analysis)
        if approach == AgentApproach.MULTI_AGENT_SEQUENTIAL:
            return await self._execute_sequential(task, analysis)
        if approach == AgentApproach.MULTI_AGENT_PARALLEL:
            return await self._execute_parallel(task, analysis)
        # MULTI_AGENT_COLLABORATIVE
        return await self._execute_collaborative(task, analysis)

    async def _execute_single_agent(self, task: Task, analysis: TaskAnalysis) -> str:
        """Executa tarefa com um único agente"""
        logger.info("Executing with single agent approach")

        # Broadcast orchestrator single agent start
        await progress_broadcaster.broadcast_progress(
            task_id=f"orch_{hash(task.description) % 10000}",
            stage="Roteando para agente especializado",
            progress=70,
            execution_type="single",
            description="Selecionando e preparando agente especializado",
        )

        # Escolher o melhor agente baseado nos domínios
        agent_id = self._select_best_agent(analysis.domains)
        agent = self.specialized_agents.get(
            agent_id, self.specialized_agents["default"]
        )

        task.assigned_agent = agent_id
        task.status = "running"

        try:
            result = await agent.run(task.description)
            task.status = "completed"
            task.result = result
            logger.info(f"Task completed by {agent_id}")
            return result
        except Exception as e:
            task.status = "failed"
            task.result = f"Error: {str(e)}"
            logger.error(f"Task failed on {agent_id}: {e}")
            return task.result

    async def _execute_sequential(self, task: Task, analysis: TaskAnalysis) -> str:
        """Executa tarefa sequencialmente com múltiplos agentes"""
        logger.info("Executing with multi-agent sequential approach")

        # Broadcast sequential start
        await progress_broadcaster.broadcast_progress(
            task_id=f"orch_{hash(task.description) % 10000}",
            stage="Execução sequencial multi-agente",
            progress=70,
            execution_type="multi",
            description="Dividindo tarefa em etapas sequenciais",
        )

        # Dividir tarefa em subtarefas baseado nos domínios
        subtasks = self._decompose_task(task, analysis)
        results = []

        for i, subtask in enumerate(subtasks):
            # Broadcast current step
            progress = 70 + (i / len(subtasks)) * 15  # 70-85% range
            await progress_broadcaster.broadcast_progress(
                task_id=f"orch_{hash(task.description) % 10000}",
                stage=f"Executando etapa {i+1}/{len(subtasks)}",
                progress=progress,
                execution_type="multi",
                step_number=i + 1,
                total_steps=len(subtasks),
                description=f"Processando: {subtask.description[:50]}...",
            )

            agent_id = subtask.assigned_agent or self._select_best_agent(
                {subtask.description}
            )
            agent = self.specialized_agents.get(
                agent_id, self.specialized_agents["default"]
            )

            logger.info(f"Executing subtask {i+1}/{len(subtasks)} with {agent_id}")

            try:
                # Incluir contexto dos resultados anteriores
                context = (
                    f"Previous results: {'; '.join(results[-2:])}\n" if results else ""
                )
                full_description = f"{context}Current task: {subtask.description}"

                result = await agent.run(full_description)
                results.append(f"Step {i+1}: {result}")
                subtask.status = "completed"
                subtask.result = result

            except Exception as e:
                error_msg = f"Step {i+1} failed: {str(e)}"
                results.append(error_msg)
                subtask.status = "failed"
                logger.error(f"Subtask failed: {e}")

        final_result = "\n\n".join(results)
        task.status = "completed"
        task.result = final_result
        return final_result

    async def _execute_parallel(self, task: Task, analysis: TaskAnalysis) -> str:
        """Executa tarefa em paralelo com múltiplos agentes"""
        logger.info("Executing with multi-agent parallel approach")

        # Broadcast parallel start
        await progress_broadcaster.broadcast_progress(
            task_id=f"orch_{hash(task.description) % 10000}",
            stage="Execução paralela multi-agente",
            progress=70,
            execution_type="multi",
            description="Distribuindo tarefa entre agentes paralelos",
        )

        # Dividir tarefa em subtarefas independentes
        subtasks = self._decompose_task(task, analysis, parallel=True)

        # Broadcast parallel execution
        await progress_broadcaster.broadcast_progress(
            task_id=f"orch_{hash(task.description) % 10000}",
            stage=f"Executando {len(subtasks)} tarefas em paralelo",
            progress=75,
            execution_type="multi",
            agents=[st.assigned_agent for st in subtasks if st.assigned_agent],
            description="Processamento simultâneo por múltiplos agentes",
        )

        # Executar subtarefas em paralelo
        async def execute_subtask(subtask: Task) -> str:
            agent_id = subtask.assigned_agent or self._select_best_agent(
                {subtask.description}
            )
            agent = self.specialized_agents.get(
                agent_id, self.specialized_agents["default"]
            )

            try:
                result = await agent.run(subtask.description)
                subtask.status = "completed"
                subtask.result = result
                return f"{agent_id}: {result}"
            except Exception as e:
                subtask.status = "failed"
                error_msg = f"{agent_id} failed: {str(e)}"
                subtask.result = error_msg
                return error_msg

        # Executar todas as subtarefas em paralelo
        results = await asyncio.gather(
            *[execute_subtask(st) for st in subtasks], return_exceptions=True
        )

        # Combinar resultados
        final_result = "\n\n".join(str(result) for result in results)
        task.status = "completed"
        task.result = final_result
        return final_result

    async def _execute_collaborative(self, task: Task, analysis: TaskAnalysis) -> str:
        """Executa tarefa com colaboração entre agentes"""
        logger.info("Executing with multi-agent collaborative approach")

        # Para colaboração, usar abordagem sequencial com compartilhamento de contexto
        return await self._execute_sequential(task, analysis)

    def _select_best_agent(self, domains) -> str:
        """Seleciona o melhor agente baseado nos domínios da tarefa"""
        if not domains:
            return "default"

        # Contar qual agente é mais adequado para os domínios
        agent_scores = {}
        for domain in domains:
            optimal_agent = self.mcp_tool_router.get_optimal_agent_for_domain(domain)
            agent_scores[optimal_agent] = agent_scores.get(optimal_agent, 0) + 1

        # Retornar agente com maior pontuação
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]
            return best_agent if best_agent in self.specialized_agents else "default"

        return "default"

    def _decompose_task(
        self, task: Task, analysis: TaskAnalysis, parallel: bool = False
    ) -> list[Task]:
        """Decompõe uma tarefa em subtarefas"""
        subtasks = []

        if len(analysis.domains) <= 1:
            # Tarefa simples, não dividir
            return [task]

        # Criar subtarefas baseado nos domínios
        for i, domain in enumerate(analysis.domains):
            subtask_description = f"Handle {domain} aspects of: {task.description}"
            agent_id = self.mcp_tool_router.get_optimal_agent_for_domain(domain)

            subtask = Task(
                description=subtask_description,
                priority=task.priority,
                dependencies=[] if parallel else [f"task_{i-1}"] if i > 0 else [],
                assigned_agent=agent_id,
            )
            subtasks.append(subtask)

        return subtasks

    async def get_agent_status(self) -> dict[str, Any]:
        """Retorna status de todos os agentes"""
        status = {}
        for agent_id, agent in self.specialized_agents.items():
            try:
                agent_status = {
                    "id": agent_id,
                    "type": type(agent).__name__,
                    "active": (
                        hasattr(agent, "state") and agent.state.value
                        if hasattr(agent, "state")
                        else "unknown"
                    ),
                    "tools": (
                        len(agent.available_tools.tools)
                        if hasattr(agent, "available_tools")
                        else 0
                    ),
                }
                status[agent_id] = agent_status
            except Exception as e:
                status[agent_id] = {"error": str(e)}

        return status

    async def cleanup(self):
        """Limpeza de recursos"""
        logger.info("Cleaning up MCP Agent Orchestrator...")
        for agent_id, agent in self.specialized_agents.items():
            try:
                if hasattr(agent, "cleanup"):
                    await agent.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up {agent_id}: {e}")

        self.specialized_agents.clear()
        self.active_tasks.clear()
