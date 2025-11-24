from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import db_manager
from app.api.courses import router as courses_router
from app.api.lessons import router as lessons_router
from app.api.decks import router as decks_router
from app.api.flashcards import router as flashcards_router
from app.api.ai import router as ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print(f"🚀 Content Service starting up...")
    print(f"📊 MongoDB URL: {settings.mongodb_url}")
    print(f"🔑 Environment: {settings.environment}")
    
    # Connect to database
    await db_manager.connect_to_database()
    
    yield
    
    # Close database connection
    await db_manager.close_database_connection()
    print("📊 Content Service shutting down...")

app = FastAPI(
    title="LMS Content Service",
    description="Content Management Service for Learning Management System - Courses, Lessons, Decks, and Flashcards",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.core.database import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "content-service",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LMS Content Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "courses": "/api/v1/courses",
            "lessons": "/api/v1/lessons",
            "decks": "/api/v1/decks",
            "flashcards": "/api/v1/flashcards",
            "ai": "/api/v1/ai"
        }
    }

# Include routers
app.include_router(courses_router, prefix="/api/v1")
app.include_router(lessons_router, prefix="/api/v1")
app.include_router(decks_router, prefix="/api/v1")
app.include_router(flashcards_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
