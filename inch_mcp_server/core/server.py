import argparse
from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware

from inch_mcp_server.config import settings
from inch_mcp_server.core.limit_order_handler import LimitOrderHandler
from inch_mcp_server.core.models import PostLimitOrderV4Request
from inch_mcp_server.core.services import post_order, fetch_and_store_orders
from inch_mcp_server.utils.logger_setup import setup_logger
from inch_mcp_server.database import initialize_database, close_database_connections

logger = setup_logger("server")

MCP_BASE_URL = settings.mcp_base_url
MCP_BASE_PORT = settings.effective_port

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
#
# app.add_middleware(
#     SQLAlchemyMiddleware,
#     db_url=settings.database_url,
#     engine_args={
#         "echo": True,
#         "pool_pre_ping": True,
#         "pool_size": 10,
#         "max_overflow": 20,
#     }
# )


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/orders", tags=["orders"])
async def get_orders(chain: int, address: str):
    return await fetch_and_store_orders(chain, address)


@app.post("/orders", tags=["orders"])
async def store_order(chain: int, order: PostLimitOrderV4Request):
    return await post_order(chain, order)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "1inch-mcp"}


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
    uvicorn.run(app, host=MCP_BASE_URL, port=MCP_BASE_PORT)


if __name__ == '__main__':
    main()
