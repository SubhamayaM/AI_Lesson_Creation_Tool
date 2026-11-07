
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.qc_instructional import run_instructional_qc

INPUT_FILE = PROJECT_ROOT / "exports" / "http_requests_pipeline.json"
OUTPUT_FILE = PROJECT_ROOT / "exports" / "instructional_qc_report.json"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Pipeline JSON not found. Run tests/run_pipeline.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    lesson = data.get("lesson")

    if not lesson:
        raise ValueError("No lesson found in pipeline JSON.")

    print("\n1. Loading saved lesson...")
    print(f"Lesson: {lesson.get('title')}")
    print(f"Duration: {lesson.get('duration_minutes')} minutes")

    print("\n2. Running QC Layer 2: Instructional Quality...")

    report = run_instructional_qc(lesson)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\nINSTRUCTIONAL QC COMPLETED SUCCESSFULLY")
    print("---------------------------------------")
    print(f"QC Layer: {report['qc_layer']}")
    print(f"Status: {report['overall_status']}")
    print(f"Score: {report['score']}/100")
    print(f"Findings: {len(report['findings'])}")
    print(
        f"Recommendations: "
        f"{len(report['recommended_changes'])}"
    )
    print(f"Summary: {report['summary']}")
    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
