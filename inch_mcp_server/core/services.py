from uuid import uuid4

from fastapi_async_sqlalchemy import db
from sqlalchemy import select, delete

from .models import GetLimitOrdersV4Response, PostLimitOrderV4Request, FeeExtension, FeeInfoDTO
from .one_inch_service import OneInchService
from ..database import LimitOrder


one_inch_service = OneInchService()

async def fetch_and_store_orders(chain: int, address: str):
    orders = await one_inch_service.get_orders_by_address(chain, address)
    orders = [GetLimitOrdersV4Response(**order) for order in orders]
    retrieved_hashes = {order.orderHash for order in orders}
    query = (
        select(LimitOrder)
        .where((LimitOrder.blockchain_id == chain) & (LimitOrder.address == address))
    )
    result = (await db.session.scalars(query)).all()
    stored_hashes = {order.order_hash for order in result}
    hashes_to_delete = list(stored_hashes - retrieved_hashes)
    hashes_to_return = list(retrieved_hashes & stored_hashes)
    if hashes_to_delete:
        await db.session.execute(delete(LimitOrder).where(LimitOrder.order_hash.in_(hashes_to_delete)))
        await db.session.commit()
    orders = [order for order in orders if order.orderHash in hashes_to_return]
    return orders

async def retrieve_order_fee(chain: int, fee_extension: FeeExtension):
    fee_info = await one_inch_service.get_fee_info(chain, fee_extension.model_dump(mode="json"))
    fee_info = FeeInfoDTO(**fee_info)
    return fee_info


async def post_order(chain: int, order_data: PostLimitOrderV4Request):
    response = await one_inch_service.post_order(chain, order_data.model_dump(mode="json"))
    entry = LimitOrder(
        id=uuid4(),
        blockchain_id=chain,
        address=order_data.data.maker,
        order_hash=order_data.orderHash,
        data=order_data.model_dump(mode="json"),
    )
    db.session.add(entry)
    await db.session.commit()
    return response.json()
