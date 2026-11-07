
import json
import re

from integrations.llm_client import generate_text
from prompts.factual_qc_prompt import build_factual_qc_prompt


def _parse_qc_response(response: str) -> dict:
    """Parse the JSON returned by the factual QC reviewer."""

    if not response or not response.strip():
        raise ValueError("Factual QC returned an empty response.")

    cleaned = response.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Factual QC returned invalid JSON: {error}"
        ) from error


def validate_factual_report(report: dict) -> dict:
    """Validate the structure of the factual QC report."""

    if not isinstance(report, dict):
        raise ValueError("Factual QC report must be a JSON object.")

    required_fields = [
        "qc_layer",
        "overall_status",
        "score",
        "summary",
        "findings",
        "recommended_changes"
    ]

    for field in required_fields:
        if field not in report:
            raise ValueError(
                f"Factual QC report is missing: {field}"
            )

    if report["overall_status"] not in (
        "pass",
        "needs_review",
        "fail"
    ):
        raise ValueError("Invalid factual QC status.")

    score = report["score"]

    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or not 0 <= score <= 100
    ):
        raise ValueError("Factual QC score must be between 0 and 100.")

    if not isinstance(report["findings"], list):
        raise ValueError("Factual QC findings must be a list.")

    if not isinstance(report["recommended_changes"], list):
        raise ValueError(
            "Factual QC recommendations must be a list."
        )

    return report


def run_research_qc(lesson: dict, research: dict) -> dict:
    """
    Run the independent factual and research accuracy review.

    Returns a structured QC report for instructor review.
    """

    if not isinstance(lesson, dict):
        raise ValueError("A valid lesson dictionary is required.")

    if not lesson.get("segments"):
        raise ValueError("The lesson has no segments to review.")

    if not isinstance(research, dict):
        raise ValueError("Research data must be a dictionary.")

    prompt = build_factual_qc_prompt(
        lesson=lesson,
        research=research
    )

    response = generate_text(prompt)

    report = _parse_qc_response(response)

    return validate_factual_report(report)
