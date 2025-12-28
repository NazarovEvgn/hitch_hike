from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pathlib import Path

from app.core.config import settings
from app.core.redis import redis_client
from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Lets API...")
    await redis_client.connect()
    logger.info("Redis connected")

    yield

    # Shutdown
    logger.info("Shutting down Lets API...")
    await redis_client.disconnect()
    logger.info("Redis disconnected")


# Create FastAPI application
app = FastAPI(
    title="Lets API",
    description="Real-time service availability platform for auto services",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
# In development, allow common localhost ports
# In production, use ALLOWED_ORIGINS from .env
if settings.environment == "development":
    # Explicitly list development origins for debugging
    cors_origins = [
        "http://localhost:5173",  # Business app
        "http://localhost:5174",  # Alternative port
        "http://localhost:5175",  # Consumer app
        "http://localhost:8000",  # Backend self-reference
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:8000",
    ]
else:
    cors_origins = settings.allowed_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
from app.api.v1 import admin, businesses, bookings, favorites, upload, profile

app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(businesses.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(favorites.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")

# Mount static files for uploaded photos
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Lets API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
