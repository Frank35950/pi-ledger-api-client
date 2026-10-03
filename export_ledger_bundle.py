from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from pi_ledger_api import PiLedgerClient

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def build_summary(ledger: dict) -> dict:
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


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, payload: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "value"])
        for key, value in payload.items():
            writer.writerow([key, value])


def write_yaml(path: Path, payload: dict) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed. Install with: pip install pyyaml")
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Pi ledger summary data in multiple formats")
    parser.add_argument("--ledger-id", type=int, default=29023217, help="Ledger sequence number to export")
    parser.add_argument("--output-dir", type=str, default="./exports", help="Directory to save exported files")
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=["json", "csv", "yaml"],
        default=["json", "csv", "yaml"],
        help="Export formats to generate",
    )
    args = parser.parse_args()

    client = PiLedgerClient()
    ledger = client.get_ledger(args.ledger_id)
    summary = build_summary(ledger)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for fmt in args.formats:
        filename = output_dir / f"ledger_{args.ledger_id}.{fmt}"
        if fmt == "json":
            write_json(filename, summary)
        elif fmt == "csv":
            write_csv(filename, summary)
        else:
            write_yaml(filename, summary)

    print(f"Exported ledger summary for #{args.ledger_id} to {output_dir}")
    for fmt in args.formats:
        print(f"- ledger_{args.ledger_id}.{fmt}")


if __name__ == "__main__":
    main()
