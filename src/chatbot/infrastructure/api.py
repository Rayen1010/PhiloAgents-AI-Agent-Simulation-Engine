"""FastAPI application setup"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from chatbot.config import settings
from chatbot.infrastructure.routes import chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting Chatbot API")
    yield
    logger.info("Shutting down Chatbot API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application
    
    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title=settings.API_TITLE,
        description="Generic chatbot backend with RAG and evaluation",
        version=settings.API_VERSION,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat_router, prefix=settings.API_PREFIX, tags=["chat"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": settings.API_VERSION}
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": settings.API_TITLE,
            "version": settings.API_VERSION,
            "status": "running",
        }
    
    return app
