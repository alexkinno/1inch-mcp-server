"""Tool handler for the 1inch Limit Order Protocol MCP Server."""
from typing import List

from ..core.one_inch_service import OneInchService
from ..core.services import fetch_and_store_orders, retrieve_order_fee, fetch_order_by_hash, fetch_orders_count, fetch_unique_active_pairs
from ..core.models import FeeExtension, FeeInfoDTO
from ..utils import validate_evm_address, validate_hash


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
            validate_evm_address(address, "address", required=True)
            
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

            validate_evm_address(maker_asset, "makerAsset", required=True)
            validate_evm_address(taker_asset, "takerAsset", required=True)

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
            validate_hash(order_hash, "Order hash", expected_length=66, required=True)
            
            try:
                order = await fetch_order_by_hash(chain, order_hash)
                return order.model_dump()
            except Exception as e:
                raise ValueError(f"Failed to fetch order: {str(e)}")

        @mcp.tool
        async def get_limit_orders_count_by_filters(chain: int, statuses: List[int], taker_asset: str = None,
                                                    maker_asset: str = None) -> dict:
            """Get count of limit orders filtered by specified criteria (statuses).

            Args:
                chain: The blockchain chain ID (e.g., 1 for Ethereum, 137 for Polygon). Optional parameter, defaults to 1
                statuses: list of statuses to filter by. Valid statuses: 1 - Valid orders, 2 - Temporarily invalid orders, 3 - Invalid orders. Optional parameter, defaults to empty list
                taker_asset: The token address that makers want to buy. Optional parameter
                maker_asset: The token address that makers want to sell. Optional parameter

            Returns:
                Dictionary containing the count of orders matching the specified filters
            """
            if not chain or chain <= 0:
                raise ValueError("Chain ID must be a positive integer")
            if not statuses:
                raise ValueError("Statuses parameter is required")
            
            # Validate statuses format
            if any(status not in [1, 2, 3] for status in statuses):
                raise ValueError("Statuses must be a list of integers (1, 2, or 3)")
            
            # Validate asset addresses if provided
            validate_evm_address(taker_asset, "taker_asset", required=False)
            validate_evm_address(maker_asset, "maker_asset", required=False)
            
            try:
                count_data = await fetch_orders_count(chain, statuses, taker_asset, maker_asset)
                return count_data.model_dump()
            except Exception as e:
                raise ValueError(f"Failed to fetch order count: {str(e)}")

        @mcp.tool
        async def get_unique_active_token_pairs(chain: int = 1, page: int = 1, limit: int = 100) -> dict:
            """Get unique active token pairs available for limit orders on a specific chain.

            Args:
                chain: The blockchain chain ID (e.g., 1 for Ethereum, 137 for Polygon). Optional parameter, defaults to 1
                page: Page number for pagination. Optional parameter, defaults to 1
                limit: Number of pairs per page (1-100). Optional parameter, defaults to 100

            Returns:
                Dictionary containing the list of unique active token pairs and pagination metadata
            """
            if not chain or chain <= 0:
                raise ValueError("Chain ID must be a positive integer")
            if not page or page <= 0:
                raise ValueError("Page must be a positive integer")
            if not limit or limit <= 0 or limit > 100:
                raise ValueError("Limit must be a positive integer between 1 and 100")
            
            try:
                pairs_data = await fetch_unique_active_pairs(chain, page, limit)
                return pairs_data.model_dump()
            except Exception as e:
                raise ValueError(f"Failed to fetch unique active pairs: {str(e)}")
