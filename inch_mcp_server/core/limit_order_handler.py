"""Tool handler for the 1inch Limit Order Protocol MCP Server."""
from typing import List

from .one_inch_service import OneInchService
from .services import fetch_and_store_orders, retrieve_order_fee, fetch_order_by_hash
from .models import FeeExtension, FeeInfoDTO


class LimitOrderHandler:
    """Handler for retrieving information about the 1inch Limit Order Protocol."""

    def __init__(self, mcp):
        """Initialize the Limit Order handler.

        Args:
            mcp: The MCP server instance (FastMCP v2)
        """
        self.mcp = mcp
        self.one_inch_service = OneInchService()

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

        @mcp.tool
        async def get_limit_orders_by_chain_and_address(chain: int, address: str) -> List[dict]:
            """Get all limit orders for a specific chain and address.

            Args:
                chain: The blockchain chain ID (e.g., 1 for Ethereum, 137 for Polygon). Optional parameter, 1 by default
                address: The wallet address to get orders for. Required parameter

            Returns:
                Dictionary containing the limit orders data
            """
            if not chain or chain <= 0:
                raise ValueError("Chain ID must be a positive integer")
            if not address or len(address) != 42 or not address.startswith("0x"):
                raise ValueError("Address must be a valid Ethereum address (42 characters starting with 0x)")
            
            try:
                return await fetch_and_store_orders(chain, address)
            except Exception as e:
                raise ValueError(f"Failed to fetch orders: {str(e)}")

        @mcp.tool
        async def get_limit_order_fee_info(chain: int, maker_asset: str, taker_asset: str,
                                     maker_amount: int, taker_amount: int) -> dict:
            """Get fee information for a limit order on a specific chain.

            Args:
                chain: The blockchain chain ID (e.g., 1 for Ethereum, 137 for Polygon). Optional parameter, 1 by default
                maker_asset: The token address that the maker wants to sell. Required parameter. Should be a valid maker token address specific to the provided chain
                taker_asset: The token address that the maker wants to buy. Required parameter. Should be a valid taker token address specific to the provided chain
                maker_amount: The amount of maker tokens to sell. Required parameter
                taker_amount: The amount of taker tokens to buy. Required parameter

            Returns:
                Dictionary containing the fee information including feeBps, whitelist, etc.
            """
            if not chain or chain <= 0:
                raise ValueError("Chain ID must be a positive integer")
            if not maker_asset or len(maker_asset) != 42 or not maker_asset.startswith("0x"):
                raise ValueError("makerAsset must be a valid Ethereum address (42 characters starting with 0x)")
            if not taker_asset or len(taker_asset) != 42 or not taker_asset.startswith("0x"):
                raise ValueError("takerAsset must be a valid Ethereum address (42 characters starting with 0x)")
            if not maker_amount or maker_amount <= 0:
                raise ValueError("makerAmount must be a positive integer")
            if not taker_amount or taker_amount <= 0:
                raise ValueError("taker_amount must be a positive integer")
            
            try:
                fee_extension = FeeExtension(
                    makerAsset=maker_asset,
                    takerAsset=taker_asset,
                    makerAmount=maker_amount,
                    takerAmount=taker_amount
                )
                fee_info = await retrieve_order_fee(chain, fee_extension)
                return fee_info.model_dump()
            except Exception as e:
                raise ValueError(f"Failed to retrieve fee info: {str(e)}")

        @mcp.tool
        async def get_limit_order_by_hash(chain: int, order_hash: str) -> dict:
            """Get a specific limit order by its order hash on a specific chain.

            Args:
                chain: The blockchain chain ID (e.g., 1 for Ethereum, 137 for Polygon). Optional parameter, 1 by default
                order_hash: The unique order hash to retrieve. Required parameter

            Returns:
                Dictionary containing the limit order data
            """
            if not chain or chain <= 0:
                raise ValueError("Chain ID must be a positive integer")
            if not order_hash or len(order_hash) != 66 or not order_hash.startswith("0x"):
                raise ValueError("Order hash must be a valid 66-character hash starting with 0x")
            
            try:
                order = await fetch_order_by_hash(chain, order_hash)
                return order.model_dump()
            except Exception as e:
                raise ValueError(f"Failed to fetch order: {str(e)}")
