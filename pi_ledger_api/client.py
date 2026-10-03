from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .exceptions import (
    PiLedgerAPIError,
    PiLedgerNotFoundError,
    PiLedgerRateLimitError,
    PiLedgerTimeoutError,
)


class PiLedgerClient:
    """Read-only client for the Pi Network mainnet ledger API."""

    def __init__(
        self,
        base_url: str = "https://api.mainnet.minepi.com",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = session or requests.Session()

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

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"

        import time

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
            except requests.exceptions.Timeout as exc:
                if attempt == self.max_retries:
                    raise PiLedgerTimeoutError(f"Request timed out for {url}") from exc
                time.sleep(self.backoff_factor * (2**attempt))
                continue
            except requests.exceptions.RequestException as exc:
                raise PiLedgerAPIError(f"HTTP request failed for {url}: {exc}") from exc

            if response.status_code == 429:
                if attempt == self.max_retries:
                    raise PiLedgerRateLimitError(f"Rate limit exceeded for {url}")
                time.sleep(self.backoff_factor * (2**attempt))
                continue

            if response.status_code == 404:
                raise PiLedgerNotFoundError(f"Resource not found for {url}")

            if response.status_code >= 500:
                if attempt == self.max_retries:
                    raise PiLedgerAPIError(
                        f"Server error {response.status_code} for {url}: {response.text[:200]}"
                    )
                time.sleep(self.backoff_factor * (2**attempt))
                continue

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise PiLedgerAPIError(f"Request failed for {url}: {response.text[:200]}") from exc

            try:
                payload = response.json()
            except ValueError as exc:
                raise PiLedgerAPIError(f"Invalid JSON response from {url}") from exc
            return payload

        raise PiLedgerAPIError(f"Request failed unexpectedly for {url}")

    def get_ledger(self, ledger_id: int | str) -> Dict[str, Any]:
        """Fetch a single ledger by numeric sequence or hash."""
        return self._request(f"/ledgers/{ledger_id}")

    def list_ledgers(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """List ledgers with pagination support."""
        return self._request("/ledgers", params=self._pagination_params(limit=limit, cursor=cursor, order=order))

    def get_transactions(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch transactions for a ledger."""
        return self._request(
            f"/ledgers/{ledger_id}/transactions",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    def get_operations(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch operations for a ledger."""
        return self._request(
            f"/ledgers/{ledger_id}/operations",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    def get_payments(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch payment operations for a ledger."""
        return self._request(
            f"/ledgers/{ledger_id}/payments",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    def get_effects(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch effects for a ledger."""
        return self._request(
            f"/ledgers/{ledger_id}/effects",
            params=self._pagination_params(limit=limit, cursor=cursor, order=order),
        )

    def latest_ledger_summary(self) -> Dict[str, Any]:
        """Fetch the latest ledger and return a summary."""
        ledgers = self.list_ledgers(limit=1, order="desc")
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
