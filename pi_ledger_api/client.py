from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class PiLedgerClient:
    """Simple read-only client for the Pi mainnet ledger API."""

    def __init__(self, base_url: str = "https://api.mainnet.minepi.com", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_ledger(self, ledger_id: int | str) -> Dict[str, Any]:
        """Fetch a single ledger by numeric sequence or ledger hash."""
        return self._request(f"/ledgers/{ledger_id}")

    def list_ledgers(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """List ledgers in pagination order."""
        params = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return self._request("/ledgers", params=params)

    def get_transactions(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch transactions for a given ledger."""
        params = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(f"/ledgers/{ledger_id}/transactions", params=params)

    def get_operations(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch operations for a given ledger."""
        params = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(f"/ledgers/{ledger_id}/operations", params=params)

    def get_payments(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch payment operations for a given ledger."""
        params = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(f"/ledgers/{ledger_id}/payments", params=params)

    def get_effects(
        self,
        ledger_id: int | str,
        limit: int = 100,
        cursor: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """Fetch effects for a given ledger."""
        params = {"limit": limit, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(f"/ledgers/{ledger_id}/effects", params=params)
