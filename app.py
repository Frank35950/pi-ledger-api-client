from __future__ import annotations

import argparse

from flask import Flask, render_template_string, request

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
    ledger_id = request.args.get("ledger_id", default="29023217", type=int)
    client = PiLedgerClient()
    ledger = client.get_ledger(ledger_id)
    summary = build_summary(ledger)

    successful = int(summary.get("successful_transactions") or 0)
    failed = int(summary.get("failed_transactions") or 0)
    operations = int(summary.get("operation_count") or 0)

    max_bar = max(successful, failed, operations, 1)
    success_ratio = (successful / max_bar) * 100
    failure_ratio = (failed / max_bar) * 100
    operation_ratio = (operations / max_bar) * 100

    template = """
    <!doctype html>
    <html lang="en">
      <head>
        <title>Pi Ledger Dashboard</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          :root {
            --bg: #f3f6fb;
            --panel: #ffffff;
            --ink: #1f2937;
            --muted: #6b7280;
            --line: #e5e7eb;
            --brand: #2563eb;
            --success: #16a34a;
            --warning: #f59e0b;
            --danger: #dc2626;
            --shadow: rgba(15, 23, 42, 0.08);
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: var(--bg);
            color: var(--ink);
          }
          .container {
            max-width: 1100px;
            margin: 48px auto;
            padding: 24px;
          }
          .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: 0 8px 24px var(--shadow);
            padding: 24px;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 20px;
          }
          h1 {
            margin: 0;
            font-size: 2rem;
          }
          form {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
          }
          label {
            font-weight: 600;
            color: var(--muted);
          }
          input[type="number"] {
            padding: 10px 12px;
            width: 180px;
            border: 1px solid var(--line);
            border-radius: 10px;
            font-size: 1rem;
          }
          button {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            background: var(--brand);
            color: white;
            font-weight: 700;
            cursor: pointer;
          }
          .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin: 20px 0;
          }
          .stat-card {
            background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%);
            border: 1px solid #dfeafc;
            border-radius: 12px;
            padding: 16px;
          }
          .stat-label {
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
          }
          .stat-value {
            font-size: 1.6rem;
            font-weight: 700;
            margin-top: 8px;
          }
          .chart-card {
            margin-top: 24px;
            background: #f9fafb;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 18px;
          }
          .chart-row {
            margin: 14px 0;
          }
          .chart-head {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            margin-bottom: 6px;
          }
          .bar {
            height: 14px;
            width: 100%;
            background: #e5e7eb;
            border-radius: 999px;
            overflow: hidden;
          }
          .bar > span {
            display: block;
            height: 100%;
            border-radius: 999px;
          }
          .success { background: var(--success); }
          .warning { background: var(--warning); }
          .danger { background: var(--danger); }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 18px;
          }
          th, td {
            text-align: left;
            padding: 12px 10px;
            border-bottom: 1px solid var(--line);
            vertical-align: top;
          }
          th {
            width: 220px;
            color: var(--muted);
            font-weight: 600;
          }
          code {
            background: #f5f7fb;
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: 3px 6px;
            font-size: 0.9rem;
          }
          @media (max-width: 600px) {
            .header { align-items: flex-start; }
            form { width: 100%; }
            input[type="number"] { width: 100%; }
            button { width: 100%; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="panel">
            <div class="header">
              <h1>Pi Ledger Dashboard</h1>
              <form method="get">
                <label for="ledger_id">Ledger ID</label>
                <input id="ledger_id" name="ledger_id" type="number" min="1" value="{{ summary.sequence }}" />
                <button type="submit">Load</button>
              </form>
            </div>

            <div class="stats">
              <div class="stat-card">
                <div class="stat-label">Sequence</div>
                <div class="stat-value">{{ summary.sequence }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Successful</div>
                <div class="stat-value">{{ summary.successful_transactions }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-value">{{ summary.failed_transactions }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Operations</div>
                <div class="stat-value">{{ summary.operation_count }}</div>
              </div>
            </div>

            <div class="chart-card">
              <h2 style="margin-top: 0;">Activity Overview</h2>
              <div class="chart-row">
                <div class="chart-head">
                  <span>Successful Transactions</span>
                  <span>{{ summary.successful_transactions }}</span>
                </div>
                <div class="bar"><span class="success" style="width: {{ success_ratio }}%"></span></div>
              </div>
              <div class="chart-row">
                <div class="chart-head">
                  <span>Failed Transactions</span>
                  <span>{{ summary.failed_transactions }}</span>
                </div>
                <div class="bar"><span class="danger" style="width: {{ failure_ratio }}%"></span></div>
              </div>
              <div class="chart-row">
                <div class="chart-head">
                  <span>Operations</span>
                  <span>{{ summary.operation_count }}</span>
                </div>
                <div class="bar"><span class="warning" style="width: {{ operation_ratio }}%"></span></div>
              </div>
            </div>

            <table>
              {% for key, value in summary.items() %}
              <tr>
                <th>{{ key.replace('_', ' ').title() }}</th>
                <td><code>{{ value }}</code></td>
              </tr>
              {% endfor %}
            </table>
          </div>
        </div>
      </body>
    </html>
    """
    return render_template_string(
        template,
        summary=summary,
        success_ratio=success_ratio,
        failure_ratio=failure_ratio,
        operation_ratio=operation_ratio,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Pi Ledger dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
