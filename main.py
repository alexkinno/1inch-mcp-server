#!/usr/bin/env python3
"""
Main entry point for the 1inch MCP Server.

This module provides the command-line interface for starting the server
with different transport options (http or stdio). It also exports the 
FastAPI app for direct use with uvicorn.
"""

from inch_mcp_server.core.server import main, app

# Export the FastAPI app for direct uvicorn usage (like test.py)
__all__ = ["app", "main"]

if __name__ == "__main__":
    main()
