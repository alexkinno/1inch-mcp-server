# 1inch API MCP Server - Project Brief

## Project Overview
A Model Context Protocol (MCP) server designed to integrate with 1inch DeFi protocol services, enabling AI agents and applications to interact with decentralized exchange functionality.

## Current Implementation Status
- ✅ Basic FastMCP server framework (HTTP + stdio transport)
- ✅ Docker containerization support
- ✅ Logging infrastructure
- ✅ Basic project structure
- ⚠️ **CRITICAL GAP**: Only minimal static tool (`get_1inch_protocol_info`)

## Technical Stack
- **Framework**: FastMCP (Model Context Protocol)
- **Transport**: Streamable HTTP (default) + stdio
- **Language**: Python 3.11+
- **Dependencies**: FastAPI, MCP, httpx, PyJWT, Pydantic
- **Deployment**: Docker + Docker Compose

## 1inch Protocol Context
1inch is a decentralized exchange (DEX) aggregator that:
- Finds optimal trading routes across multiple DEXes
- Provides limit order functionality via off-chain signed orders
- Offers gas-efficient trading mechanisms
- Supports advanced features like dynamic pricing and conditional execution

## Core Business Value
Enable AI agents to:
1. Execute DeFi trades through 1inch API
2. Query optimal swap routes and pricing
3. Manage limit orders programmatically  
4. Access real-time DeFi market data
5. Integrate DeFi functionality into AI workflows

## Architecture Goals
- **Security**: Safe handling of wallet interactions and API keys
- **Reliability**: Robust error handling for DeFi operations
- **Performance**: Efficient API calls and data processing
- **Extensibility**: Modular design for adding new 1inch features
