from pi_ledger_api import PiLedgerClient
import json


def print_ledger_summary(ledger_id: int) -> None:
    """Fetch and print a formatted summary for a given ledger."""
    client = PiLedgerClient()
    ledger = client.get_ledger(ledger_id)

    summary = {
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

    print(f"\n{'='*80}")
    print(f"Ledger Summary for Ledger #{ledger_id}")
    print(f"{'='*80}")
    print(json.dumps(summary, indent=2))
    print(f"{'='*80}\n")


if __name__ == "__main__":
    print_ledger_summary(29023217)
