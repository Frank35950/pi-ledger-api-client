from __future__ import annotations

import argparse
import json

from pi_ledger_api import PiLedgerClient


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Query Pi Network ledgers")
    parser.add_argument("--ledger-id", type=str, default="29023217", help="Ledger sequence or hash")
    parser.add_argument("--resource", choices=["ledger", "transactions", "operations", "payments", "effects"], default="ledger")
    parser.add_argument("--limit", type=int, default=10, help="Number of items to fetch")
    parser.add_argument("--cursor", type=str, default=None, help="Paging cursor for API pagination")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc")
    args = parser.parse_args()

    client = PiLedgerClient()

    if args.resource == "ledger":
        result = client.get_ledger(args.ledger_id)
    elif args.resource == "transactions":
        result = client.get_transactions(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
    elif args.resource == "operations":
        result = client.get_operations(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
    elif args.resource == "payments":
        result = client.get_payments(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
    else:
        result = client.get_effects(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)

    _print_json(result)


if __name__ == "__main__":
    main()
