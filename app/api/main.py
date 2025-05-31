"""
OpenManus API v2 - Clean Architecture Implementation
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api.routers import chat, system, tasks

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application with clean architecture"""

    app = FastAPI(
        title="OpenManus API v2",
        version="2.0.0",
        description="AI Assistant Backend API with Clean Architecture",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:5173",
            "http://localhost:5174",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat.router, prefix="/api/v2")
    app.include_router(tasks.router, prefix="/api/v2")
    app.include_router(system.router, prefix="/api/v2")

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "OpenManus API v2 - Clean Architecture",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/api/v2/system/health",
        }

    # Backward compatibility endpoints
    @app.get("/health")
    async def health_legacy():
        """Legacy health endpoint for backward compatibility"""
        return {"status": "healthy", "version": "2.0.0"}

    @app.get("/dashboard/stats")
    async def dashboard_stats_legacy():
        """Legacy dashboard stats endpoint"""
        from app.api.dependencies.core import get_task_service

        task_service = get_task_service()
        return await task_service.get_dashboard_stats()

    logger.info("OpenManus API v2 initialized with Clean Architecture")
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
