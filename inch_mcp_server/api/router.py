"""Main API router aggregator."""

from fastapi import APIRouter

from inch_mcp_server.api.routes import health, limit_orders

# Create the main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(limit_orders.router)
api_router.include_router(health.router)