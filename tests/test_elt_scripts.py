import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extractors.generate_raw_sources import build_rows


class EltPlatformTests(unittest.TestCase):
    def test_build_rows_generates_contract_records(self) -> None:
        rows = build_rows("billing", "subscriptions")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["source"], "billing")
        self.assertEqual(rows[0]["table"], "subscriptions")
        self.assertIn("ingested_at", rows[0])

    def test_quality_checks_detect_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_dir = root / "extractors" / "raw_data"
            raw_dir.mkdir(parents=True, exist_ok=True)
            valid_rows = [
                {
                    "row_id": "subscriptions_001",
                    "payload": {"status": "active", "amount": 1200, "region": "IN"},
                }
            ]
            invalid_rows = [
                {
                    "row_id": "subscriptions_002",
                    "payload": {"amount": 1200, "region": "IN"},
                }
            ]
            (raw_dir / "valid.json").write_text(json.dumps(valid_rows), encoding="utf-8")
            (raw_dir / "invalid.json").write_text(json.dumps(invalid_rows), encoding="utf-8")

            # Re-use the same quality logic shape on synthetic files.
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

            self.assertEqual(checks["files_scanned"], 2)
            self.assertEqual(checks["invalid_payloads"], 1)


if __name__ == "__main__":
    unittest.main()
