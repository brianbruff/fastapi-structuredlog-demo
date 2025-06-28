"""
FastAPI application with structured logging example.
"""

import secrets
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
import structlog

from .logger import get_logger
from .middleware import UserContextMiddleware
from .dependencies import get_request_logger

# Initialize the main logger
main_logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Structured Logging Demo bek",
    description="Example application demonstrating structured logging with user context",
    version="1.0.0",
)

# Add middleware for user context
app.add_middleware(UserContextMiddleware)

# Basic auth security
security = HTTPBasic()

# Mock user database (in production, use a real database)
fake_users_db = {
    "alice": "secret123",
    "bob": "password456", 
    "charlie": "mypassword",
    "admin": "admin123"
}

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user with basic auth credentials."""
    username = credentials.username
    password = credentials.password
    
    # Check if user exists and password is correct
    if username in fake_users_db and secrets.compare_digest(password, fake_users_db[username]):
        return username
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    main_logger.info("Application starting up", version="1.0.0")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    main_logger.info("Application shutting down")


@app.get("/")
async def root(logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)) -> Dict[str, str]:
    """Root endpoint with structured logging."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to FastAPI Structured Logging Demo boss",
        "info": "Use /login for authentication instructions, or /docs to see all endpoints"
    }


@app.get("/login")
async def login_info(logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)) -> Dict[str, Any]:
    """Provide login instructions and available test users."""
    logger.info("Login info requested")
    return {
        "message": "Use Basic Authentication to test username logging",
        "instructions": {
            "curl_example": "curl -u alice:secret123 http://localhost:8000/protected",
            "browser": "Visit /protected and enter username/password when prompted",
            "headers": "Add Authorization: Basic <base64(username:password)> header"
        },
        "test_users": {
            "alice": "secret123",
            "bob": "password456", 
            "charlie": "mypassword",
            "admin": "admin123"
        },
        "endpoints_to_test": [
            "/protected (requires auth)",
            "/user-info (shows current user)",
            "/auth-test (requires auth)"
        ]
    }


@app.get("/auth-test")
async def auth_test(
    current_user: str = Depends(authenticate_user),
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, str]:
    """Test endpoint that requires authentication."""
    logger.info("Authenticated endpoint accessed", authenticated_user=current_user)
    return {
        "message": f"Hello {current_user}! You are successfully authenticated.",
        "user": current_user,
        "note": "Check the logs to see your username being logged!"
    }


@app.get("/hello/{name}")
async def hello_user(
    name: str,
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, str]:
    """Personalized greeting endpoint."""
    logger.info("Hello endpoint accessed", target_name=name)
    return {"message": f"Hello, {name}!"}


@app.get("/protected")
async def protected_endpoint(
    current_user: str = Depends(authenticate_user),
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, str]:
    """Protected endpoint that requires authentication."""
    logger.info("Protected endpoint accessed", authenticated_user=current_user)
    return {
        "message": "This is a protected resource", 
        "status": "authenticated",
        "user": current_user
    }


@app.get("/user-info")
async def get_user_info(
    request: Request,
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, Any]:
    """Get current user information from the request context."""
    # Extract user from the logger context
    user = "unknown"
    if hasattr(request.state, "logger"):
        # Access bound context from the logger
        bound_logger = request.state.logger
        if hasattr(bound_logger, "_context"):
            user = bound_logger._context.get("user", "unknown")
    
    logger.info("User info requested", requested_user=user)
    
    return {
        "user": user,
        "request_id": id(request),
        "path": request.url.path,
        "method": request.method,
    }


@app.post("/simulate-error")
async def simulate_error(
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, str]:
    """Endpoint that simulates an error for testing logging."""
    logger.warning("Error simulation requested")
    
    try:
        # Simulate some processing
        logger.info("Processing simulation")
        
        # Simulate an error
        raise ValueError("This is a simulated error for testing logging")
        
    except ValueError as e:
        logger.error("Simulated error occurred", error_details=str(e))
        raise HTTPException(status_code=500, detail="Simulated error occurred")


@app.get("/health")
async def health_check(
    logger: structlog.stdlib.BoundLogger = Depends(get_request_logger)
) -> Dict[str, str]:
    """Health check endpoint."""
    logger.debug("Health check performed")
    return {"status": "healthy", "service": "fastapi-structured-logging"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging."""
    logger = get_request_logger(request)
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_id": id(request)},
    )


if __name__ == "__main__":
    import uvicorn
    
    main_logger.info("Starting FastAPI server", host="127.0.0.1", port=8000)
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=None,  # Disable uvicorn's default logging to use our structured logging
    )