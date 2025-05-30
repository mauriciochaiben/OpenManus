import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="OpenManus API", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# In-memory storage (replace with database in production)
tasks_db = {}
documents_db = {}
mcp_servers_db = {}
task_executions_db = {}
agents_db = {}


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: str):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        for client_id in disconnected_clients:
            self.disconnect(client_id)


manager = ConnectionManager()


# Pydantic models
class TaskCreateRequest(BaseModel):
    title: str
    description: str
    complexity: str = "medium"
    priority: str = "medium"
    document_ids: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    mode: Optional[str] = "auto"
    config: Optional[Dict[str, Any]] = {}


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    complexity: str
    priority: str
    status: str
    created_at: str
    updated_at: str
    documents: Optional[List[dict]] = []
    tags: Optional[List[str]] = []
    mode: Optional[str] = "auto"
    progress: Optional[float] = 0.0
    steps: Optional[List[dict]] = []


class ComplexityAnalysisRequest(BaseModel):
    description: str


class ComplexityAnalysis(BaseModel):
    score: float
    isComplex: bool
    indicators: Dict[str, bool]
    recommendation: str


class DocumentProcessRequest(BaseModel):
    document_id: str


class ExecutionStep(BaseModel):
    id: str
    step_number: int
    title: str
    description: Optional[str] = ""
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    agent_name: Optional[str] = None
    output: Optional[str] = None
    error_message: Optional[str] = None


class TaskExecution(BaseModel):
    id: str
    task_id: str
    status: str = "pending"
    started_at: str
    completed_at: Optional[str] = None
    progress: float = 0.0
    steps: List[ExecutionStep] = []


class Agent(BaseModel):
    id: str
    name: str
    type: str
    status: str = "idle"
    capabilities: List[str] = []


class MCPServerConfig(BaseModel):
    name: str
    host: str
    port: int
    enabled: bool = True
    description: Optional[str] = ""


# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            logger.info(f"Received from {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)


# Helper function to broadcast task updates
async def broadcast_task_update(
    task_id: str, task_data: dict, event_type: str = "task_update"
):
    message = json.dumps({"type": event_type, "taskId": task_id, "data": task_data})
    await manager.broadcast(message)


# Task execution simulation
async def simulate_task_execution(task_id: str, execution_id: str):
    """Simulate task execution with progress updates"""
    try:
        if task_id not in tasks_db:
            return

        task = tasks_db[task_id]
        execution = task_executions_db[execution_id]

        # Update task status to running
        task["status"] = "running"
        execution["status"] = "running"
        await broadcast_task_update(task_id, task, "task_started")

        # Simulate execution steps
        steps = [
            {"title": "Analyzing requirements", "duration": 2},
            {"title": "Planning execution", "duration": 1},
            {"title": "Executing task", "duration": 3},
            {"title": "Finalizing results", "duration": 1},
        ]

        for i, step_info in enumerate(steps):
            if task["status"] == "cancelled":
                break

            step_id = str(uuid.uuid4())
            step = {
                "id": step_id,
                "step_number": i + 1,
                "title": step_info["title"],
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "agent_name": "manus-agent",
            }

            task["steps"].append(step)
            execution["steps"].append(step)

            # Broadcast step start
            await broadcast_task_update(task_id, {"step": step}, "step_started")

            # Simulate processing time
            await asyncio.sleep(step_info["duration"])

            # Complete step
            step["status"] = "completed"
            step["completed_at"] = datetime.now().isoformat()
            step["output"] = f"Completed {step_info['title'].lower()}"

            # Update progress
            progress = (i + 1) / len(steps)
            task["progress"] = progress
            execution["progress"] = progress

            # Broadcast step completion and progress
            await broadcast_task_update(task_id, {"step": step}, "step_completed")
            await broadcast_task_update(
                task_id, {"progress": progress}, "progress_update"
            )

        # Complete task if not cancelled
        if task["status"] != "cancelled":
            task["status"] = "completed"
            task["progress"] = 1.0
            task["completed_at"] = datetime.now().isoformat()
            execution["status"] = "completed"
            execution["completed_at"] = datetime.now().isoformat()

            await broadcast_task_update(task_id, task, "task_completed")

    except Exception as e:
        logger.error(f"Error in task execution {task_id}: {e}")
        if task_id in tasks_db:
            tasks_db[task_id]["status"] = "error"
            await broadcast_task_update(task_id, {"error": str(e)}, "task_error")


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# System info
@app.get("/info")
async def get_info():
    return {
        "name": "OpenManus API",
        "version": "1.0.0",
        "description": "AI Assistant Backend API",
    }


# Complexity analysis endpoint
@app.post("/analyze-complexity")
async def analyze_complexity(request: ComplexityAnalysisRequest) -> ComplexityAnalysis:
    description = request.description.lower()

    # Simple heuristic-based complexity analysis
    indicators = {
        "length": len(description) > 100,
        "keywords": any(
            keyword in description
            for keyword in [
                "multiple",
                "several",
                "many",
                "complex",
                "analyze",
                "research",
                "coordinate",
                "integrate",
                "comprehensive",
            ]
        ),
        "multipleDomains": any(
            domain in description
            for domain in [
                "file",
                "web",
                "database",
                "api",
                "document",
                "image",
                "data",
            ]
        ),
        "timeConsuming": any(
            phrase in description
            for phrase in ["detailed", "thorough", "extensive", "complete", "full"]
        ),
    }

    score = sum(indicators.values()) / len(indicators)
    is_complex = score > 0.5
    recommendation = "multi" if is_complex else "single"

    return ComplexityAnalysis(
        score=score,
        isComplex=is_complex,
        indicators=indicators,
        recommendation=recommendation,
    )


# Agents endpoint
@app.get("/agents")
async def get_agents():
    return list(agents_db.values())


# Task endpoints
@app.post("/tasks")
async def create_task(task_data: TaskCreateRequest):
    task_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    task = {
        "id": task_id,
        "title": task_data.title,
        "description": task_data.description,
        "complexity": task_data.complexity,
        "priority": task_data.priority,
        "mode": task_data.mode or "auto",
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "documents": [],
        "tags": task_data.tags or [],
        "progress": 0.0,
        "steps": [],
        "config": task_data.config or {},
    }

    # Add associated documents
    if task_data.document_ids:
        for doc_id in task_data.document_ids:
            if doc_id in documents_db:
                task["documents"].append(documents_db[doc_id])

    tasks_db[task_id] = task

    # Create task execution
    execution_id = str(uuid.uuid4())
    execution = {
        "id": execution_id,
        "task_id": task_id,
        "status": "pending",
        "started_at": now,
        "progress": 0.0,
        "steps": [],
    }
    task_executions_db[execution_id] = execution

    # Broadcast task creation
    await broadcast_task_update(task_id, task, "task_created")

    # Start task execution (simulate)
    asyncio.create_task(simulate_task_execution(task_id, execution_id))

    return {"task": task, "message": "Task created successfully"}


@app.get("/tasks")
async def get_tasks():
    return list(tasks_db.values())


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": "Task deleted successfully"}


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_db[task_id]["status"] = "cancelled"
    tasks_db[task_id]["updated_at"] = datetime.now().isoformat()

    # Broadcast cancellation
    await broadcast_task_update(task_id, tasks_db[task_id], "task_cancelled")

    return {"message": "Task cancelled successfully"}


@app.post("/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_id]
    task["status"] = "pending"
    task["progress"] = 0.0
    task["updated_at"] = datetime.now().isoformat()

    # Create new execution
    execution_id = str(uuid.uuid4())
    execution = {
        "id": execution_id,
        "task_id": task_id,
        "status": "pending",
        "started_at": datetime.now().isoformat(),
        "progress": 0.0,
        "steps": [],
    }
    task_executions_db[execution_id] = execution

    # Broadcast retry
    await broadcast_task_update(task_id, task, "task_retried")

    # Start task execution (simulate)
    asyncio.create_task(simulate_task_execution(task_id, execution_id))

    return {"task": task, "message": "Task retry initiated"}


@app.get("/tasks/{task_id}/logs")
async def get_task_logs(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return sample logs for now
    logs = [
        {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"Task {task_id} started",
            "source": "system",
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": "Processing task requirements",
            "source": "orchestrator",
        },
    ]
    return logs


# Document endpoints
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Create file path
    file_extension = Path(file.filename).suffix
    stored_filename = f"{doc_id}{file_extension}"
    file_path = UPLOADS_DIR / stored_filename

    try:
        # Save file to disk
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Create document record
        document = {
            "id": doc_id,
            "filename": file.filename,
            "stored_filename": stored_filename,
            "file_size": len(content),
            "file_type": file.content_type or "unknown",
            "status": "uploaded",
            "uploaded_at": datetime.now().isoformat(),
            "file_path": str(file_path),
        }

        documents_db[doc_id] = document
        return document

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_db[doc_id]


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    document = documents_db[doc_id]

    # Delete file from disk
    try:
        file_path = Path(document["file_path"])
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.error(f"Error deleting file: {e}")

    del documents_db[doc_id]
    return {"message": "Document deleted successfully"}


@app.post("/documents/{doc_id}/process")
async def process_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    document = documents_db[doc_id]
    document["status"] = "processing"

    # Simulate document processing
    await asyncio.sleep(1)

    # Mock extracted text based on file type
    if document["file_type"] and "text" in document["file_type"]:
        document["extracted_text"] = (
            f"Sample extracted text from {document['filename']}"
        )
    else:
        document["extracted_text"] = f"Processed content from {document['filename']}"

    document["status"] = "processed"
    document["processed_at"] = datetime.now().isoformat()

    return document


@app.get("/documents/{doc_id}/download")
async def download_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    document = documents_db[doc_id]
    file_path = Path(document["file_path"])

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path, filename=document["filename"], media_type=document["file_type"]
    )


# MCP Server endpoints
@app.get("/mcp/servers")
async def get_mcp_servers():
    return list(mcp_servers_db.values())


@app.post("/mcp/servers")
async def create_mcp_server(server_config: MCPServerConfig):
    server_id = str(uuid.uuid4())

    server = {
        "id": server_id,
        "name": server_config.name,
        "host": server_config.host,
        "port": server_config.port,
        "enabled": server_config.enabled,
        "description": server_config.description,
        "status": "disconnected",
        "created_at": datetime.now().isoformat(),
        "last_seen": None,
        "tools": [],
    }

    mcp_servers_db[server_id] = server
    return server


@app.put("/mcp/servers/{server_id}")
async def update_mcp_server(server_id: str, server_config: MCPServerConfig):
    if server_id not in mcp_servers_db:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server = mcp_servers_db[server_id]
    server.update(
        {
            "name": server_config.name,
            "host": server_config.host,
            "port": server_config.port,
            "enabled": server_config.enabled,
            "description": server_config.description,
            "updated_at": datetime.now().isoformat(),
        }
    )

    return server


@app.delete("/mcp/servers/{server_id}")
async def delete_mcp_server(server_id: str):
    if server_id not in mcp_servers_db:
        raise HTTPException(status_code=404, detail="MCP server not found")
    del mcp_servers_db[server_id]
    return {"message": "MCP server deleted successfully"}


@app.post("/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    if server_id not in mcp_servers_db:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server = mcp_servers_db[server_id]

    # Simulate connection attempt
    await asyncio.sleep(0.5)

    server["status"] = "connected"
    server["last_seen"] = datetime.now().isoformat()

    # Add mock tools
    server["tools"] = [
        {"name": "file_read", "description": "Read file contents"},
        {"name": "file_write", "description": "Write file contents"},
        {"name": "list_directory", "description": "List directory contents"},
    ]

    return server


@app.post("/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    if server_id not in mcp_servers_db:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server = mcp_servers_db[server_id]
    server["status"] = "disconnected"
    server["tools"] = []

    return {"message": "MCP server disconnected successfully"}


@app.get("/mcp/servers/{server_id}/tools")
async def get_server_tools(server_id: str):
    if server_id not in mcp_servers_db:
        raise HTTPException(status_code=404, detail="MCP server not found")

    server = mcp_servers_db[server_id]
    return server.get("tools", [])


# Add some sample data
def initialize_sample_data():
    # Sample agents
    sample_agents = [
        {
            "id": "agent-manus",
            "name": "Manus Agent",
            "type": "manus",
            "status": "idle",
            "capabilities": ["file_operations", "text_processing", "general_tasks"],
        },
        {
            "id": "agent-browser",
            "name": "Browser Agent",
            "type": "browser",
            "status": "idle",
            "capabilities": ["web_browsing", "web_scraping", "form_filling"],
        },
        {
            "id": "agent-swe",
            "name": "Software Engineering Agent",
            "type": "swe",
            "status": "idle",
            "capabilities": ["code_generation", "debugging", "testing"],
        },
        {
            "id": "agent-data",
            "name": "Data Analysis Agent",
            "type": "data_analysis",
            "status": "idle",
            "capabilities": ["data_processing", "visualization", "statistics"],
        },
    ]

    for agent in sample_agents:
        agents_db[agent["id"]] = agent

    # Sample MCP servers
    sample_mcp_servers = [
        {
            "id": "mcp-1",
            "name": "File Manager",
            "host": "localhost",
            "port": 8001,
            "enabled": True,
            "description": "File management operations",
            "status": "connected",
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "tools": [
                {"name": "read_file", "description": "Read file contents"},
                {"name": "write_file", "description": "Write content to file"},
                {"name": "list_files", "description": "List directory contents"},
            ],
        },
        {
            "id": "mcp-2",
            "name": "Database Connector",
            "host": "localhost",
            "port": 8002,
            "enabled": False,
            "description": "Database operations and queries",
            "status": "disconnected",
            "created_at": datetime.now().isoformat(),
            "last_seen": None,
            "tools": [],
        },
        {
            "id": "mcp-3",
            "name": "Web API Client",
            "host": "localhost",
            "port": 8003,
            "enabled": True,
            "description": "HTTP API client for external services",
            "status": "connected",
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "tools": [
                {"name": "http_get", "description": "Make HTTP GET requests"},
                {"name": "http_post", "description": "Make HTTP POST requests"},
            ],
        },
    ]

    for server in sample_mcp_servers:
        mcp_servers_db[server["id"]] = server

    # Sample tasks with more realistic data
    sample_tasks = [
        {
            "id": "task-1",
            "title": "Analisar Coleção de Documentos",
            "description": "Processar e analisar a coleção de documentos carregados para identificar padrões e insights importantes.",
            "complexity": "high",
            "priority": "medium",
            "mode": "multi",
            "status": "completed",
            "created_at": "2025-05-29T10:00:00",
            "updated_at": "2025-05-29T10:30:00",
            "completed_at": "2025-05-29T10:30:00",
            "documents": [],
            "tags": ["análise", "documentos", "insights"],
            "progress": 1.0,
            "steps": [
                {
                    "id": "step-1-1",
                    "step_number": 1,
                    "title": "Análise de requisitos",
                    "status": "completed",
                    "started_at": "2025-05-29T10:00:00",
                    "completed_at": "2025-05-29T10:05:00",
                    "agent_name": "manus-agent",
                    "output": "Requisitos analisados com sucesso",
                },
                {
                    "id": "step-1-2",
                    "step_number": 2,
                    "title": "Processamento dos documentos",
                    "status": "completed",
                    "started_at": "2025-05-29T10:05:00",
                    "completed_at": "2025-05-29T10:20:00",
                    "agent_name": "data-analysis-agent",
                    "output": "Documentos processados e indexados",
                },
                {
                    "id": "step-1-3",
                    "step_number": 3,
                    "title": "Extração de insights",
                    "status": "completed",
                    "started_at": "2025-05-29T10:20:00",
                    "completed_at": "2025-05-29T10:30:00",
                    "agent_name": "data-analysis-agent",
                    "output": "Insights extraídos e relatório gerado",
                },
            ],
        },
        {
            "id": "task-2",
            "title": "Gerar Relatório Executivo",
            "description": "Criar um relatório executivo abrangente baseado nos dados analisados, incluindo visualizações e recomendações.",
            "complexity": "medium",
            "priority": "high",
            "mode": "single",
            "status": "running",
            "created_at": "2025-05-29T11:00:00",
            "updated_at": "2025-05-29T11:15:00",
            "documents": [],
            "tags": ["relatório", "executivo", "visualização"],
            "progress": 0.6,
            "steps": [
                {
                    "id": "step-2-1",
                    "step_number": 1,
                    "title": "Coleta de dados",
                    "status": "completed",
                    "started_at": "2025-05-29T11:00:00",
                    "completed_at": "2025-05-29T11:05:00",
                    "agent_name": "manus-agent",
                    "output": "Dados coletados dos sistemas",
                },
                {
                    "id": "step-2-2",
                    "step_number": 2,
                    "title": "Criação de visualizações",
                    "status": "running",
                    "started_at": "2025-05-29T11:05:00",
                    "agent_name": "data-analysis-agent",
                },
            ],
        },
        {
            "id": "task-3",
            "title": "Pesquisa de Mercado Automatizada",
            "description": "Realizar pesquisa automatizada sobre tendências de mercado utilizando múltiplas fontes web e APIs.",
            "complexity": "high",
            "priority": "low",
            "mode": "multi",
            "status": "pending",
            "created_at": "2025-05-29T12:00:00",
            "updated_at": "2025-05-29T12:00:00",
            "documents": [],
            "tags": ["pesquisa", "mercado", "automação", "web"],
            "progress": 0.0,
            "steps": [],
        },
    ]

    for task in sample_tasks:
        tasks_db[task["id"]] = task


# Initialize sample data on startup
initialize_sample_data()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
