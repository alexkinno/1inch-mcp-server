#!/usr/bin/env python3
"""
Main entry point for the 1inch MCP Server.

This module provides the command-line interface for starting the server
with different transport options (streamable-http or stdio).
"""

from inch_mcp_server.core.server import main

if __name__ == "__main__":
    main()
