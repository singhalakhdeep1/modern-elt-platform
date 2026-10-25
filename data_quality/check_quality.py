"""Format-agnostic data quality checks for the ELT pipeline raw sources."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

_RAW_DIR = Path(__file__).resolve().parents[1] / "extractors" / "raw_data"

_PRIMARY_KEYS: dict[str, str] = {
    "crm_accounts": "account_id",
    "crm_contacts": "contact_id",
    "crm_opportunities": "opportunity_id",
    "billing_subscriptions": "sub_id",
    "billing_invoices": "invoice_id",
    "billing_refunds": "refund_id",
    "support_tickets": "ticket_id",
    "support_sla_events": "sla_id",
    "product_users": "user_id",
    "product_workspaces": "workspace_id",
    "product_events": "event_id",
}

_FRESHNESS_HOURS = 48


def _check_file(path: Path, issues: dict[str, int]) -> int:
    try:
        rows: list[dict] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        issues["invalid_files"] += 1
        return 0

    table = path.stem
    pk = _PRIMARY_KEYS.get(table)
    seen_ids: set[Any] = set()

    for row in rows:
        if not isinstance(row, dict):
            issues["invalid_rows"] += 1
            continue

        if pk:
            pk_val = row.get(pk)
            if not pk_val:
                issues["null_primary_keys"] += 1
            elif pk_val in seen_ids:
                issues["duplicate_rows"] += 1
            else:
                seen_ids.add(pk_val)

        ingest_raw = row.get("ingested_at")
        if ingest_raw:
            try:
                ingest_ts = datetime.fromisoformat(ingest_raw.rstrip("Z")).replace(tzinfo=UTC)
                if datetime.now(UTC) - ingest_ts > timedelta(hours=_FRESHNESS_HOURS):
                    issues["stale_rows"] += 1
            except (ValueError, TypeError):
                pass

    return len(rows)


def run_checks() -> dict[str, Any]:
    files = sorted(_RAW_DIR.glob("*.json"))
    issues: dict[str, int] = {
        "invalid_files": 0,
        "invalid_rows": 0,
        "null_primary_keys": 0,
        "duplicate_rows": 0,
        "stale_rows": 0,
    }
    total_rows = 0
    for f in files:
        total_rows += _check_file(f, issues)

    hard_failures = issues["invalid_files"] + issues["invalid_rows"] + issues["null_primary_keys"] + issues["duplicate_rows"]

    return {
        "files_scanned": len(files),
        "rows_scanned": total_rows,
        **issues,
        "passed": hard_failures == 0,
        "timestamp": datetime.now(UTC).isoformat(),
    }


if __name__ == "__main__":
    result = run_checks()
    print(json.dumps(result, indent=2))
