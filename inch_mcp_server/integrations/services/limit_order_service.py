from typing import List
from uuid import uuid4

from fastapi_async_sqlalchemy import db
from sqlalchemy import delete, select

from inch_mcp_server.database import LimitOrder
from inch_mcp_server.utils.logger_setup import setup_logger
from inch_mcp_server.core.models import FeeExtension, FeeInfoDTO, GetLimitOrdersV4Response, PostLimitOrderV4Request, LimitOrderV4Response, GetLimitOrdersCountV4Response, GetActiveUniquePairsResponse
from inch_mcp_server.integrations.api.limit_order_api_client import LimitOrderAPIClient

logger = setup_logger("services")


class LimitOrderService:
    """Service for handling limit order operations using the 1inch API client."""
    
    def __init__(self, api_client: LimitOrderAPIClient):
        """Initialize the service with an API client.
        
        Args:
            api_client: LimitOrderAPIClient instance (injected dependency).
        """
        self.api_client = api_client

    async def fetch_and_store_orders(self, chain: int, address: str):
        """Fetch orders from API and synchronize with database."""
        orders = await self.api_client.get_orders_by_address(chain, address)
        orders = [GetLimitOrdersV4Response(**order) for order in orders]
        logger.info("Fetched {} orders".format(len(orders)))
        retrieved_hashes = {order.orderHash for order in orders}
        logger.info("retrieved from api: {}".format(retrieved_hashes))
        query = select(LimitOrder).where((LimitOrder.blockchain_id == chain) & (LimitOrder.address == address.lower()))
        result = (await db.session.scalars(query)).all()
        stored_hashes = {order.order_hash for order in result}
        logger.info("retrieved from db: {}".format(stored_hashes))
        hashes_to_delete = list(stored_hashes - retrieved_hashes)
        hashes_to_return = list(retrieved_hashes & stored_hashes)
        logger.info("created: {}".format(hashes_to_return))
        logger.info("outdated: {}".format(hashes_to_delete))
        if hashes_to_delete:
            await db.session.execute(delete(LimitOrder).where(LimitOrder.order_hash.in_(hashes_to_delete)))
            await db.session.commit()
        orders = [order for order in orders if order.orderHash in hashes_to_return]
        return orders

    async def retrieve_order_fee(self, chain: int, fee_extension: FeeExtension):
        """Retrieve fee information for a limit order."""
        fee_info = await self.api_client.get_fee_info(chain, fee_extension.model_dump(mode="json"))
        fee_info = FeeInfoDTO(**fee_info)
        logger.info("for {} and fee ext {} got fee info {}".format(chain, fee_extension, fee_info))
        return fee_info

    async def fetch_order_by_hash(self, chain: int, order_hash: str):
        """Fetch a specific order by its hash."""
        try:
            raw_order = await self.api_client.get_order_by_hash(chain, order_hash)
            logger.info("Raw API response for hash {}: {}".format(order_hash, raw_order))
            order = LimitOrderV4Response.model_validate(raw_order)
            logger.info("Successfully validated order with hash: {}".format(order_hash))
            return order
        except Exception as e:
            logger.error("Failed to fetch/validate order with hash {}: {}".format(order_hash, str(e)))
            raise

    async def post_order(self, chain: int, order_data: PostLimitOrderV4Request):
        """Post a new limit order."""
        logger.info("posting for {} order {}".format(chain, order_data))
        response = await self.api_client.post_order(chain, order_data.model_dump(mode="json"))
        entry = LimitOrder(
            id=uuid4(),
            blockchain_id=chain,
            address=order_data.data.maker.lower(),
            order_hash=order_data.orderHash,
            data=order_data.model_dump(mode="json"),
        )
        logger.info("storing to db for {} with {} order {}".format(chain, order_data.orderHash, order_data))
        db.session.add(entry)
        await db.session.commit()
        return response.json()

    async def fetch_orders_count(self, chain: int, statuses: List[int], taker_asset: str = None, maker_asset: str = None):
        """Fetch count of orders matching specified criteria."""
        try:
            count_response = await self.api_client.get_orders_count(chain, statuses, taker_asset, maker_asset)
            logger.info("Fetched order count for chain {}, statuses {}: {}".format(chain, statuses, count_response))
            count_data = GetLimitOrdersCountV4Response.model_validate(count_response)
            return count_data
        except Exception as e:
            logger.error("Failed to fetch order count for chain {}, statuses {}: {}".format(chain, statuses, str(e)))
            raise

    async def fetch_unique_active_pairs(self, chain: int = 1, page: int = 1, limit: int = 100):
        """Fetch unique active trading pairs."""
        try:
            pairs_response = await self.api_client.get_unique_active_pairs(chain, page, limit)
            logger.info("Fetched unique active pairs for chain {}, page {}, limit {}: {}".format(chain, page, limit, pairs_response))
            pairs_data = GetActiveUniquePairsResponse.model_validate(pairs_response)
            return pairs_data
        except Exception as e:
            logger.error("Failed to fetch unique active pairs for chain {}, page {}, limit {}: {}".format(chain, page, limit, str(e)))
            raise
