from __future__ import annotations


class PiLedgerError(RuntimeError):
    """Base exception for Pi ledger API errors."""


class PiLedgerAPIError(PiLedgerError):
    """Raised for failed API responses or invalid data."""


class PiLedgerNotFoundError(PiLedgerAPIError):
    """Raised when the requested resource does not exist."""


class PiLedgerRateLimitError(PiLedgerAPIError):
    """Raised when the API rate limit is exceeded."""


class PiLedgerTimeoutError(PiLedgerAPIError):
    """Raised when the API request times out."""
