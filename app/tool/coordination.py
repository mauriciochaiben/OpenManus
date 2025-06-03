"""
Ferramentas MCP especializadas para coordenação multi-agente
"""

import json
import uuid
from datetime import datetime
from typing import Any

from app.logger import logger
from app.tool.base import BaseTool, ToolResult


class CoordinationTool(BaseTool):
    """Ferramenta MCP para coordenação entre agentes"""

    name: str = "coordination"
    description: str = "Coordena ações entre múltiplos agentes"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "send_message",
                    "broadcast",
                    "request_status",
                    "delegate_task",
                    "sync_state",
                ],
                "description": "Ação de coordenação a ser executada",
            },
            "target_agent": {
                "type": "string",
                "description": "ID do agente alvo (opcional para broadcast)",
            },
            "message": {
                "type": "string",
                "description": "Mensagem ou dados a serem enviados",
            },
            "task_data": {
                "type": "object",
                "description": "Dados da tarefa para delegação",
                "properties": {
                    "description": {"type": "string"},
                    "priority": {"type": "integer", "default": 1},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "required": ["action"],
    }

    # Campos de estado como atributos de classe
    message_queue: dict[str, list[dict]] = {}
    agent_registry: dict[str, dict] = {}
    task_delegations: dict[str, dict] = {}

    def __init__(self):
        super().__init__()
        # Inicializar state se necessário
        if not hasattr(self.__class__, "_initialized"):
            self.__class__.message_queue = {}
            self.__class__.agent_registry = {}
            self.__class__.task_delegations = {}
            self.__class__._initialized = True

    async def execute(
        self,
        action: str,
        target_agent: str = None,
        message: str = None,
        task_data: dict = None,
    ) -> ToolResult:
        """Implementa comunicação inter-agentes via MCP"""

        try:
            if action == "send_message":
                return await self._send_message(target_agent, message)
            if action == "broadcast":
                return await self._broadcast_message(message)
            if action == "request_status":
                return await self._request_status(target_agent)
            if action == "delegate_task":
                return await self._delegate_task(target_agent, task_data)
            if action == "sync_state":
                return await self._sync_state(target_agent, message)
            return ToolResult(error=f"Unknown coordination action: {action}")

        except Exception as e:
            logger.error(f"Error in coordination tool: {e}")
            return ToolResult(error=f"Coordination error: {str(e)}")

    async def _send_message(self, target_agent: str, message: str) -> ToolResult:
        """Envia mensagem para um agente específico"""
        if not target_agent or not message:
            return ToolResult(error="Target agent and message are required")

        msg_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "sender": "coordination_system",
        }

        if target_agent not in self.message_queue:
            self.message_queue[target_agent] = []

        self.message_queue[target_agent].append(msg_data)

        logger.info(f"Message sent to {target_agent}: {message[:50]}...")
        return ToolResult(output=f"Message sent to {target_agent} successfully")

    async def _broadcast_message(self, message: str) -> ToolResult:
        """Envia mensagem para todos os agentes registrados"""
        if not message:
            return ToolResult(error="Message is required for broadcast")

        msg_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "sender": "coordination_system",
            "type": "broadcast",
        }

        sent_count = 0
        for agent_id in self.agent_registry:
            if agent_id not in self.message_queue:
                self.message_queue[agent_id] = []
            self.message_queue[agent_id].append(msg_data)
            sent_count += 1

        logger.info(f"Broadcast sent to {sent_count} agents: {message[:50]}...")
        return ToolResult(output=f"Broadcast sent to {sent_count} agents")

    async def _request_status(self, target_agent: str = None) -> ToolResult:
        """Solicita status de um agente ou todos os agentes"""
        if target_agent:
            status = self.agent_registry.get(target_agent, {})
            return ToolResult(output=json.dumps({target_agent: status}))
        return ToolResult(output=json.dumps(self.agent_registry))

    async def _delegate_task(self, target_agent: str, task_data: dict) -> ToolResult:
        """Delega uma tarefa para um agente específico"""
        if not target_agent or not task_data:
            return ToolResult(error="Target agent and task data are required")

        task_id = str(uuid.uuid4())
        delegation = {
            "task_id": task_id,
            "target_agent": target_agent,
            "task_data": task_data,
            "status": "delegated",
            "timestamp": datetime.now().isoformat(),
        }

        self.task_delegations[task_id] = delegation

        # Enviar mensagem de delegação
        await self._send_message(target_agent, f"Task delegated: {json.dumps(task_data)}")

        logger.info(f"Task {task_id} delegated to {target_agent}")
        return ToolResult(output=f"Task {task_id} delegated to {target_agent}")

    async def _sync_state(self, target_agent: str, state_data: str) -> ToolResult:
        """Sincroniza estado com um agente"""
        if not target_agent:
            return ToolResult(error="Target agent is required for sync")

        # Registrar ou atualizar agente
        self.agent_registry[target_agent] = {
            "last_sync": datetime.now().isoformat(),
            "state": state_data,
            "status": "active",
        }

        return ToolResult(output=f"State synchronized with {target_agent}")


class DistributedMemoryTool(BaseTool):
    """Ferramenta MCP para memória compartilhada"""

    name: str = "distributed_memory"
    description: str = "Gerencia memória compartilhada entre agentes"
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["store", "retrieve", "delete", "list", "search"],
                "description": "Operação a ser executada na memória",
            },
            "key": {
                "type": "string",
                "description": "Chave para armazenamento/recuperação",
            },
            "value": {"type": "string", "description": "Valor a ser armazenado"},
            "namespace": {
                "type": "string",
                "default": "default",
                "description": "Namespace para organizar dados",
            },
            "query": {"type": "string", "description": "Query para busca"},
        },
        "required": ["operation"],
    }

    # Campo de estado como atributo de classe
    memory_store: dict[str, dict[str, Any]] = {}

    def __init__(self):
        super().__init__()
        # Inicializar store se necessário
        if not hasattr(self.__class__, "_memory_initialized"):
            self.__class__.memory_store = {}
            self.__class__._memory_initialized = True

    async def execute(
        self,
        operation: str,
        key: str = None,
        value: str = None,
        namespace: str = "default",
        query: str = None,
    ) -> ToolResult:
        """Implementa operações de memória compartilhada"""

        try:
            if operation == "store":
                return await self._store(namespace, key, value)
            if operation == "retrieve":
                return await self._retrieve(namespace, key)
            if operation == "delete":
                return await self._delete(namespace, key)
            if operation == "list":
                return await self._list(namespace)
            if operation == "search":
                return await self._search(namespace, query)
            return ToolResult(error=f"Unknown memory operation: {operation}")

        except Exception as e:
            logger.error(f"Error in distributed memory tool: {e}")
            return ToolResult(error=f"Memory error: {str(e)}")

    async def _store(self, namespace: str, key: str, value: str) -> ToolResult:
        """Armazena valor na memória"""
        if not key or value is None:
            return ToolResult(error="Key and value are required for store operation")

        if namespace not in self.memory_store:
            self.memory_store[namespace] = {}

        self.memory_store[namespace][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": type(value).__name__,
        }

        logger.info(f"Stored {key} in namespace {namespace}")
        return ToolResult(output=f"Value stored successfully at {namespace}:{key}")

    async def _retrieve(self, namespace: str, key: str) -> ToolResult:
        """Recupera valor da memória"""
        if not key:
            return ToolResult(error="Key is required for retrieve operation")

        if namespace not in self.memory_store:
            return ToolResult(error=f"Namespace {namespace} not found")

        if key not in self.memory_store[namespace]:
            return ToolResult(error=f"Key {key} not found in namespace {namespace}")

        data = self.memory_store[namespace][key]
        return ToolResult(output=data["value"])

    async def _delete(self, namespace: str, key: str) -> ToolResult:
        """Remove valor da memória"""
        if not key:
            return ToolResult(error="Key is required for delete operation")

        if namespace not in self.memory_store:
            return ToolResult(error=f"Namespace {namespace} not found")

        if key not in self.memory_store[namespace]:
            return ToolResult(error=f"Key {key} not found in namespace {namespace}")

        del self.memory_store[namespace][key]
        logger.info(f"Deleted {key} from namespace {namespace}")
        return ToolResult(output=f"Key {key} deleted from namespace {namespace}")

    async def _list(self, namespace: str) -> ToolResult:
        """Lista todas as chaves em um namespace"""
        if namespace not in self.memory_store:
            return ToolResult(output=json.dumps([]))

        keys = list(self.memory_store[namespace].keys())
        return ToolResult(output=json.dumps(keys))

    async def _search(self, namespace: str, query: str) -> ToolResult:
        """Busca valores que contenham a query"""
        if not query:
            return ToolResult(error="Query is required for search operation")

        if namespace not in self.memory_store:
            return ToolResult(output=json.dumps({}))

        results = {}
        for key, data in self.memory_store[namespace].items():
            if query.lower() in str(data["value"]).lower():
                results[key] = data["value"]

        return ToolResult(output=json.dumps(results))


class TaskRoutingTool(BaseTool):
    """Ferramenta MCP para roteamento inteligente de tarefas"""

    name: str = "task_routing"
    description: str = "Roteia tarefas para agentes especializados"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "analyze_task",
                    "route_task",
                    "get_recommendations",
                    "register_agent",
                ],
                "description": "Ação de roteamento",
            },
            "task": {"type": "string", "description": "Descrição da tarefa"},
            "requirements": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Requisitos específicos da tarefa",
            },
            "agent_info": {
                "type": "object",
                "description": "Informações do agente para registro",
                "properties": {
                    "agent_id": {"type": "string"},
                    "specializations": {"type": "array", "items": {"type": "string"}},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "load": {"type": "number", "default": 0.0},
                },
            },
        },
        "required": ["action"],
    }

    # Campo de estado como atributo de classe
    agent_capabilities: dict[str, dict] = {
        "code": {
            "specializations": ["development", "programming", "debugging"],
            "capabilities": ["bash", "editor", "python", "git"],
            "load": 0.0,
        },
        "research": {
            "specializations": ["research", "information_gathering", "analysis"],
            "capabilities": ["browser", "search", "document_reader"],
            "load": 0.0,
        },
        "analysis": {
            "specializations": ["data_analysis", "document_processing"],
            "capabilities": ["python", "editor", "document_reader"],
            "load": 0.0,
        },
        "browser": {
            "specializations": ["web_automation", "scraping"],
            "capabilities": ["browser"],
            "load": 0.0,
        },
        "system": {
            "specializations": ["system_admin", "infrastructure"],
            "capabilities": ["bash"],
            "load": 0.0,
        },
    }

    def __init__(self):
        super().__init__()
        # Inicializar capabilities se necessário
        if not hasattr(self.__class__, "_routing_initialized"):
            self.__class__._routing_initialized = True

    async def execute(
        self,
        action: str,
        task: str = None,
        requirements: list[str] = None,
        agent_info: dict = None,
    ) -> ToolResult:
        """Analisa tarefa e roteia para agente adequado"""

        try:
            if action == "analyze_task":
                return await self._analyze_task(task)
            if action == "route_task":
                return await self._route_task(task, requirements)
            if action == "get_recommendations":
                return await self._get_recommendations(task, requirements)
            if action == "register_agent":
                return await self._register_agent(agent_info)
            return ToolResult(error=f"Unknown routing action: {action}")

        except Exception as e:
            logger.error(f"Error in task routing tool: {e}")
            return ToolResult(error=f"Routing error: {str(e)}")

    async def _analyze_task(self, task: str) -> ToolResult:
        """Analisa uma tarefa e identifica requisitos"""
        if not task:
            return ToolResult(error="Task description is required")

        # Análise simples baseada em palavras-chave
        task_lower = task.lower()
        detected_requirements = []

        requirement_patterns = {
            "programming": [
                "code",
                "program",
                "develop",
                "script",
                "python",
                "javascript",
            ],
            "research": ["research", "find", "search", "investigate", "gather"],
            "web_automation": ["browser", "website", "web", "click", "navigate"],
            "data_analysis": ["analyze", "data", "chart", "graph", "statistics"],
            "system_admin": ["install", "configure", "system", "server", "terminal"],
            "document_processing": ["document", "pdf", "text", "read", "parse"],
        }

        for requirement, keywords in requirement_patterns.items():
            if any(keyword in task_lower for keyword in keywords):
                detected_requirements.append(requirement)

        analysis = {
            "task": task,
            "detected_requirements": detected_requirements,
            "complexity": (
                "high" if len(detected_requirements) > 2 else "medium" if len(detected_requirements) > 1 else "low"
            ),
        }

        return ToolResult(output=json.dumps(analysis))

    async def _route_task(self, task: str, requirements: list[str] = None) -> ToolResult:
        """Roteia tarefa para o melhor agente"""
        if not task:
            return ToolResult(error="Task description is required")

        # Se não há requisitos, analisar a tarefa
        if not requirements:
            analysis_result = await self._analyze_task(task)
            analysis = json.loads(analysis_result.output)
            requirements = analysis["detected_requirements"]

        # Calcular pontuação para cada agente
        agent_scores = {}
        for agent_id, capabilities in self.agent_capabilities.items():
            score = 0

            # Pontuação baseada em especializações
            for req in requirements:
                if req in capabilities["specializations"]:
                    score += 3

            # Pontuação baseada em capacidades
            for req in requirements:
                if req in capabilities["capabilities"]:
                    score += 2

            # Penalizar por carga atual
            score -= capabilities["load"] * 0.5

            agent_scores[agent_id] = score

        # Escolher melhor agente
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1])
            result = {
                "recommended_agent": best_agent[0],
                "confidence_score": best_agent[1],
                "all_scores": agent_scores,
            }
        else:
            result = {
                "recommended_agent": "default",
                "confidence_score": 0,
                "all_scores": {},
            }

        return ToolResult(output=json.dumps(result))

    async def _get_recommendations(self, task: str, requirements: list[str] = None) -> ToolResult:
        """Obtém recomendações detalhadas para roteamento"""
        routing_result = await self._route_task(task, requirements)
        routing_data = json.loads(routing_result.output)

        # Adicionar informações detalhadas
        recommended_agent = routing_data["recommended_agent"]
        if recommended_agent in self.agent_capabilities:
            agent_info = self.agent_capabilities[recommended_agent]
            routing_data["agent_info"] = agent_info
            routing_data["reasoning"] = (
                f"Agent {recommended_agent} selected based on specializations: {agent_info['specializations']}"
            )

        return ToolResult(output=json.dumps(routing_data))

    async def _register_agent(self, agent_info: dict) -> ToolResult:
        """Registra um novo agente no sistema de roteamento"""
        if not agent_info or "agent_id" not in agent_info:
            return ToolResult(error="Agent info with agent_id is required")

        agent_id = agent_info["agent_id"]
        self.agent_capabilities[agent_id] = {
            "specializations": agent_info.get("specializations", []),
            "capabilities": agent_info.get("capabilities", []),
            "load": agent_info.get("load", 0.0),
        }

        logger.info(f"Registered agent {agent_id}")
        return ToolResult(output=f"Agent {agent_id} registered successfully")
