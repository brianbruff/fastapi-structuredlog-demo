"""
Middleware for capturing user context and adding it to structured logs.
"""

import base64
import re
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from .logger import get_logger

logger = get_logger(__name__)


class UserContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract user context from requests and bind it to the logger."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract user context and bind it to the logger for this request."""
        # Extract user from Authorization header
        username = self._extract_username(request)
        
        # Create a new logger context for this request
        request_logger = logger.bind(
            user=username,
            route=request.url.path,
            method=request.method,
            user_agent=request.headers.get("user-agent", "unknown"),
            request_id=id(request),  # Simple request ID for demo
        )
        
        # Store the logger in request state for use in routes
        request.state.logger = request_logger
        
        # Log the incoming request
        request_logger.info(
            "Request started",
            query_params=dict(request.query_params),
        )
        
        try:
            response = await call_next(request)
            
            # Log successful response
            request_logger.info(
                "Request completed",
                status_code=response.status_code,
            )
            
            return response
            
        except Exception as exc:
            # Log error
            request_logger.error(
                "Request failed",
                error=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )
            raise

    def _extract_username(self, request: Request) -> str:
        """
        Extract username from Authorization header.
        
        Supports:
        - Basic auth: Authorization: Basic <base64(username:password)>
        - Bearer token: Authorization: Bearer <token> (mock extraction)
        - Custom header: X-User-Name: <username>
        """
        auth_header = request.headers.get("authorization", "")
        custom_user_header = request.headers.get("x-user-name", "")
        
        # Check custom user header first (simplest for demo)
        if custom_user_header:
            return custom_user_header
        
        # Handle Basic auth
        if auth_header.startswith("Basic "):
            try:
                encoded_credentials = auth_header.split(" ", 1)[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
                username, _ = decoded_credentials.split(":", 1)
                return username
            except (ValueError, UnicodeDecodeError, IndexError):
                logger.warning("Invalid Basic auth header format")
                return "anonymous"
        
        # Handle Bearer token (mock extraction for demo)
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            # In a real application, you would validate the token and extract user info
            # For demo purposes, we'll mock user extraction from token
            return self._mock_user_from_token(token)
        
        return "anonymous"

    def _mock_user_from_token(self, token: str) -> str:
        """
        Mock user extraction from Bearer token.
        
        In a real application, this would validate the JWT token
        and extract user information from claims.
        """
        # Simple mock: if token contains 'user_', extract what follows until the next '_'
        if "user_" in token:
            match = re.search(r"user_(\w+?)(?:_|$)", token)
            if match:
                return match.group(1)
        
        # For demo tokens, return a mock user based on token hash
        if len(token) > 10:
            return f"user_{abs(hash(token)) % 1000}"
        
        return "anonymous"