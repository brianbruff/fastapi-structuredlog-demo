"""
FastAPI dependencies for structured logging.
"""

from fastapi import Request
import structlog

from .logger import get_logger

# Default logger for routes that don't have middleware context
default_logger = get_logger(__name__)


def get_request_logger(request: Request) -> structlog.stdlib.BoundLogger:
    """
    Get the logger with user context bound from middleware.
    
    Falls back to default logger if middleware is not configured.
    """
    if hasattr(request.state, "logger"):
        return request.state.logger
    else:
        # Fallback for routes not using middleware
        return default_logger.bind(
            route=request.url.path,
            method=request.method,
            user="unknown",
        )