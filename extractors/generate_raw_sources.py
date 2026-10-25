"""Generate realistic raw source JSON files for the ELT pipeline demo."""
from __future__ import annotations

import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path


RNG = random.Random(42)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _past(days: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=RNG.randint(1, days))


# ---------------------------------------------------------------------------
# Domain-specific row builders
# ---------------------------------------------------------------------------

def _crm_accounts(n: int = 20) -> list[dict]:
    industries = ["SaaS", "Fintech", "HealthTech", "EdTech", "E-commerce", "Gaming"]
    statuses = ["active", "churned", "trial", "suspended"]
    regions = ["IN", "US", "EU", "APAC", "LATAM"]
    rows = []
    for i in range(1, n + 1):
        created = _past(365)
        rows.append({
            "account_id": f"acc_{i:04d}",
            "name": f"Customer Corp {i}",
            "industry": RNG.choice(industries),
            "arr_usd": round(RNG.uniform(1200, 120000), 2),
            "status": RNG.choice(statuses),
            "region": RNG.choice(regions),
            "created_at": _iso(created),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _crm_contacts(n: int = 40) -> list[dict]:
    roles = ["CEO", "CTO", "VP Engineering", "Product Manager", "Procurement"]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "contact_id": f"con_{i:04d}",
            "account_id": f"acc_{RNG.randint(1, 20):04d}",
            "name": f"Contact Person {i}",
            "email": f"contact{i}@example.com",
            "role": RNG.choice(roles),
            "is_active": RNG.choice([True, True, True, False]),
            "created_at": _iso(_past(300)),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _crm_opportunities(n: int = 30) -> list[dict]:
    stages = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
    rows = []
    for i in range(1, n + 1):
        created = _past(180)
        close = created + timedelta(days=RNG.randint(14, 90))
        rows.append({
            "opp_id": f"opp_{i:04d}",
            "account_id": f"acc_{RNG.randint(1, 20):04d}",
            "stage": RNG.choice(stages),
            "amount_usd": round(RNG.uniform(5000, 200000), 2),
            "probability": RNG.randint(10, 90),
            "close_date": _iso(close),
            "created_at": _iso(created),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _billing_subscriptions(n: int = 20) -> list[dict]:
    plans = ["starter", "growth", "pro", "enterprise"]
    statuses = ["active", "active", "active", "cancelled", "past_due"]
    rows = []
    for i in range(1, n + 1):
        started = _past(400)
        rows.append({
            "sub_id": f"sub_{i:04d}",
            "account_id": f"acc_{i:04d}",
            "plan": RNG.choice(plans),
            "mrr_usd": round(RNG.choice([99, 299, 599, 1499]) * RNG.uniform(0.9, 1.1), 2),
            "status": RNG.choice(statuses),
            "started_at": _iso(started),
            "cancelled_at": None,
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _billing_invoices(n: int = 60) -> list[dict]:
    statuses = ["paid", "paid", "paid", "open", "overdue", "void"]
    rows = []
    for i in range(1, n + 1):
        due = _past(120)
        paid = due + timedelta(days=RNG.randint(0, 10)) if RNG.random() > 0.2 else None
        rows.append({
            "invoice_id": f"inv_{i:04d}",
            "sub_id": f"sub_{RNG.randint(1, 20):04d}",
            "amount_usd": round(RNG.uniform(100, 5000), 2),
            "status": RNG.choice(statuses),
            "due_date": _iso(due),
            "paid_at": _iso(paid) if paid else None,
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _billing_refunds(n: int = 10) -> list[dict]:
    reasons = ["duplicate_charge", "service_outage", "customer_request", "error"]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "refund_id": f"ref_{i:04d}",
            "invoice_id": f"inv_{RNG.randint(1, 60):04d}",
            "amount_usd": round(RNG.uniform(50, 1000), 2),
            "reason": RNG.choice(reasons),
            "created_at": _iso(_past(90)),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _support_tickets(n: int = 50) -> list[dict]:
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "in_progress", "resolved", "closed"]
    categories = ["billing", "technical", "onboarding", "feature_request", "outage"]
    rows = []
    for i in range(1, n + 1):
        created = _past(90)
        resolved = created + timedelta(hours=RNG.randint(1, 72)) if RNG.random() > 0.3 else None
        rows.append({
            "ticket_id": f"tkt_{i:04d}",
            "account_id": f"acc_{RNG.randint(1, 20):04d}",
            "priority": RNG.choice(priorities),
            "status": RNG.choice(statuses),
            "category": RNG.choice(categories),
            "created_at": _iso(created),
            "resolved_at": _iso(resolved) if resolved else None,
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _support_sla_events(n: int = 50) -> list[dict]:
    sla_types = ["first_response", "resolution"]
    rows = []
    for i in range(1, n + 1):
        response_hours = round(RNG.uniform(0.5, 48), 1)
        sla_type = RNG.choice(sla_types)
        threshold = 4.0 if sla_type == "first_response" else 24.0
        rows.append({
            "sla_id": f"sla_{i:04d}",
            "ticket_id": f"tkt_{RNG.randint(1, 50):04d}",
            "sla_type": sla_type,
            "response_hours": response_hours,
            "threshold_hours": threshold,
            "breached": response_hours > threshold,
            "created_at": _iso(_past(90)),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _product_users(n: int = 80) -> list[dict]:
    roles = ["admin", "editor", "viewer", "developer"]
    rows = []
    for i in range(1, n + 1):
        created = _past(365)
        last_seen = created + timedelta(days=RNG.randint(0, 60))
        rows.append({
            "user_id": f"usr_{i:04d}",
            "workspace_id": f"ws_{RNG.randint(1, 15):04d}",
            "email": f"user{i}@example.com",
            "role": RNG.choice(roles),
            "is_active": RNG.choice([True, True, True, False]),
            "created_at": _iso(created),
            "last_seen_at": _iso(last_seen),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _product_workspaces(n: int = 15) -> list[dict]:
    plans = ["free", "starter", "pro", "enterprise"]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "workspace_id": f"ws_{i:04d}",
            "account_id": f"acc_{RNG.randint(1, 20):04d}",
            "name": f"Workspace {i}",
            "plan": RNG.choice(plans),
            "seat_count": RNG.randint(1, 50),
            "created_at": _iso(_past(400)),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


def _product_events(n: int = 200) -> list[dict]:
    event_names = [
        "page_view", "button_click", "feature_used", "api_call",
        "export_created", "invite_sent", "login", "logout",
    ]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "event_id": f"evt_{i:05d}",
            "user_id": f"usr_{RNG.randint(1, 80):04d}",
            "workspace_id": f"ws_{RNG.randint(1, 15):04d}",
            "event_name": RNG.choice(event_names),
            "page": RNG.choice(["/dashboard", "/settings", "/reports", "/api"]),
            "duration_ms": RNG.randint(50, 3000),
            "created_at": _iso(_past(30)),
            "ingested_at": _iso(datetime.now(UTC)),
        })
    return rows


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_BUILDERS: dict[str, callable] = {
    "crm_accounts": _crm_accounts,
    "crm_contacts": _crm_contacts,
    "crm_opportunities": _crm_opportunities,
    "billing_subscriptions": _billing_subscriptions,
    "billing_invoices": _billing_invoices,
    "billing_refunds": _billing_refunds,
    "support_tickets": _support_tickets,
    "support_sla_events": _support_sla_events,
    "product_users": _product_users,
    "product_workspaces": _product_workspaces,
    "product_events": _product_events,
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    contracts_path = root / "extractors" / "source_contracts.json"
    output_dir = root / "extractors" / "raw_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    contracts = json.loads(contracts_path.read_text(encoding="utf-8"))
    for source in contracts["sources"]:
        source_name = source["name"]
        for table_name in source["tables"]:
            key = f"{source_name}_{table_name}"
            builder = _BUILDERS.get(key)
            if builder is None:
                print(f"WARNING: no builder for {key}, skipping")
                continue
            rows = builder()
            out_file = output_dir / f"{key}.json"
            out_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"Wrote {len(rows)} rows to {out_file.name}")


if __name__ == "__main__":
    main()
