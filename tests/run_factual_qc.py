
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.qc_research import run_research_qc

INPUT_FILE = PROJECT_ROOT / "exports" / "http_requests_pipeline.json"
OUTPUT_FILE = PROJECT_ROOT / "exports" / "factual_qc_report.json"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Pipeline file not found: {INPUT_FILE}\n"
            "Run tests/run_pipeline.py first."
        )

    print("\n1. Loading saved lesson and research...")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    lesson = data.get("lesson")
    research = data.get("research")

    if not lesson or not research:
        raise ValueError("Saved pipeline file is missing lesson or research data.")

    print(f"Lesson: {lesson.get('title')}")
    print(f"Duration: {lesson.get('duration_minutes')} minutes")

    print("\n2. Running QC Layer 1: Research Accuracy...")

    report = run_research_qc(lesson, research)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\nFACTUAL QC COMPLETED SUCCESSFULLY")
    print("---------------------------------")
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
