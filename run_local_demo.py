import json
from pathlib import Path

from data_quality.check_quality import run_checks
from extractors.generate_raw_sources import main as generate_raw_sources


def run_demo() -> dict:
    generate_raw_sources()
    quality = run_checks()

    root = Path(__file__).resolve().parent
    output_path = root / "data_quality" / "quality_summary.json"
    output_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")

    return {
        "quality_passed": quality.get("passed", False),
        "files_scanned": quality.get("files_scanned", 0),
        "rows_scanned": quality.get("rows_scanned", 0),
        "quality_output": str(output_path),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
