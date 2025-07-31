import argparse
from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastmcp import FastMCP

from inch_mcp_server.config import settings
from inch_mcp_server.core.limit_order_handler import LimitOrderHandler
from inch_mcp_server.utils.logger_setup import setup_logger
from inch_mcp_server.database import initialize_database, close_database_connections

logger = setup_logger("server")

MCP_BASE_PORT = settings.effective_port
MCP_BASE_URL = settings.mcp_base_url

# Global reference to the MCP server instance
mcp = FastMCP('1inch-mcp-server')
LimitOrderHandler(mcp)
mcp_app = mcp.http_app()


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for FastAPI app with database initialization."""
    logger.info("Starting up 1inch MCP Server...")
    # try:
    #     # Initialize database and run migrations if needed
    #     await initialize_database()
    #     logger.info("Database initialized successfully")
    # except Exception as e:
    #     logger.error(f"Failed to initialize database: {e}")
    #     logger.warning("Continuing without database initialization. Database may not be available.")
        # Don't raise - allow server to start even if database is not available
    # task = create_task()  # TODO: Implement the task to check orders
    yield
    logger.info("Shutting down 1inch MCP Server...")
    # try:
    #     await close_database_connections()
    #     logger.info("Database connections closed")
    # except Exception as e:
    #     logger.error(f"Error closing database connections: {e}")
    # task.cancel()


app = FastAPI(
    title="1inch-mcp",
    description="1inch API Limit Order MCP",
    version="0.0.1",
    redoc_url=None,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    lifespan=mcp_app.lifespan,
)

@app.get("/", tags=["orders"])
async def get_orders(wallet: str):
    pass


@app.post("/", tags=["orders"])
async def store_order(wallet: str, order: dict):
    pass


@app.delete("/", tags=["orders"])
async def delete_order(wallet: str, order_id: str):
    pass


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "1inch-mcp"}


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
