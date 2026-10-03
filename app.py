from __future__ import annotations

import argparse

from flask import Flask, render_template_string

from pi_ledger_api import PiLedgerClient

app = Flask(__name__)


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


@app.route("/")
def index():
    client = PiLedgerClient()
    ledger = client.get_ledger(29023217)
    summary = build_summary(ledger)

    template = """
    <!doctype html>
    <html>
      <head>
        <title>Pi Ledger Summary</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; background: #f4f6f8; }
          .card { max-width: 800px; margin: auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
          table { width: 100%; border-collapse: collapse; }
          th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eaeaea; }
          th { width: 220px; }
          code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Pi Ledger Summary</h1>
          <table>
            {% for key, value in summary.items() %}
            <tr>
              <th>{{ key.replace('_', ' ').title() }}</th>
              <td><code>{{ value }}</code></td>
            </tr>
            {% endfor %}
          </table>
        </div>
      </body>
    </html>
    """
    return render_template_string(template, summary=summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple Flask dashboard for Pi ledger summaries")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
