"""Load raw JSON source files into DuckDB raw schema."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb


def load_to_duckdb(db_path: str | Path = "data/warehouse.duckdb") -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    raw_dir = Path(__file__).resolve().parent / "raw_data"
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for json_file in sorted(raw_dir.glob("*.json")):
        table_name = json_file.stem
        rows = json.loads(json_file.read_text(encoding="utf-8"))
        if not rows:
            print(f"  SKIP {table_name} (empty)")
            continue
        posix = json_file.as_posix()
        con.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
        con.execute(
            f"CREATE TABLE raw.{table_name} AS "
            f"SELECT * FROM read_json_auto('{posix}', auto_detect=true)"
        )
        count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
        print(f"  Loaded {count:>4} rows → raw.{table_name}")

    con.close()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    load_to_duckdb(root / "data" / "warehouse.duckdb")
    print("Load complete.")
