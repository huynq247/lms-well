from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import assignments, progress, sessions, analytics
from app.database import init_database

app = FastAPI(
    title="Assignment Service",
    description="Assignment and Progress Tracking Service for LMS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assignments.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Assignment Service is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "assignment-service"}
