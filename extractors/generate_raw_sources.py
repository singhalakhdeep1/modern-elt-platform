import json
from datetime import UTC, datetime
from pathlib import Path


def load_contracts(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(source_name: str, table_name: str) -> list[dict]:
    timestamp = datetime.now(UTC).isoformat()
    return [
        {
            "source": source_name,
            "table": table_name,
            "row_id": f"{table_name}_001",
            "payload": {"status": "active", "amount": 1200, "region": "IN"},
            "ingested_at": timestamp,
        },
        {
            "source": source_name,
            "table": table_name,
            "row_id": f"{table_name}_002",
            "payload": {"status": "active", "amount": 3200, "region": "US"},
            "ingested_at": timestamp,
        },
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    contracts_path = root / "extractors" / "source_contracts.json"
    output_dir = root / "extractors" / "raw_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    contracts = load_contracts(contracts_path)
    for source in contracts["sources"]:
        source_name = source["name"]
        for table_name in source["tables"]:
            rows = build_rows(source_name, table_name)
            out_file = output_dir / f"{source_name}_{table_name}.json"
            out_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"Wrote {len(rows)} rows to {out_file}")


if __name__ == "__main__":
    main()
