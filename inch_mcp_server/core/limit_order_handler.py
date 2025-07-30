"""Tool handler for the 1inch Limit Order Protocol MCP Server."""


class LimitOrderHandler:
    """Handler for retrieving information about the 1inch Limit Order Protocol."""

    def __init__(self, mcp):
        """Initialize the Limit Order handler.

        Args:
            mcp: The MCP server instance (FastMCP v2)
        """
        self.mcp = mcp
        
        # Register tools using FastMCP v2 decorator style
        @mcp.tool
        async def get_1inch_protocol_info(query: str) -> str:
            """Get information about the 1inch Limit Order Protocol.
            
            Args:
                query: User query about the protocol
                
            Returns:
                Description of the 1inch Protocol
            """
            if not query:
                raise ValueError("Query must not be empty")
            return """The 1inch Limit Order Protocol is a decentralized, gas-efficient trading mechanism 
            that enables users to create off-chain signed orders, which can later be executed 
            on-chain by anyone. This design allows makers to post limit orders without paying gas fees, 
            while takers pay for execution. The protocol supports advanced features like dynamic pricing, 
            conditional execution, and both ERC-20 and NFT trading. It is widely used in DeFi for peer-to-peer 
            and RFQ-based trading, offering greater flexibility and composability than traditional AMMs. 
            """
