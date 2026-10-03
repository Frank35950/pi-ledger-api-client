# Pi Ledger API Client

A lightweight Python client for the Pi Network mainnet API. It provides easy access to ledger records and related resources such as transactions, operations, payments, and effects.

## Features

- Fetch a ledger by ID or hash
- List ledgers with pagination
- Fetch transactions, operations, payments, and effects for a ledger
- Built-in retry and timeout handling
- Async and sync clients
- `latest_ledger_summary()` helper for quick summaries
- CLI support for quick testing
- Export utility for JSON/CSV/YAML bundles

## Installation

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

## Async usage

```python
import asyncio
from pi_ledger_api import AsyncPiLedgerClient

async def main():
    async with AsyncPiLedgerClient() as client:
        summary = await client.latest_ledger_summary()
        print(summary)

asyncio.run(main())
```

## CLI usage

```bash
python -m pi_ledger_api.cli --resource latest-summary
python -m pi_ledger_api.cli --resource latest-summary --async
python -m pi_ledger_api.cli --ledger-id 29023217 --resource transactions --limit 10
python -m pi_ledger_api.cli --resource latest-summary --format markdown
python -m pi_ledger_api.cli --resource latest-summary --format yaml
```

## Export bundles

```bash
python export_ledger_bundle.py --ledger-id 29023217 --output-dir ./exports --formats json csv yaml
```

This writes:

- `./exports/ledger_29023217.json`
- `./exports/ledger_29023217.csv`
- `./exports/ledger_29023217.yaml`

## API design

The client exposes helpers for:

- `get_ledger(ledger_id)`
- `list_ledgers(limit=100, cursor=None, order="desc")`
- `get_transactions(ledger_id, limit=100, cursor=None, order="desc")`
- `get_operations(ledger_id, limit=100, cursor=None, order="desc")`
- `get_payments(ledger_id, limit=100, cursor=None, order="desc")`
- `get_effects(ledger_id, limit=100, cursor=None, order="desc")`
- `latest_ledger_summary()`

## Notes

- The Pi Network API uses the public mainnet URL: `https://api.mainnet.minepi.com`
- The client does not modify chain state; it is a read-only client for ledger data.
