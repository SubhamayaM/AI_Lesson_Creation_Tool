import json
from datetime import datetime
from pathlib import Path

from config import EXPORT_DIR
from core.research_engine import conduct_research
from core.lesson_generator import generate_lesson


LESSON_TITLE = "HTTP Requests and Responses"

LEARNING_OBJECTIVE = (
    "Explain GET and POST methods and distinguish between "
    "2xx, 4xx, and 5xx status categories."
)

OUTPUT_FILE = Path(EXPORT_DIR) / "http_requests_pipeline.json"


def save_pipeline(data: dict) -> None:
    """Save research and lesson data locally as JSON."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    pipeline_data = {
        "lesson_title": LESSON_TITLE,
        "learning_objective": LEARNING_OBJECTIVE,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "started",
        "research": None,
        "lesson": None,
    }

    try:
        print("\nSTEP 1: Conducting research...")

        research = conduct_research(
            LESSON_TITLE,
            LEARNING_OBJECTIVE,
        )

        pipeline_data["research"] = research
        pipeline_data["status"] = "research_completed"

        # Save research immediately, even if lesson generation fails.
        save_pipeline(pipeline_data)

        print("Websites:", len(research.get("websites", [])))
        print("Books:", len(research.get("books", [])))
        print("Videos:", len(research.get("videos", [])))
        print("Research errors:", research.get("errors", []))

        print("\nSTEP 2: Generating the 45-minute lesson...")

        lesson = generate_lesson(
            LESSON_TITLE,
            LEARNING_OBJECTIVE,
            research,
        )

        pipeline_data["lesson"] = lesson
        pipeline_data["status"] = "completed"

        save_pipeline(pipeline_data)

        print("\nPIPELINE COMPLETED")
        print("Lesson:", lesson["title"])
        print("Duration:", lesson["duration_minutes"], "minutes")
        print("Segments:", len(lesson["segments"]))
        print(
            "Total segment minutes:",
            sum(s["duration_minutes"] for s in lesson["segments"]),
        )
        print("Actual references:", len(lesson["references"]))
        print("\nSaved file:", OUTPUT_FILE)

    except Exception as error:
        pipeline_data["status"] = "failed"
        pipeline_data["error"] = str(error)
        save_pipeline(pipeline_data)

        print("\nPIPELINE FAILED")
        print("Error:", error)
        print("Available progress saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()