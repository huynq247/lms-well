"""
Simple API Gateway simulation for development testing
WITHOUT Docker - just run the services manually and use this gateway for routing
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import os
from typing import Any

app = FastAPI(
    title="🌐 LMS API Gateway",
    description="""
    # Learning Management System - API Gateway
    
    Central routing point for all LMS microservices.
    
    ## Available Services:
    
    ### � Auth Service (`/api/v1/auth/*`)
    - Manages user authentication and authorization
    - Endpoints: login, register, profile, logout
    - Database: PostgreSQL
    - Port: 8001
    
    ### �📚 Assignment Service (`/api/assignments/*`)
    - Manages assignments, user progress, and study sessions
    - Endpoints: assignments, users, progress, analytics
    - Database: PostgreSQL
    - Port: 8004
    
    ### 📖 Content Service (`/api/courses/*`, `/api/lessons/*`, `/api/decks/*`, `/api/flashcards/*`)
    - Manages courses, lessons, decks, and flashcards
    - Endpoints: courses, lessons, decks, flashcards
    - Database: MongoDB  
    - Port: 8002
    
    ## Authentication
    - JWT tokens (coming soon)
    - API key authentication (coming soon)
    
    ## Rate Limiting
    - Per-user limits (coming soon)
    - Per-IP limits (coming soon)
    
    ## Health Monitoring
    - Gateway health: `GET /health`
    - Individual service health monitoring
    """,
    version="1.0.0",
    contact={
        "name": "LMS Development Team",
        "email": "dev@lms.local"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Service URLs - read from environment variables with fallback to localhost
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
ASSIGNMENT_SERVICE_URL = os.getenv("ASSIGNMENT_SERVICE_URL", "http://localhost:8004")
CONTENT_SERVICE_URL = os.getenv("CONTENT_SERVICE_URL", "http://localhost:8002")

async def forward_request(url: str, method: str, headers: dict, params: dict = None, json_data: Any = None):
    """Forward request to target service"""
    # Filter out problematic headers
    filtered_headers = {
        k: v for k, v in headers.items() 
        if k.lower() not in ['content-length', 'host', 'connection', 'transfer-encoding']
    }
    
    print(f"🔧 Gateway forwarding {method} {url}")
    print(f"🔧 Authorization header: {filtered_headers.get('authorization', 'NOT FOUND')}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=filtered_headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=filtered_headers, params=params, json=json_data)
            elif method == "PUT":
                response = await client.put(url, headers=filtered_headers, params=params, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url, headers=filtered_headers, params=params)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return {
                "status_code": response.status_code,
                "content": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {url}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

async def get_json_data_safely(request: Request):
    """Safely get JSON data from request based on method and content type"""
    if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
        try:
            return await request.json()
        except:
            return None
    return None

@app.get("/")
async def gateway_info():
    """API Gateway information - Frontend Integration Ready"""
    return {
        "service": "LMS API Gateway",
        "version": "1.0.0",
        "status": "ready_for_frontend",
        "base_url": "http://localhost:8000",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "services": {
            "auth_service": AUTH_SERVICE_URL,
            "assignment_service": ASSIGNMENT_SERVICE_URL,
            "content_service": CONTENT_SERVICE_URL
        },
        "available_endpoints": {
            "auth": "/api/v1/auth/*",
            "assignments": "/api/assignments/",
            "courses": "/api/courses/*",
            "lessons": "/api/lessons/*",
            "decks": "/api/decks/*",
            "flashcards": "/api/flashcards/*",
            "health": "/health",
            "status": {
                "auth": "/api/v1/auth/profile",
                "assignments": "/api/assignments/status",
                "courses": "/api/courses/status"
            }
        },
        "frontend_notes": {
            "cors": "enabled_for_all_origins",
            "authentication": "jwt_implementation_pending",
            "pagination": "supported_with_page_size_params",
            "error_handling": "standard_http_status_codes"
        }
    }

@app.get("/health")
async def health_check():
    """Aggregate health check"""
    health_status = {"gateway": "healthy", "services": {}}
    
    # Check Auth Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/health")
            health_status["services"]["auth_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["auth_service"] = "unavailable"
    
    # Check Assignment Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ASSIGNMENT_SERVICE_URL}/health")
            health_status["services"]["assignment_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["assignment_service"] = "unavailable"
    
    # Check Content Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CONTENT_SERVICE_URL}/health")
            health_status["services"]["content_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["content_service"] = "unavailable"
    
    return health_status

# Auth Service Routes
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth(request: Request, path: str):
    """Route auth requests"""
    url = f"{AUTH_SERVICE_URL}/api/v1/auth/{path}"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Users Service Routes (part of Auth Service)
@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_users_with_path(request: Request, path: str):
    """Route users requests with path to Auth Service"""
    url = f"{AUTH_SERVICE_URL}/api/v1/users/{path}"
    
    # Only try to parse JSON for methods that might have a body
    json_data = None
    if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
        try:
            json_data = await request.json()
        except:
            json_data = None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/v1/users/", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/v1/users", methods=["GET", "POST", "PUT", "DELETE"])
async def route_users_root(request: Request):
    """Route users root requests to Auth Service (with and without trailing slash)"""
    url = f"{AUTH_SERVICE_URL}/api/v1/users/"
    
    # Only try to parse JSON for methods that might have a body
    json_data = None
    if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
        try:
            json_data = await request.json()
        except:
            json_data = None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Assignment Service Routes
@app.api_route("/api/assignments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_assignments(request: Request, path: str):
    """Route assignments requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/assignments/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Backward compatibility route for assignments (without /api prefix)
@app.api_route("/assignments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_assignments_compat(request: Request, path: str):
    """Route assignments requests (backward compatibility)"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/assignments/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/progress/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_progress(request: Request, path: str):
    """Route progress requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/progress/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

@app.api_route("/api/sessions/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_sessions(request: Request, path: str):
    """Route sessions requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/sessions/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

@app.api_route("/api/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_analytics(request: Request, path: str):
    """Route analytics requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/analytics/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

# Content Service Routes
@app.api_route("/api/courses/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/courses/", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/courses", methods=["GET", "POST", "PUT", "DELETE"])
async def route_courses(request: Request, path: str = ""):
    """Route courses requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/courses/{path}" if path else f"{CONTENT_SERVICE_URL}/api/v1/courses/"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Decks Service Routes (Content Service)
@app.api_route("/api/decks/", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/decks", methods=["GET", "POST", "PUT", "DELETE"])
async def route_decks_root(request: Request):
    """Route decks root requests to Content Service"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/decks/"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Lessons Service Routes (Content Service)
@app.api_route("/api/lessons/", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/lessons", methods=["GET", "POST", "PUT", "DELETE"])
async def route_lessons_root(request: Request):
    """Route lessons root requests to Content Service"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/lessons/"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/lessons/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_lessons(request: Request, path: str):
    """Route lessons requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/lessons/{path}"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

# Flashcards Service Routes (Content Service)
@app.api_route("/api/flashcards/", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/flashcards", methods=["GET", "POST", "PUT", "DELETE"])
async def route_flashcards_root(request: Request):
    """Route flashcards root requests to Content Service"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/flashcards/"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/flashcards/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_flashcards(request: Request, path: str):
    """Route flashcards requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/flashcards/{path}"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/decks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_decks(request: Request, path: str):
    """Route decks requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/decks/{path}"
    json_data = await get_json_data_safely(request)
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting API Gateway on http://localhost:8000")
    print("� Auth Service: http://localhost:8001")
    print("�📚 Assignment Service: http://localhost:8004")
    print("📖 Content Service: http://localhost:8002")
    print("🔗 Gateway Routes:")
    print("  - /api/v1/auth/* → Auth Service")
    print("  - /api/assignments/* → Assignment Service")
    print("  - /api/courses/* → Content Service")
    print("  - /api/decks/* → Content Service")
    print("  - /api/flashcards/* → Content Service")
    uvicorn.run(app, host="0.0.0.0", port=8000)
