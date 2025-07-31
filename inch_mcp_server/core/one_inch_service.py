import os

import httpx
from typing import Any, Dict, Optional

class OneInchService:
    def __init__(self):
        self.base_url = "https://api.1inch.dev/orderbook/v4.0/"
        self.api_key = os.getenv("INCH_API_KEY")
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()

    async def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {"Accepts": "application/json", "Authorization": self.api_key}
        response = await self._client.post(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    async def get_orders_by_address(self, chain: str, address: str):
        endpoint = f"{chain}/address/{address}"
        params = {
                "page": 1,
                "limit": 100,
                "statuses": "1,2,3"
            }
        url = f"{self.base_url}{endpoint}"
        headers = {"Accepts": "application/json", "Authorization": self.api_key}
        response = await self._client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post_order(self, chain: str, data: Dict[str, Any]) -> httpx.Response:
        endpoint = f"{chain}"
        response = await self._client.post(endpoint, json=data)
        response.raise_for_status()
        return response
