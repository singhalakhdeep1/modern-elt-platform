import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extractors.generate_raw_sources import build_rows


def run() -> dict:
    iterations = 6000
    started = time.perf_counter()
    generated = 0
    for _ in range(iterations):
        rows = build_rows("billing", "subscriptions")
        generated += len(rows)
    duration = max(0.001, time.perf_counter() - started)

    return {
        "workload": "extractor_row_generation",
        "iterations": iterations,
        "rows_generated": generated,
        "duration_sec": round(duration, 2),
        "rows_per_sec": round(generated / duration, 2),
    }


if __name__ == "__main__":
    report = run()
    output = Path(__file__).resolve().parent / "loadtest_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
