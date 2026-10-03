from pi_ledger_api import PiLedgerClient


if __name__ == "__main__":
    client = PiLedgerClient()
    ledger = client.get_ledger(29023217)

    print(f"Ledger sequence: {ledger.get('sequence')}")
    print(f"Hash: {ledger.get('hash')}")
    print(f"Closed at: {ledger.get('closed_at')}")
    print(f"Successful txs: {ledger.get('successful_transaction_count')}")
    print(f"Failed txs: {ledger.get('failed_transaction_count')}")
