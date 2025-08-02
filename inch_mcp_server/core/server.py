import argparse
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastmcp import FastMCP

from inch_mcp_server.api.router import api_router
from inch_mcp_server.config import settings
from inch_mcp_server.dependencies import create_service_for_mcp
from inch_mcp_server.handlers import LimitOrderHandler
from inch_mcp_server.utils.logger_setup import setup_logger

logger = setup_logger("server")

MCP_BASE_URL = settings.mcp_base_url
MCP_BASE_PORT = settings.effective_port

# Global reference to the MCP server instance
mcp = FastMCP("1inch-mcp-server")

_service_for_mcp = create_service_for_mcp()
LimitOrderHandler(mcp, _service_for_mcp)
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


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://aiagents.hackathon.haust.app",
]

app = FastAPI(
    title="1inch-mcp",
    description="1inch API Limit Order MCP",
    version="0.0.1",
    redoc_url=None,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    lifespan=mcp_app.lifespan,
)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.database_url,
    engine_args={
        "echo": True,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    },
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

# Include the MCP app as a sub-application
app.mount("/mcp-server", mcp_app)


def main():
    """Run the server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="1inch MCP Server - Model Context Protocol server for 1inch API integration"
    )
    parser.add_argument(
        "--transport", choices=["http", "stdio"], default="http", help="Transport method to use (default: http)"
    )

    args = parser.parse_args()
    logger.info(f"Starting 1inch MCP server with {args.transport} transport")
    uvicorn.run(app, host=MCP_BASE_URL, port=MCP_BASE_PORT)


if __name__ == "__main__":
    main()
