"""System and health API router"""

from fastapi import APIRouter, Depends

from app.api.dependencies.core import get_task_service
from app.services.task_service import TaskService

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "OpenManus API is running",
    }


@router.get("/info")
async def get_info():
    """System information"""
    return {
        "name": "OpenManus API",
        "version": "2.0.0",
        "description": "AI Assistant Backend API with Clean Architecture",
        "architecture": "Layered Architecture with DDD patterns",
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(task_service: TaskService = Depends(get_task_service)):
    """Get dashboard statistics"""
    return await task_service.get_dashboard_stats()
