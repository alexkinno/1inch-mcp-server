import os
from typing import Any, Dict, List

import httpx
from starlette.exceptions import HTTPException


class LimitOrderAPIClient:
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
        params = {"page": 1, "limit": 100, "statuses": "1,2,3"}
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

    async def get_order_by_hash(self, chain: int, order_hash: str):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}/order/{order_hash}"
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching order: {response.text}")
        return response.json()

    async def post_order(self, chain: int, data: Dict[str, Any]):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}"
        response = await self._client.post(endpoint, json=data, headers=self.headers)
        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=response.status_code, detail=f"Error posting order: {response.json().get("message")}"
            )
        return response

    async def get_orders_count(self, chain: int, statuses: List[int], taker_asset: str = None, maker_asset: str = None):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}/count"
        params = {}
        if statuses:
            params["statuses"] = ','.join(map(str, statuses))

        if taker_asset:
            params["takerAsset"] = taker_asset

        if maker_asset:
            params["makerAsset"] = maker_asset

        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching order count: {response.text}")
        return response.json()

    async def get_unique_active_pairs(self, chain: int = 1, page: int = 1, limit: int = 100):
        if not self._client:
            self._client = httpx.AsyncClient(base_url=self.base_url)
        endpoint = f"{chain}/unique-active-pairs"
        params = {"page": page, "limit": limit}
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching unique active pairs: {response.text}")
        return response.json()
