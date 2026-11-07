import json
import re

from integrations.llm_client import generate_text
from prompts.lesson_prompt import build_lesson_prompt


def _parse_json_response(response_text: str) -> dict:
    """Parse JSON returned by the language model."""
    if not response_text or not response_text.strip():
        raise ValueError("The AI returned an empty lesson.")

    cleaned = response_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The AI returned invalid JSON: {error}"
        ) from error


def _build_actual_references(research: dict) -> list:
    """Build references only from resources actually returned by research."""
    references = []

    resource_types = [
        ("website", "websites"),
        ("book", "books"),
        ("video", "videos"),
    ]

    for resource_type, category in resource_types:
        for item in research.get(category, []):
            url = item.get("url", "").strip()

            if not url:
                continue

            references.append({
                "title": item.get("title") or "Untitled resource",
                "type": resource_type,
                "url": url,
            })

    return references


def validate_lesson(lesson: dict) -> dict:
    """Validate the lesson structure and exact 45-minute duration."""
    if not isinstance(lesson, dict):
        raise ValueError("Lesson must be a JSON object.")

    required_fields = [
        "title",
        "learning_objective",
        "duration_minutes",
        "segments",
        "references",
    ]

    for field in required_fields:
        if field not in lesson:
            raise ValueError(f"Lesson is missing required field: {field}")

    if lesson["duration_minutes"] != 45:
        raise ValueError("Lesson duration must be exactly 45 minutes.")

    segments = lesson["segments"]

    if not isinstance(segments, list) or not segments:
        raise ValueError("Lesson must contain at least one segment.")

    total_minutes = 0

    for index, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            raise ValueError(f"Segment {index} must be an object.")

        duration = segment.get("duration_minutes")

        if not isinstance(duration, int) or isinstance(duration, bool):
            raise ValueError(
                f"Segment {index} must have an integer duration."
            )

        if duration <= 0:
            raise ValueError(
                f"Segment {index} must have a positive duration."
            )

        if not segment.get("title"):
            raise ValueError(f"Segment {index} is missing its title.")

        if not segment.get("explanation"):
            raise ValueError(
                f"Segment {index} is missing its explanation."
            )

        total_minutes += duration

    if total_minutes != 45:
        raise ValueError(
            f"Segment durations total {total_minutes} minutes, not 45."
        )

    return lesson


def generate_lesson(
    lesson_title: str,
    learning_objective: str,
    research: dict | None = None,
) -> dict:
    """Generate and validate a complete 45-minute lesson."""
    if not lesson_title or not lesson_title.strip():
        raise ValueError("Lesson title cannot be empty.")

    if not learning_objective or not learning_objective.strip():
        raise ValueError("Learning objective cannot be empty.")

    research = research or {}

    prompt = build_lesson_prompt(
        lesson_title=lesson_title.strip(),
        learning_objective=learning_objective.strip(),
        research=research,
    )

    response_text = generate_text(prompt)
    lesson = _parse_json_response(response_text)

    # Use only URLs returned by the research engine.
    lesson["references"] = _build_actual_references(research)

    lesson = validate_lesson(lesson)

    return lesson