"""
Flow Multi-Agente especializado que aproveita o sistema MCP existente
"""

import json
import time
import uuid
from enum import Enum

from pydantic import Field

from app.agent.base import BaseAgent
from app.agent.decision import AgentApproach, AgentDecisionSystem
from app.agent.orchestrator import MCPAgentOrchestrator, Task
from app.flow.base import BaseFlow
from app.infrastructure.messaging.progress_broadcaster import progress_broadcaster
from app.llm import LLM
from app.logger import logger
from app.schema import Message, ToolChoice
from app.tool.coordination import (
    CoordinationTool,
    DistributedMemoryTool,
    TaskRoutingTool,
)
from app.tool.planning import PlanningTool


class ExecutionMode(Enum):
    """Modos de execução do flow"""

    AUTO = "auto"  # Decisão automática
    FORCE_SINGLE = "force_single"  # Forçar single agent
    FORCE_MULTI = "force_multi"  # Forçar multi-agent


class MultiAgentFlow(BaseFlow):
    """Flow especializado para coordenação multi-agente via MCP"""

    llm: LLM = Field(default_factory=lambda: LLM())
    orchestrator: MCPAgentOrchestrator = Field(default_factory=MCPAgentOrchestrator)
    decision_system: AgentDecisionSystem = Field(default_factory=AgentDecisionSystem)

    # Ferramentas de coordenação
    coordination_tool: CoordinationTool = Field(default_factory=CoordinationTool)
    memory_tool: DistributedMemoryTool = Field(default_factory=DistributedMemoryTool)
    routing_tool: TaskRoutingTool = Field(default_factory=TaskRoutingTool)
    planning_tool: PlanningTool = Field(default_factory=PlanningTool)

    # Configurações
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    max_execution_time: int = 3600  # 1 hora
    enable_planning: bool = True
    enable_coordination: bool = True

    # Estado interno
    active_plan_id: str | None = None
    current_task: Task | None = None
    execution_history: list[dict] = Field(default_factory=list)
    current_task_id: str | None = None  # For progress tracking

    def __init__(
        self, agents: BaseAgent | list[BaseAgent] | dict[str, BaseAgent], **data
    ):
        super().__init__(agents, **data)

        # Configurar execution_mode se fornecido
        if "mode" in data:
            self.execution_mode = ExecutionMode(
                data.pop("mode", ExecutionMode.AUTO.value)
            )

    async def initialize(self):
        """Inicializa o flow e todos os componentes"""
        logger.info("Initializing MultiAgentFlow...")

        # Inicializar orquestrador
        await self.orchestrator.initialize()

        # Registrar agentes do flow no orquestrador se necessário
        for agent_id, agent in self.agents.items():
            if agent_id not in self.orchestrator.specialized_agents:
                self.orchestrator.specialized_agents[agent_id] = agent

        logger.info("MultiAgentFlow initialized successfully")

    async def execute(self, input_text: str) -> str:
        """Execute o flow com a entrada fornecida"""
        start_time = time.time()

        # Generate task ID for progress tracking
        self.current_task_id = f"task_{uuid.uuid4().hex[:8]}"

        try:
            logger.info(f"Starting MultiAgentFlow execution: {input_text[:100]}...")

            # Broadcast initial progress
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Inicializando",
                progress=5,
                execution_type="multi",
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=1,
                total_steps=6,
                description="Inicializando sistema multi-agente",
            )

            # Inicializar se necessário
            if not self.orchestrator.specialized_agents:
                await self.initialize()

            # Broadcast initialization complete
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Analisando tarefa",
                progress=15,
                execution_type="multi",
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=2,
                total_steps=6,
                description="Analisando complexidade e requisitos da tarefa",
            )

            # Criar tarefa
            task = Task(description=input_text, priority=1)
            self.current_task = task

            # Armazenar tarefa na memória distribuída
            if self.enable_coordination:
                await self.memory_tool.execute(
                    operation="store",
                    namespace="tasks",
                    key=f"task_{int(time.time())}",
                    value=input_text,
                )

            # Decidir abordagem de execução
            approach = await self._determine_execution_approach(input_text)
            logger.info(f"Selected execution approach: {approach.value}")

            # Broadcast approach selected
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Selecionando abordagem",
                progress=25,
                execution_type="multi",
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=3,
                total_steps=6,
                description=f"Abordagem selecionada: {approach.value}",
            )

            # Executar baseado na abordagem
            if approach == AgentApproach.SINGLE_AGENT:
                result = await self._execute_single_agent(input_text)
            else:
                result = await self._execute_multi_agent(input_text, approach)

            # Broadcast completion
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Finalizando",
                progress=95,
                execution_type="multi",
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=6,
                total_steps=6,
                description="Consolidando resultados finais",
            )

            # Registrar na história
            execution_record = {
                "timestamp": time.time(),
                "input": input_text,
                "approach": approach.value,
                "result": result[:500] + "..." if len(result) > 500 else result,
                "duration": time.time() - start_time,
            }
            self.execution_history.append(execution_record)

            # Limitar histórico
            if len(self.execution_history) > 10:
                self.execution_history = self.execution_history[-10:]

            # Broadcast final completion
            await progress_broadcaster.broadcast_completion(
                task_id=self.current_task_id, result=result
            )

            logger.info(
                f"MultiAgentFlow execution completed in {time.time() - start_time:.2f}s"
            )
            return result

        except Exception as e:
            logger.error(f"Error in MultiAgentFlow execution: {e}")

            # Broadcast failure
            await progress_broadcaster.broadcast_failure(
                task_id=self.current_task_id, error=str(e)
            )

            return f"Execution failed: {str(e)}"

    async def _determine_execution_approach(self, input_text: str) -> AgentApproach:
        """Determina a abordagem de execução baseada no modo e análise"""

        if self.execution_mode == ExecutionMode.FORCE_SINGLE:
            return AgentApproach.SINGLE_AGENT
        if self.execution_mode == ExecutionMode.FORCE_MULTI:
            return AgentApproach.MULTI_AGENT_SEQUENTIAL

        # Modo AUTO - usar sistema de decisão
        analysis = self.decision_system.analyze_task_complexity(input_text)
        approach = self.decision_system.recommend_approach(analysis)

        # Log da análise
        logger.info(f"Task analysis: {analysis}")
        logger.info(f"Recommended approach: {approach}")

        return approach

    async def _execute_single_agent(self, input_text: str) -> str:
        """Executa com single agent usando o agente primário"""
        logger.info("Executing with single agent")

        # Broadcast single agent start
        await progress_broadcaster.broadcast_progress(
            task_id=self.current_task_id,
            stage="Executando com agente único",
            progress=40,
            execution_type="single",
            agents=["manus"] if self.primary_agent else [],
            task_name=input_text[:50] + "..." if len(input_text) > 50 else input_text,
            step_number=4,
            total_steps=6,
            description="Executando tarefa com agente especializado único",
        )

        if not self.primary_agent:
            return "Error: No primary agent available"

        try:
            # Usar agente primário diretamente
            result = await self.primary_agent.run(input_text)

            # Broadcast single agent completion
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Agente único concluído",
                progress=85,
                execution_type="single",
                agents=["manus"],
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=5,
                total_steps=6,
                description="Execução do agente único finalizada com sucesso",
            )

            # Coordenação opcional
            if self.enable_coordination:
                await self.coordination_tool.execute(
                    action="broadcast",
                    message=f"Single agent execution completed: {result[:100]}...",
                )

            return result

        except Exception as e:
            logger.error(f"Single agent execution failed: {e}")
            return f"Single agent execution failed: {str(e)}"

    async def _execute_multi_agent(
        self, input_text: str, approach: AgentApproach
    ) -> str:
        """Executa com múltiplos agentes usando o orquestrador"""
        logger.info(f"Executing with multi-agent approach: {approach.value}")

        # Broadcast multi-agent start
        available_agents = (
            list(self.orchestrator.specialized_agents.keys())
            if self.orchestrator.specialized_agents
            else ["manus"]
        )
        await progress_broadcaster.broadcast_progress(
            task_id=self.current_task_id,
            stage="Coordenando múltiplos agentes",
            progress=40,
            execution_type="multi",
            agents=available_agents,
            task_name=input_text[:50] + "..." if len(input_text) > 50 else input_text,
            step_number=4,
            total_steps=6,
            description=f"Execução {approach.value} com {len(available_agents)} agente(s)",
        )

        try:
            # Criar tarefa para o orquestrador
            task = Task(description=input_text, priority=1)

            # Se planejamento está habilitado, criar plano primeiro
            if self.enable_planning:
                await progress_broadcaster.broadcast_progress(
                    task_id=self.current_task_id,
                    stage="Criando plano de execução",
                    progress=50,
                    execution_type="multi",
                    agents=available_agents,
                    task_name=(
                        input_text[:50] + "..." if len(input_text) > 50 else input_text
                    ),
                    description="Elaborando estratégia detalhada de execução",
                )
                await self._create_execution_plan(input_text)

            # Broadcast execution phase
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Executando via orquestrador",
                progress=65,
                execution_type="multi",
                agents=available_agents,
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                description="Orquestrando execução entre agentes especializados",
            )

            # Executar via orquestrador
            result = await self.orchestrator.route_task_to_agent(task)

            # Broadcast multi-agent completion
            await progress_broadcaster.broadcast_progress(
                task_id=self.current_task_id,
                stage="Multi-agente concluído",
                progress=85,
                execution_type="multi",
                agents=available_agents,
                task_name=(
                    input_text[:50] + "..." if len(input_text) > 50 else input_text
                ),
                step_number=5,
                total_steps=6,
                description="Execução multi-agente finalizada com sucesso",
            )

            # Coordenação final
            if self.enable_coordination:
                await self.coordination_tool.execute(
                    action="broadcast",
                    message=f"Multi-agent execution completed: {result[:100]}...",
                )

            return result

        except Exception as e:
            logger.error(f"Multi-agent execution failed: {e}")
            return f"Multi-agent execution failed: {str(e)}"

    async def _create_execution_plan(self, input_text: str) -> None:
        """Cria um plano de execução usando a ferramenta de planejamento"""
        try:
            self.active_plan_id = f"plan_{int(time.time())}"

            # Criar plano usando LLM + PlanningTool
            system_message = Message.system_message(
                "You are a planning assistant for multi-agent execution. "
                "Create a detailed, actionable plan that can be executed by specialized agents."
            )

            user_message = Message.user_message(
                f"Create an execution plan for this task: {input_text}"
            )

            # Usar LLM com PlanningTool
            response = await self.llm.ask_tool(
                messages=[user_message],
                system_msgs=[system_message],
                tools=[self.planning_tool.to_param()],
                tool_choice=ToolChoice.AUTO,
            )

            # Processar tool calls se presente
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "planning":
                        args = tool_call.function.arguments
                        if isinstance(args, str):
                            args = json.loads(args)

                        # Garantir que plan_id está correto
                        args["plan_id"] = self.active_plan_id

                        # Executar ferramenta de planejamento
                        await self.planning_tool.execute(**args)

                        logger.info(f"Execution plan created: {self.active_plan_id}")
                        return

            # Fallback: criar plano padrão
            await self.planning_tool.execute(
                command="create",
                plan_id=self.active_plan_id,
                title=f"Execution plan for: {input_text[:50]}",
                steps=[
                    "Analyze task requirements",
                    "Route to appropriate agents",
                    "Execute specialized tasks",
                    "Coordinate results",
                    "Deliver final output",
                ],
            )

        except Exception as e:
            logger.warning(f"Failed to create execution plan: {e}")
            # Continuar sem plano

    async def get_status(self) -> dict:
        """Retorna status detalhado do flow"""
        return {
            "mode": self.execution_mode.value,
            "active_plan": self.active_plan_id,
            "current_task": (
                self.current_task.description if self.current_task else None
            ),
            "agents": await self.orchestrator.get_agent_status(),
            "execution_history": len(self.execution_history),
            "coordination_enabled": self.enable_coordination,
            "planning_enabled": self.enable_planning,
        }

    async def get_execution_history(self) -> list[dict]:
        """Retorna histórico de execuções"""
        return self.execution_history.copy()

    async def set_execution_mode(self, mode: ExecutionMode):
        """Define o modo de execução"""
        self.execution_mode = mode
        logger.info(f"Execution mode set to: {mode.value}")

    async def enable_features(self, planning: bool = None, coordination: bool = None):
        """Habilita/desabilita features"""
        if planning is not None:
            self.enable_planning = planning
            logger.info(f"Planning {'enabled' if planning else 'disabled'}")

        if coordination is not None:
            self.enable_coordination = coordination
            logger.info(f"Coordination {'enabled' if coordination else 'disabled'}")

    async def cleanup(self):
        """Limpeza de recursos"""
        logger.info("Cleaning up MultiAgentFlow...")

        # Cleanup do orquestrador
        await self.orchestrator.cleanup()

        # Cleanup dos agentes do flow
        for agent in self.agents.values():
            try:
                if hasattr(agent, "cleanup"):
                    await agent.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up agent: {e}")

        # Limpar estado
        self.current_task = None
        self.active_plan_id = None
        self.execution_history.clear()

        logger.info("MultiAgentFlow cleanup completed")

    def __del__(self):
        """Destructor para garantir cleanup"""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup())
            else:
                loop.run_until_complete(self.cleanup())
        except Exception:
            pass  # Ignore cleanup errors during destruction
