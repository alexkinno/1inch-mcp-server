from .models import GetLimitOrdersV4Response
from .one_inch_service import OneInchService
# from .db import save_order_to_db  # hypothetical

one_inch_service = OneInchService()

async def fetch_and_store_orders(chain: str, address: str):  # TODO: check db
    orders = await one_inch_service.get_orders_by_address(chain, address)
    orders = [GetLimitOrdersV4Response(**order) for order in orders]
    return orders


async def post_order(chain: str, order_data: dict):
    response = await one_inch_service.post_order(chain, order_data)
    return response.json()
