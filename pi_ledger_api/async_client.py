from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import aiohttp

from .exceptions import (
    PiLedgerAPIError,
    PiLedgerNotFoundError,
    PiLedgerRateLimitError,
    PiLedgerTimeoutError,
)


class AsyncPiLedgerClient:
    """Async read-only client for the Pi Network mainnet ledger API."""

    def __init__(
        self,
        base_url: str = "https://api.mainnet.minepi.com",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncPiLedgerClient":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    def _pagination_params(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        if limit < 1:
            raise ValueError("limit must be greater than 0")
        params: Dict[str, Any] = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return params

    async def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        session = await self._ensure_session()

        for attempt in range(self.max_retries + 1):
            try:
                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 429:
                        if attempt == self.max_retries:
                            raise PiLedgerRateLimitError(f"Rate limit exceeded for {url}")
                        await asyncio.sleep(self.backoff_factor * (2**attempt))
                        continue

                    if response.status == 404:
                        raise PiLedgerNotFoundError(f"Resource not found for {url}")

                    if response.status >= 500:
                        if attempt == self.max_retries:
                            text = await response.text()
                            raise PiLedgerAPIError(
                                f"Server error {response.status} for {url}: {text[:200]}"
                            )
                        await asyncio.sleep(self.backoff_factor * (2**attempt))
                        continue

                    if response.status >= 400:
                        text = await response.text()
                        raise PiLedgerAPIError(
                            f"Request failed for {url} ({response.status}): {text[:200]}"
                        )

                    try:
                        payload = await response.json()
                    except ValueError as exc:
                        raise PiLedgerAPIError(f"Invalid JSON response from {url}") from exc
                    return payload

            except asyncio.TimeoutError as exc:
                if attempt == self.max_retries:
                    raise PiLedgerTimeoutError(f"Request timed out for {url}") from exc
                await asyncio.sleep(self.backoff_factor * (2**attempt))
            except aiohttp.ClientError as exc:
                if attempt == self.max_retries:
                    raise PiLedgerAPIError(f"HTTP request failed for {url}: {exc}") from exc
                await asyncio.sleep(self.backoff_factor * (2**attempt))

        raise PiLedgerAPIError(f"Request failed unexpectedly for {url}")

    async def get_ledger(self, ledger_id: int | str) -> Dict[str, Any]:
        """Fetch a single ledger by numeric sequence or hash."""
        return await self._request(f"/ledgers/{ledger_id}")

    async def list_ledgers(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """List ledgers with pagination support."""
        return await self._request(
            "/ledgers", params=self._pagination_params(limit=limit, cursor=cursor, order=order)
        )

    async def get_transactions(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch transactions for a ledger."""
        return await self._request(
            f"/ledgers/{ledger_id}/transactions",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    async def get_operations(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch operations for a ledger."""
        return await self._request(
            f"/ledgers/{ledger_id}/operations",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    async def get_payments(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch payment operations for a ledger."""
        return await self._request(
            f"/ledgers/{ledger_id}/payments",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    async def get_effects(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch effects for a ledger."""
        return await self._request(
            f"/ledgers/{ledger_id}/effects",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    async def latest_ledger_summary(self) -> Dict[str, Any]:
        """Fetch the latest ledger and return a summary."""
        ledgers = await self.list_ledgers(limit=1, order="desc")
        records = ledgers.get("_embedded", {}).get("records", [])
        if not records:
            raise PiLedgerAPIError("No ledger records found")
        ledger = records[0]
        return {
            "sequence": ledger.get("sequence"),
            "hash": ledger.get("hash"),
            "closed_at": ledger.get("closed_at"),
            "successful_transactions": ledger.get("successful_transaction_count"),
            "failed_transactions": ledger.get("failed_transaction_count"),
            "operation_count": ledger.get("operation_count"),
            "total_coins": ledger.get("total_coins"),
            "base_fee_in_stroops": ledger.get("base_fee_in_stroops"),
            "protocol_version": ledger.get("protocol_version"),
        }

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self.session:
            await self.session.close()
