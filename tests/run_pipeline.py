
import sys
import json
from pathlib import Path

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.research_engine import conduct_research
from core.lesson_generator import generate_lesson

OUTPUT_DIR = PROJECT_ROOT / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    title = "HTTP Requests and Responses"

    objective = (
        "Explain GET and POST methods and distinguish between "
        "2xx, 4xx, 5xx status categories."
    )

    print("\n1. Conducting research...")
    research = conduct_research(title, objective)

    print(f"Websites found: {len(research.get('websites', []))}")
    print(f"Books found: {len(research.get('books', []))}")
    print(f"Videos found: {len(research.get('videos', []))}")

    print("\n2. Generating the 45-minute lesson...")
    lesson = generate_lesson(title, objective, research)

    output = {
        "lesson": lesson,
        "research": research
    }

    output_path = OUTPUT_DIR / "http_requests_pipeline.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")
    print(f"Lesson duration: {lesson['duration_minutes']} minutes")
    print(f"Segments: {len(lesson['segments'])}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
