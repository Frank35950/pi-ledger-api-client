from __future__ import annotations

import argparse
import csv
import io
import json

from pi_ledger_api import AsyncPiLedgerClient, PiLedgerClient


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _print_table(data: dict) -> None:
    if not isinstance(data, dict):
        _print_json(data)
        return

    key_width = max((len(str(key)) for key in data.keys()), default=0)
    for key, value in data.items():
        print(f"{str(key).ljust(key_width)}  {value}")


def _print_csv(data: dict) -> None:
    if not isinstance(data, dict):
        _print_json(data)
        return

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["field", "value"])
    for key, value in data.items():
        writer.writerow([key, value])
    print(buf.getvalue(), end="")


def _print_markdown(data: dict) -> None:
    if not isinstance(data, dict):
        _print_json(data)
        return

    print("| Field | Value |")
    print("| --- | --- |")
    for key, value in data.items():
        print(f"| {key} | {value} |")


def main() -> None:
    parser = argparse.ArgumentParser(description="Query Pi Network ledgers")
    parser.add_argument("--ledger-id", type=str, default="29023217", help="Ledger sequence or hash")
    parser.add_argument(
        "--resource",
        choices=["ledger", "transactions", "operations", "payments", "effects", "latest-summary"],
        default="ledger",
        help="Resource to fetch",
    )
    parser.add_argument("--limit", type=int, default=10, help="Maximum items to fetch")
    parser.add_argument("--cursor", type=str, default=None, help="Optional pagination cursor")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc", help="Response order")
    parser.add_argument("--format", choices=["json", "table", "csv", "markdown"], default="json", help="Output layout")
    parser.add_argument("--async", action="store_true", help="Use async client")
    args = parser.parse_args()

    if args.resource == "latest-summary":
        if args.async:
            import asyncio

            async def _run():
                async with AsyncPiLedgerClient() as client:
                    result = await client.latest_ledger_summary()
                    if args.format == "table":
                        _print_table(result)
                    elif args.format == "csv":
                        _print_csv(result)
                    elif args.format == "markdown":
                        _print_markdown(result)
                    else:
                        _print_json(result)

            asyncio.run(_run())
            return

        result = PiLedgerClient().latest_ledger_summary()
        if args.format == "table":
            _print_table(result)
        elif args.format == "csv":
            _print_csv(result)
        elif args.format == "markdown":
            _print_markdown(result)
        else:
            _print_json(result)
        return

    if args.async:
        import asyncio

        async def _run():
            async with AsyncPiLedgerClient() as client:
                if args.resource == "ledger":
                    result = await client.get_ledger(args.ledger_id)
                elif args.resource == "transactions":
                    result = await client.get_transactions(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
                elif args.resource == "operations":
                    result = await client.get_operations(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
                elif args.resource == "payments":
                    result = await client.get_payments(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)
                else:
                    result = await client.get_effects(args.ledger_id, limit=args.limit, cursor=args.cursor, order=args.order)

                if args.format == "table" and isinstance(result, dict):
                    _print_table(result)
                elif args.format == "csv" and isinstance(result, dict):
                    _print_csv(result)
                elif args.format == "markdown" and isinstance(result, dict):
                    _print_markdown(result)
                else:
                    _print_json(result)

        asyncio.run(_run())
        return

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

    if args.format == "table" and isinstance(result, dict):
        _print_table(result)
    elif args.format == "csv" and isinstance(result, dict):
        _print_csv(result)
    elif args.format == "markdown" and isinstance(result, dict):
        _print_markdown(result)
    else:
        _print_json(result)


if __name__ == "__main__":
    main()
