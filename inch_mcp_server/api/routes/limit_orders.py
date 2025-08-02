"""Limit order API routes."""

from typing import List

from fastapi import APIRouter

from inch_mcp_server.dependencies import LimitOrderServiceDep
from inch_mcp_server.core.models import FeeExtension, PostLimitOrderV4Request

router = APIRouter(prefix="/orders", tags=["limit-orders"])


@router.get("")
async def get_orders(chain: int, address: str, service: LimitOrderServiceDep):
    """Fetch and store orders for a given chain and address."""
    return await service.fetch_and_store_orders(chain, address)


@router.get("/fee/{chain}")
async def get_fee(
    chain: int, 
    makerAsset: str, 
    takerAsset: str, 
    makerAmount: int, 
    takerAmount: int, 
    service: LimitOrderServiceDep
):
    """Get fee information for order parameters."""
    fee_extension = FeeExtension(
        makerAsset=makerAsset, 
        takerAsset=takerAsset, 
        makerAmount=makerAmount, 
        takerAmount=takerAmount
    )
    return await service.retrieve_order_fee(chain, fee_extension)


@router.post("")
async def store_order(chain: int, order: PostLimitOrderV4Request, service: LimitOrderServiceDep):
    """Store/post a new limit order."""
    return await service.post_order(chain, order)


@router.get("/{order_hash}")
async def get_order_by_hash(chain: int, order_hash: str, service: LimitOrderServiceDep):
    """Get a specific order by its hash."""
    return await service.fetch_order_by_hash(chain, order_hash)


@router.get("/count/{chain}")
async def get_orders_count(
    chain: int, 
    statuses: List[int], 
    service: LimitOrderServiceDep, 
    taker_asset: str = None, 
    maker_asset: str = None
):
    """Get count of orders matching the specified criteria."""
    return await service.fetch_orders_count(chain, statuses, taker_asset, maker_asset)


@router.get("/unique-active-pairs/{chain}")
async def get_unique_active_pairs(
    service: LimitOrderServiceDep, 
    chain: int = 1, 
    page: int = 1, 
    limit: int = 100
):
    """Get unique active trading pairs for a chain."""
    return await service.fetch_unique_active_pairs(chain, page, limit)