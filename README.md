# 1inch API MCP

1inch API MCP (Model Context Protocol) server for integrating with 1Inch services.

Built with [FastMCP v2](https://gofastmcp.com) - the fast, Pythonic way to build MCP servers.

## Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install .
```

## Usage

The server supports two transport methods:

### Streamable HTTP (Default)

For web-based integrations and HTTP clients:

```bash
1inch-mcp-server
# or explicitly:
1inch-mcp-server --transport streamable-http
```

This starts the server on `http://localhost:8000` with the MCP endpoint at `/mcp`.

### Stdio Transport

For local integrations and command-line MCP clients:

```bash
1inch-mcp-server --transport stdio
```

This mode uses standard input/output streams and is ideal for:
- Local MCP client integrations
- Command-line tools
- Process-based communication

### Command Line Options

```bash
1inch-mcp-server --help
```

Available options:
- `--transport {streamable-http,stdio}`: Choose transport method (default: streamable-http)

## Development

This package provides MCP tools for interacting with 1inch APIs, built with FastMCP v2.

### Running Directly

For development, you can also run the server directly:

```bash
# HTTP transport (default)
python main.py --transport streamable-http

# Stdio transport  
python main.py --transport stdio
```

### Testing with FastMCP CLI

You can also test the server using FastMCP's built-in CLI:

```bash
# Test with MCP Inspector (WebUI)
fastmcp inspect main.py

# Test with CLI
fastmcp dev main.py
```

## Transport Details

### Streamable HTTP
- Uses FastMCP v2's optimized HTTP transport with Server-Sent Events
- Includes health check endpoint at `/` 
- MCP endpoint available at `/mcp`
- Suitable for web integrations and HTTP-based MCP clients
- Default port: 8000 (configurable via `PORT` or `MCP_BASE_PORT` env vars)

### Stdio
- Uses standard input/output streams
- JSON-RPC over stdin/stdout
- Suitable for local process communication
- No HTTP server required

## License

MIT