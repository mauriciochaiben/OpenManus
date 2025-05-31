"""Chat API router for OpenManus"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.infrastructure.messaging.progress_broadcaster import progress_broadcaster
from app.logger import logger


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception:
                self.disconnect(client_id)

    async def broadcast(self, message: str):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception:
                disconnected_clients.append(client_id)

        for client_id in disconnected_clients:
            self.disconnect(client_id)


# Pydantic models
class ChatMessage(BaseModel):
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    task_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    id: str
    message: str
    timestamp: str
    suggestions: Optional[List[str]] = []


# Global instances
router = APIRouter(prefix="/chat", tags=["chat"])
manager = ConnectionManager()

# Set up progress broadcaster with connection manager
progress_broadcaster.set_connection_manager(manager)

# In-memory chat history storage (replace with database in production)
chat_history: Dict[str, List[ChatMessage]] = {}


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            print(f"Received from {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@router.post("", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a message to the AI assistant and get a response"""
    from app.agent.manus import Manus
    from app.flow.flow_factory import FlowFactory, FlowType
    from app.flow.multi_agent import ExecutionMode
    from main import analyze_task_complexity

    # Generate response ID
    response_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    # Store user message
    user_message = ChatMessage(
        id=str(uuid.uuid4()), role="user", content=request.message, timestamp=timestamp
    )

    try:
        # Analisar complexidade da tarefa
        task_analysis = analyze_task_complexity(request.message)

        # Verificar se é uma pergunta sobre o sistema ou uma tarefa real
        content_lower = request.message.lower()

        # Respostas do sistema específicas (não executar agentes apenas para perguntas muito específicas)
        system_queries = [
            "o que são agentes",
            "que são agentes",
            "what are agents",
            "agentes do openmanus",
            "como funciona o openmanus",
            "how does openmanus work",
            "explicar openmanus",
            "help",
            "ajuda",
            "comandos",
            "instruções",
            "como usar",
        ]

        is_system_query = any(query in content_lower for query in system_queries)

        if is_system_query:
            if "agentes" in content_lower or "agents" in content_lower:
                response_content = """O OpenManus utiliza múltiplos agentes especializados:

🤖 **Manus Agent**: Operações gerais e coordenação
🌐 **Browser Agent**: Navegação web e coleta de dados
💻 **SWE Agent**: Desenvolvimento e programação
📊 **Data Analysis Agent**: Análise de dados e visualizações

Cada agente tem capacidades específicas e pode trabalhar em conjunto para tarefas complexas."""
                suggestions = [
                    "Como os agentes trabalham juntos?",
                    "Executar análise de dados",
                    "Navegar na web para pesquisa",
                ]
            elif "openmanus" in content_lower and (
                "como" in content_lower or "funciona" in content_lower
            ):
                response_content = """🚀 **Como funciona o OpenManus:**

O OpenManus é um sistema multi-agente que executa tarefas complexas:

• **Análise automática**: Identifica a complexidade da tarefa
• **Seleção de agentes**: Escolhe os agentes adequados
• **Execução coordenada**: Os agentes trabalham em conjunto
• **Resultados reais**: Gera arquivos, pesquisas e análises

**Exemplos de uso:**
- "Pesquisar sobre IA e criar relatório"
- "Analisar dados de vendas"
- "Desenvolver um script Python"
"""
                suggestions = [
                    "Pesquisar sobre tecnologia",
                    "Criar um relatório",
                    "Analisar dados",
                ]
            else:
                response_content = """🚀 **Bem-vindo ao OpenManus!**

Sou seu assistente de IA inteligente. Posso executar tarefas reais usando múltiplos agentes especializados:

• **Análise de documentos** e processamento de dados
• **Pesquisa na web** e coleta de informações
• **Desenvolvimento** e automação de código
• **Criação de relatórios** e apresentações
• **Automação de tarefas** complexas

**Como usar**: Simplesmente me diga o que você quer fazer, e eu executo usando os agentes apropriados!"""
                suggestions = [
                    "O que são agentes?",
                    "Pesquisar sobre IA",
                    "Analisar um documento",
                ]
        else:
            # Tarefa real - executar com agentes
            logger.info(f"Processando tarefa: {request.message}")
            logger.info(f"Análise de complexidade: {task_analysis}")

            # Criar agente Manus
            manus_agent = await Manus.create()

            # Generate task ID for progress tracking
            task_id = f"chat_{uuid.uuid4().hex[:8]}"

            try:
                if task_analysis["is_complex"]:
                    logger.info("Tarefa complexa detectada. Usando fluxo multi-agente.")

                    # Criar flow multi-agente
                    agents = {
                        "manus": manus_agent,
                        "primary": manus_agent,
                    }

                    flow = FlowFactory.create_flow(
                        flow_type=FlowType.MULTI_AGENT,
                        agents=agents,
                        mode=ExecutionMode.AUTO,
                        enable_planning=True,
                        enable_coordination=True,
                    )

                    await flow.initialize()
                    result = await flow.execute(request.message)

                    response_content = f"""✅ **Tarefa executada com multi-agentes**

**Resultado:**
{result}

**Análise:** Tarefa complexa processada com {len(agents)} agente(s) especializado(s)."""

                else:
                    logger.info("Tarefa simples detectada. Usando agente único.")

                    # Broadcast single agent progress
                    await progress_broadcaster.broadcast_progress(
                        task_id=task_id,
                        stage="Executando com agente único",
                        progress=20,
                        execution_type="single",
                        agents=["manus"],
                        task_name=(
                            request.message[:50] + "..."
                            if len(request.message) > 50
                            else request.message
                        ),
                        description="Processando tarefa com agente Manus",
                    )

                    result = await manus_agent.run(request.message)

                    # Broadcast completion
                    await progress_broadcaster.broadcast_completion(task_id, result)

                    response_content = f"""✅ **Tarefa executada com sucesso**

**Resultado:**
{result}

**Análise:** Tarefa simples processada com agente único."""

                suggestions = [
                    "Executar outra tarefa",
                    "Analisar resultado",
                    "Ver histórico de execuções",
                ]

            finally:
                # Cleanup
                await manus_agent.cleanup()
                if "flow" in locals() and hasattr(flow, "cleanup"):
                    await flow.cleanup()

    except Exception as e:
        error_msg = str(e).lower()

        # Check if this is a rate limit or quota error - let the LLM handle fallbacks
        if (
            "rate limit" in error_msg
            or "quota" in error_msg
            or "insufficient_quota" in error_msg
            or "retryerror" in error_msg
        ):
            logger.warning(
                f"Rate limit/quota error detected, attempting with system fallback: {str(e)}"
            )

            # Try using mock LLM for system queries
            if is_system_query:
                response_content = """🚀 **Sistema OpenManus (Modo Fallback)**

Sou seu assistente de IA inteligente. Atualmente operando em modo de fallback devido à limitação de recursos externos.

• **Funcionalidades Disponíveis**: Consultas sobre o sistema, informações gerais
• **Limitações Temporárias**: Execução de tarefas complexas pode estar restrita
• **Agentes**: Sistema multi-agente disponível quando recursos permitirem

**Como usar**: Faça perguntas sobre o sistema ou tente novamente em alguns minutos para tarefas complexas."""
                suggestions = [
                    "O que são agentes?",
                    "Como funciona o OpenManus?",
                    "Tentar novamente em alguns minutos",
                ]
            else:
                # For complex tasks, suggest retry or simplification
                response_content = f"""⚠️ **Recursos Temporariamente Limitados**

O sistema está enfrentando limitações temporárias de recursos externos.

**Possíveis soluções:**
• Tente novamente em alguns minutos
• Simplifique sua solicitação
• Use consultas sobre o sistema enquanto isso

**Detalhes técnicos:** {str(e)}"""
                suggestions = [
                    "Tentar novamente em 5 minutos",
                    "Simplificar a tarefa",
                    "Fazer pergunta sobre o sistema",
                    "Ver ajuda do sistema",
                ]
        else:
            # For other types of errors, use generic error handling
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            response_content = f"""❌ **Erro ao processar tarefa**

Ocorreu um erro durante a execução: {str(e)}

Tente reformular sua solicitação ou verificar se os recursos necessários estão disponíveis."""
            suggestions = [
                "Tentar novamente",
                "Simplificar a tarefa",
                "Ver ajuda do sistema",
            ]

    # Create assistant response
    assistant_message = ChatMessage(
        id=response_id, role="assistant", content=response_content, timestamp=timestamp
    )

    # Store messages in history (using 'default' session for now)
    session_id = "default"
    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].extend([user_message, assistant_message])

    # Send WebSocket notification
    await manager.broadcast(
        json.dumps(
            {
                "type": "chat_message",
                "data": {
                    "id": response_id,
                    "message": response_content,
                    "timestamp": timestamp,
                },
            }
        )
    )

    return ChatResponse(
        id=response_id,
        message=response_content,
        timestamp=timestamp,
        suggestions=suggestions,
    )


@router.get("/history")
async def get_chat_history(session_id: str = "default"):
    """Get chat history for a session"""
    return chat_history.get(session_id, [])


@router.delete("/history")
async def clear_chat_history(session_id: str = "default"):
    """Clear chat history for a session"""
    if session_id in chat_history:
        chat_history[session_id] = []
    return {"message": "Chat history cleared"}
