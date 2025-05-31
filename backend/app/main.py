from fastapi import FastAPI

from app.api.knowledge_api import router as knowledge_router

app = FastAPI()

# Include routers
app.include_router(knowledge_router)
