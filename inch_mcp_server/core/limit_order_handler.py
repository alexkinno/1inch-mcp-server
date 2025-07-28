"""Tool handler for the 1inch Limit Order Protocol MCP Server."""

from pydantic import Field


class LimitOrderHandler:
    """Handler for retrieving information about the 1inch Limit Order Protocol."""

    def __init__(self, mcp):
        """Initialize the Limit Order handler.

        Args:
            mcp: The MCP server instance (FastMCP or standard Server)
        """
        self.mcp = mcp
        self.mcp.tool(name='get_1inch_protocol_info')(self.get_1inch_protocol_info)

    @staticmethod
    async def get_1inch_protocol_info(
            query: str = Field(
            ...,
            description='User query',
            ),
    ) -> str:
        """
        :param query: the user query about protocol
        :return: description of the 1Inch Protocol
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
