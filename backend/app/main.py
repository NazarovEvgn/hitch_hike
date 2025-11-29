from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.redis import redis_client
from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting HitchHike API...")
    await redis_client.connect()
    logger.info("Redis connected")

    yield

    # Shutdown
    logger.info("Shutting down HitchHike API...")
    await redis_client.disconnect()
    logger.info("Redis disconnected")


# Create FastAPI application
app = FastAPI(
    title="HitchHike API",
    description="Real-time service availability platform for auto services",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HitchHike API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
