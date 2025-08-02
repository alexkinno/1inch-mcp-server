"""Health check API routes."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy", "service": "1inch-mcp"}