import argparse
import os

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from inch_mcp_server.core.limit_order_handler import LimitOrderHandler
from inch_mcp_server.utils.logger_setup import setup_logger

logger = setup_logger("server")

MCP_BASE_PORT = int(os.getenv("PORT", os.getenv("MCP_BASE_PORT", 8000)))
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost")

# Global reference to the MCP server instance for testing purposes
mcp = None


def setup_stdio_server():
    """Setup and run the MCP server with stdio transport."""
    global mcp

    mcp = FastMCP('1inch-mcp-server')
    
    # Initialize tool handlers
    LimitOrderHandler(mcp)

    return mcp


def setup_http_server():
    """Set up the MCP server with HTTP transport."""
    global mcp
    
    # Create FastMCP server for HTTP transport
    mcp = FastMCP('1inch-mcp-server')
    
    # Add health check endpoint for HTTP transport
    @mcp.custom_route("/", methods=["GET"])
    async def health_check(_: Request):
        """Health check endpoint for container orchestration."""
        return JSONResponse({
            "status": "healthy",
            "service": "1inch-mcp"
        })
    
    # Initialize tool handlers
    LimitOrderHandler(mcp)
    
    return mcp


def main():
    """Run the MCP server with CLI argument support."""
    global mcp

    parser = argparse.ArgumentParser(
        description='1inch MCP Server - Model Context Protocol server for 1inch API integration'
    )
    parser.add_argument(
        '--transport', 
        choices=['streamable-http', 'stdio'], 
        default='streamable-http',
        help='Transport method to use (default: streamable-http)'
    )
    
    args = parser.parse_args()
    logger.info(f'Starting 1inch MCP server with {args.transport} transport')

    if args.transport == 'stdio':
        # Run stdio server
        mcp = setup_stdio_server()
        mcp.run(transport='stdio')
    else:
        # Run HTTP server (default)
        mcp = setup_http_server()
        mcp.run(transport='http', host="0.0.0.0", port=MCP_BASE_PORT, path="/mcp")

    return mcp


if __name__ == '__main__':
    main()
