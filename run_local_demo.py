"""Full ELT pipeline demo: generate → load → dbt transform → report KPIs."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(cmd: list[str], cwd: Path | None = None) -> int:
    result = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=False)
    return result.returncode


def step_generate() -> None:
    print("\n=== Step 1: Generate raw source data ===")
    from extractors.generate_raw_sources import main as generate_raw_sources
    generate_raw_sources()
    print("Raw sources written to extractors/raw_data/")


def step_load(db_path: Path) -> None:
    print("\n=== Step 2: Load raw data into DuckDB ===")
    from extractors.loader import load_to_duckdb
    load_to_duckdb(db_path)


def step_dbt(db_path: Path) -> int:
    print("\n=== Step 3: dbt run (staging + marts) ===")
    dbt_dir = ROOT / "dbt"
    env = {**os.environ, "DBT_DUCKDB_PATH": str(db_path)}
    rc = subprocess.run(
        ["dbt", "run", "--profiles-dir", str(dbt_dir)],
        cwd=dbt_dir,
        env=env,
    ).returncode
    return rc


def step_quality() -> dict:
    print("\n=== Step 4: Data quality checks ===")
    from data_quality.check_quality import run_checks
    quality = run_checks()
    output_path = ROOT / "data_quality" / "quality_summary.json"
    output_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return quality


def step_kpi_report(db_path: Path) -> dict:
    print("\n=== Step 5: KPI summary from mart tables ===")
    try:
        import duckdb
        con = duckdb.connect(str(db_path), read_only=True)

        mrr_row = con.execute(
            "SELECT count(*) as accounts, sum(current_mrr_usd) as total_mrr, "
            "sum(arr_usd) as total_arr FROM mart_mrr"
        ).fetchone()

        churn_row = con.execute(
            "SELECT avg(churn_rate_pct) as avg_churn_rate, "
            "count(*) FILTER (WHERE fully_churned) as fully_churned_accounts "
            "FROM mart_churn"
        ).fetchone()

        act_row = con.execute(
            "SELECT count(*) as total_workspaces, "
            "count(*) FILTER (WHERE is_activated) as activated_workspaces, "
            "avg(activation_rate_pct) as avg_activation_rate "
            "FROM mart_activation"
        ).fetchone()

        sla_row = con.execute(
            "SELECT avg(breach_rate_pct) as avg_breach_rate, "
            "count(*) FILTER (WHERE sla_health = 'excellent') as excellent_accounts "
            "FROM mart_support_sla"
        ).fetchone()

        con.close()

        report = {
            "mrr": {
                "accounts": mrr_row[0],
                "total_mrr_usd": round(mrr_row[1] or 0, 2),
                "total_arr_usd": round(mrr_row[2] or 0, 2),
            },
            "churn": {
                "avg_churn_rate_pct": round(churn_row[0] or 0, 2),
                "fully_churned_accounts": churn_row[1],
            },
            "activation": {
                "total_workspaces": act_row[0],
                "activated_workspaces": act_row[1],
                "avg_activation_rate_pct": round(act_row[2] or 0, 2),
            },
            "support_sla": {
                "avg_breach_rate_pct": round(sla_row[0] or 0, 2),
                "excellent_accounts": sla_row[1],
            },
        }
        print(json.dumps(report, indent=2))
        return report
    except Exception as exc:
        print(f"KPI report skipped (dbt may not have run): {exc}")
        return {}


def run_demo() -> dict:
    db_path = ROOT / "data" / "warehouse.duckdb"

    step_generate()
    step_load(db_path)

    dbt_rc = step_dbt(db_path)
    if dbt_rc != 0:
        print("WARNING: dbt run exited with errors — KPI report may be incomplete.")

    quality = step_quality()
    kpis = step_kpi_report(db_path)

    summary = {
        "quality_passed": quality.get("passed", False),
        "files_scanned": quality.get("files_scanned", 0),
        "rows_scanned": quality.get("rows_scanned", 0),
        "dbt_exit_code": dbt_rc,
        "kpis": kpis,
    }

    print("\n=== Demo complete ===")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run_demo()
