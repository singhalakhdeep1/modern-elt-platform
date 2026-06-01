import json
from pathlib import Path


def run_checks() -> dict:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "extractors" / "raw_data"
    files = sorted(raw_dir.glob("*.json"))

    checks = {
        "files_scanned": len(files),
        "rows_scanned": 0,
        "null_row_ids": 0,
        "invalid_payloads": 0,
    }

    for file in files:
        rows = json.loads(file.read_text(encoding="utf-8"))
        checks["rows_scanned"] += len(rows)
        for row in rows:
            if not row.get("row_id"):
                checks["null_row_ids"] += 1
            payload = row.get("payload", {})
            if not isinstance(payload, dict) or "status" not in payload:
                checks["invalid_payloads"] += 1

    checks["passed"] = checks["null_row_ids"] == 0 and checks["invalid_payloads"] == 0
    return checks


if __name__ == "__main__":
    result = run_checks()
    print(json.dumps(result, indent=2))
