"""Dependency injection configuration for the 1inch MCP Server."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from inch_mcp_server.integrations.api.limit_order_api_client import LimitOrderAPIClient
from inch_mcp_server.integrations.services.limit_order_service import LimitOrderService


@lru_cache()
def get_api_client() -> LimitOrderAPIClient:
    """Get a singleton instance of the API client.
    
    Returns:
        LimitOrderAPIClient: The API client instance
    """
    return LimitOrderAPIClient()


def get_limit_order_service(
    api_client: Annotated[LimitOrderAPIClient, Depends(get_api_client)]
) -> LimitOrderService:
    """Get a limit order service instance with injected API client.
    
    Args:
        api_client: The injected API client instance
        
    Returns:
        LimitOrderService: The service instance with injected dependencies
    """
    return LimitOrderService(api_client=api_client)


def create_service_for_mcp() -> LimitOrderService:
    """Create a service instance for MCP setup (outside of FastAPI context).
    
    This function manually resolves dependencies since it's called outside of 
    FastAPI's dependency injection system during MCP server initialization.
    
    Returns:
        LimitOrderService: Service instance with properly injected dependencies
    """
    api_client = get_api_client()
    return LimitOrderService(api_client=api_client)


# Type aliases for dependency injection
APIClientDep = Annotated[LimitOrderAPIClient, Depends(get_api_client)]
LimitOrderServiceDep = Annotated[LimitOrderService, Depends(get_limit_order_service)]