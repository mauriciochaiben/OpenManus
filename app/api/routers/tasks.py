"""Task management API router"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies.core import get_task_service
from app.domain.entities import Task, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Request/Response models
class CreateTaskRequest(BaseModel):
    title: str
    description: str
    mode: str = "auto"
    priority: str = "medium"
    tags: list[str] = []
    document_ids: list[str] = []
    config: dict = {}


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    complexity: str
    mode: str
    status: str
    progress: float
    created_at: str
    updated_at: str
    priority: str
    tags: list[str]
    document_ids: list[str]

    @classmethod
    def from_entity(cls, task: Task):
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            complexity=task.complexity.value,
            mode=task.mode.value,
            status=task.status.value,
            progress=task.progress,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            priority=task.priority,
            tags=task.tags,
            document_ids=task.document_ids,
        )


class UpdateTaskStatusRequest(BaseModel):
    status: str


@router.post("/", response_model=dict)
async def create_task(request: CreateTaskRequest, task_service: TaskService = Depends(get_task_service)):
    """Create a new task"""
    try:
        task = await task_service.create_task(
            title=request.title,
            description=request.description,
            mode=request.mode,
            priority=request.priority,
            tags=request.tags,
            document_ids=request.document_ids,
            config=request.config,
        )

        return {
            "task": TaskResponse.from_entity(task).dict(),
            "message": "Task created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(task_service: TaskService = Depends(get_task_service)):
    """Get all tasks"""
    tasks = await task_service.get_all_tasks()
    return [TaskResponse.from_entity(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    """Get task by ID"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_entity(task)


@router.put("/{task_id}/status")
async def update_task_status(
    task_id: str,
    request: UpdateTaskStatusRequest,
    task_service: TaskService = Depends(get_task_service),
):
    """Update task status"""
    try:
        status = TaskStatus(request.status)
        task = await task_service.update_task_status(task_id, status)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "task": TaskResponse.from_entity(task).dict(),
            "message": "Task status updated successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{task_id}")
async def delete_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    """Delete task"""
    success = await task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}
