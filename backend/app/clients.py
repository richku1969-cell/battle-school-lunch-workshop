from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.errors import (
    neis_invalid_response_error,
    neis_rate_limited_error,
    neis_timeout_error,
    neis_unauthorized_error,
)


class NeisClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._timeout = httpx.Timeout(settings.neis_read_timeout, connect=settings.neis_connect_timeout)

    async def fetch_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = {
            "Key": self._settings.neis_api_key,
            "Type": "json",
            **params,
        }
        try:
            async with httpx.AsyncClient(base_url=self._settings.neis_base_url, timeout=self._timeout) as client:
                response = await client.get(path, params=query)
        except httpx.TimeoutException as exc:
            raise neis_timeout_error() from exc
        except httpx.HTTPError as exc:
            raise neis_timeout_error() from exc

        if response.status_code == 429:
            raise neis_rate_limited_error()
        if response.status_code == 401:
            raise neis_unauthorized_error()
        if response.status_code == 404:
            return {}
        if response.status_code >= 500:
            raise neis_timeout_error()
        if response.status_code >= 400:
            raise neis_invalid_response_error()

        response.encoding = "utf-8"
        payload = response.json()
        if not isinstance(payload, dict):
            raise neis_invalid_response_error()
        return payload
