from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.core.config import settings
from app.core.database import db_manager, check_database_health

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"🚀 Assignment Service starting up...")
    logger.info(f"📊 Database URL: {settings.database_url}")
    logger.info(f"🔑 Environment: {settings.environment}")
    
    # Connect to database
    await db_manager.connect_to_database()
    
    yield
    
    # Cleanup
    await db_manager.disconnect_from_database()
    logger.info("📴 Assignment Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="LMS Assignment Service",
    description="Assignment and Progress Tracking Service for Learning Management System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "assignment-service",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LMS Assignment Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "assignments": "/api/v1/assignments",
            "progress": "/api/v1/progress",
            "sessions": "/api/v1/sessions",
            "analytics": "/api/v1/analytics"
        }
    }

# Include API routers
from app.api.analytics import router as analytics_router

try:
    from app.api.assignments import router as assignments_router
    app.include_router(assignments_router, prefix="/api")
except ImportError:
    logger.warning("Assignments router not available")

try:
    from app.api.progress import router as progress_router
    app.include_router(progress_router, prefix="/api")
except ImportError:
    logger.warning("Progress router not available")

try:
    from app.api.sessions import router as sessions_router
    app.include_router(sessions_router, prefix="/api")
except ImportError:
    logger.warning("Sessions router not available")

app.include_router(analytics_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
