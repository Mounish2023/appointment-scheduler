# backend/app/main.py (Updated with sample data loading)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import uvicorn
import os
from .config import settings
from .database import create_tables
from .create_collections import create_conversations_collection
from .routes import chat_routes, auth_routes, document_routes
from .utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Assist...")
    # await create_tables()
    create_conversations_collection()  # This is now a synchronous call
    # logger.info("Database initialization completed")
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT_NAME"] = settings.LANGSMITH_PROJECT_NAME
    os.environ["LANGSMITH_TRACING"] = settings.LANGSMITH_TRACING
    os.environ["LANGSMITH_ENDPOINT"] =settings.LANGSMITH_ENDPOINT
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered assistant",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
app.include_router(auth_routes.router, tags=["auth"])
app.include_router(document_routes.router, prefix="/documents", tags=["documents"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Assist",
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Assist"}

# Admin endpoint to reload sample data (for testing)
@app.post("/admin/reload-sample-data")
async def reload_sample_data():
    """Reload sample data for testing purposes."""
    from .sample_data_loader import clear_and_reload_sample_data
    await clear_and_reload_sample_data()
    return {"message": "Sample data reloaded successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
