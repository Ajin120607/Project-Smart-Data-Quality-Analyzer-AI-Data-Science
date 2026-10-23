"""Health check endpoint."""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health_check():
    """Returns backend service status and timestamp."""
    return {
        "status": "healthy",
        "service": "Smart Data Quality Analyzer API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
