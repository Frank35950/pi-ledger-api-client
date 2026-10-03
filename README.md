# Pi Ledger API Client

A lightweight Python client for the Pi Network mainnet API. It provides easy access to ledger records and related resources such as transactions, operations, payments, and effects.

## Features

- Fetch a ledger by ID or hash
- List ledgers with pagination
- Fetch transactions, operations, payments, and effects for a ledger
- Built-in retry and timeout handling
- Simple CLI for quick testing

## Installation

```bash
pip install .
```

Or for local development:

```bash
pip install -e .
```

## Quick start

```python
from pi_ledger_api import PiLedgerClient

client = PiLedgerClient()
ledger = client.get_ledger(29023217)
print(ledger["sequence"])
print(ledger["hash"])
```

## CLI usage

```bash
python -m pi_ledger_api.cli --ledger-id 29023217
python -m pi_ledger_api.cli --ledger-id 29023217 --resource transactions --limit 10
```

## Example: fetch a ledger and print summary

```python
from pi_ledger_api import PiLedgerClient

client = PiLedgerClient()
ledger = client.get_ledger(29023217)
print(
    f"Ledger {ledger['sequence']} @ {ledger['closed_at']} "
    f"| successful={ledger['successful_transaction_count']} "
    f"failed={ledger['failed_transaction_count']}"
)
```

## API design

The client exposes helpers for:

- `get_ledger(ledger_id)`
- `list_ledgers(limit=100, cursor=None, order="desc")`
- `get_transactions(ledger_id, limit=100, cursor=None, order="desc")`
- `get_operations(ledger_id, limit=100, cursor=None, order="desc")`
- `get_payments(ledger_id, limit=100, cursor=None, order="desc")`
- `get_effects(ledger_id, limit=100, cursor=None, order="desc")`

## Notes

- The Pi Network API uses the public mainnet URL: `https://api.mainnet.minepi.com`
- Some responses include pagination fields such as `_links` and `embedded` depending on the endpoint.
- The client does not modify chain state; it is a read-only client for ledger data.
