import argparse
import uvicorn

from fastapi import FastAPI
from fastmcp import FastMCP

from inch_mcp_server.config import settings
from inch_mcp_server.core.limit_order_handler import LimitOrderHandler
from inch_mcp_server.utils.logger_setup import setup_logger

logger = setup_logger("server")

MCP_BASE_PORT = settings.effective_port
MCP_BASE_URL = settings.mcp_base_url

# Global reference to the MCP server instance
mcp = FastMCP('1inch-mcp-server')
LimitOrderHandler(mcp)

mcp_app = mcp.http_app()

# Create unified FastAPI app with MCP integration
app = FastAPI(
    title="1inch MCP Server API",
    description="REST API for the 1inch MCP Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=mcp_app.lifespan  # Key integration point for MCP
)


# Add FastAPI health check endpoint
@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "1inch-mcp"}


@app.get("/api/info", tags=["api"])
async def api_info():
    """Get API information."""
    return {
        "name": "1inch MCP Server",
        "version": "1.0.0",
        "description": "MCP server for 1inch Protocol",
        "mcp_endpoint": "/mcp",
        "docs": "/docs"
    }

# Mount MCP server - makes MCP tools available at /mcp endpoint
app.mount("/", mcp_app)


def setup_stdio_server():
    """Setup and run the MCP server with stdio transport."""
    # For stdio, we only need the MCP instance
    stdio_mcp = FastMCP('1inch-mcp-server')
    LimitOrderHandler(stdio_mcp)
    return stdio_mcp


def setup_http_server():
    """Set up the unified FastAPI + MCP server for HTTP transport."""
    # Tools are already registered globally, just return the app
    return app


def main():
    """Run the server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description='1inch MCP Server - Model Context Protocol server for 1inch API integration'
    )
    parser.add_argument(
        '--transport', 
        choices=['http', 'stdio'], 
        default='http',
        help='Transport method to use (default: http)'
    )
    
    args = parser.parse_args()
    logger.info(f'Starting 1inch MCP server with {args.transport} transport')

    if args.transport == 'stdio':
        # Run stdio server
        stdio_mcp = setup_stdio_server()
        stdio_mcp.run(transport='stdio')
    else:
        logger.info(f'Starting MCP server on port {MCP_BASE_PORT}')
        uvicorn.run(app, host="0.0.0.0", port=MCP_BASE_PORT)


if __name__ == '__main__':
    main()
