from uuid import uuid4

from fastapi_async_sqlalchemy import db
from sqlalchemy import delete, select

from ..database import LimitOrder
from ..utils.logger_setup import setup_logger
from .models import FeeExtension, FeeInfoDTO, GetLimitOrdersV4Response, PostLimitOrderV4Request
from .one_inch_service import OneInchService

logger = setup_logger("services")
one_inch_service = OneInchService()


async def fetch_and_store_orders(chain: int, address: str):
    orders = await one_inch_service.get_orders_by_address(chain, address)
    orders = [GetLimitOrdersV4Response(**order) for order in orders]
    logger.info("Fetched {} orders".format(len(orders)))
    retrieved_hashes = {order.orderHash for order in orders}
    logger.info("retrieved from api: {}".format(retrieved_hashes))
    query = select(LimitOrder).where((LimitOrder.blockchain_id == chain) & (LimitOrder.address == address))
    result = (await db.session.scalars(query)).all()
    stored_hashes = {order.order_hash for order in result}
    logger.info("retrieved from db: {}".format(stored_hashes))
    hashes_to_delete = list(stored_hashes - retrieved_hashes)
    hashes_to_return = list(retrieved_hashes & stored_hashes)
    logger.info("created: {}".format(hashes_to_return))
    if hashes_to_delete:
        logger.info("outdated: {}".format(hashes_to_delete))
        await db.session.execute(delete(LimitOrder).where(LimitOrder.order_hash.in_(hashes_to_delete)))
        await db.session.commit()
    #orders = [order for order in orders if order.orderHash in hashes_to_return]
    return orders


async def retrieve_order_fee(chain: int, fee_extension: FeeExtension):
    fee_info = await one_inch_service.get_fee_info(chain, fee_extension.model_dump(mode="json"))
    fee_info = FeeInfoDTO(**fee_info)
    logger.info("for {} and fee ext {} got fee info {}".format(chain, fee_extension, fee_info))
    return fee_info


async def post_order(chain: int, order_data: PostLimitOrderV4Request):
    logger.info("posting for {} order {}".format(chain, order_data))
    response = await one_inch_service.post_order(chain, order_data.model_dump(mode="json"))
    entry = LimitOrder(
        id=uuid4(),
        blockchain_id=chain,
        address=order_data.data.maker,
        order_hash=order_data.orderHash,
        data=order_data.model_dump(mode="json"),
    )
    logger.info("storing to db for {} with {} order {}".format(chain, order_data.orderHash, order_data))
    db.session.add(entry)
    await db.session.commit()
    return response.json()
