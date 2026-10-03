import asyncio

from pi_ledger_api import AsyncPiLedgerClient


async def main():
    async with AsyncPiLedgerClient() as client:
        ledger = await client.get_ledger(29023217)
        print(f"Ledger {ledger['sequence']} fetched asynchronously")
        print(f"Hash: {ledger['hash']}")
        print(f"Closed at: {ledger['closed_at']}")
        print()

        latest_summary = await client.latest_ledger_summary()
        print(f"Latest ledger sequence: {latest_summary['sequence']}")
        print(f"Successful transactions: {latest_summary['successful_transactions']}")
        print(f"Failed transactions: {latest_summary['failed_transactions']}")
        print(f"Operations: {latest_summary['operation_count']}")


if __name__ == "__main__":
    asyncio.run(main())
