import os

import httpx
from typing import Any, Dict

from starlette.exceptions import HTTPException


class OneInchService:
    def __init__(self):
        self.base_url = "https://api.1inch.dev/orderbook/v4.0/"
        self.api_key = os.getenv("INCH_API_KEY")
        self._client = httpx.AsyncClient(base_url=self.base_url)
        self.headers = {"Accepts": "application/json", "Authorization": self.api_key}

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()

    async def get_orders_by_address(self, chain: int, address: str):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}/address/{address}"
        params = {
                "page": 1,
                "limit": 100,
                "statuses": "1,2,3"
            }
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching orders: {response.text}")
        return response.json()

    async def get_fee_info(self, chain: int, params: dict):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}/fee-info"
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching fee: {response.text}")
        return response.json()

    async def post_order(self, chain: int, data: Dict[str, Any]):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}"
        response = await self._client.post(endpoint, json=data, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error posting order: {response.json().get("message")}")
        return response
