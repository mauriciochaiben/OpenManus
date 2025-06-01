"""
API v1 package initialization.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import knowledge, workflows

# Create root router for API v1
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(knowledge.router, prefix="/knowledge")
api_router.include_router(workflows.router)
