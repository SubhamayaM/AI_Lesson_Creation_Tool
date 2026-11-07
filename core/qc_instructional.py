
import json
import re

from integrations.llm_client import generate_text
from prompts.instructional_qc_prompt import (
    build_instructional_qc_prompt
)


def _parse_instructional_qc_response(response: str) -> dict:
    if not response or not response.strip():
        raise ValueError("Instructional QC returned an empty response.")

    cleaned = response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON returned by instructional QC: {error}"
        ) from error


def validate_instructional_report(report: dict) -> dict:
    if not isinstance(report, dict):
        raise ValueError("Instructional QC report must be a dictionary.")

    required_fields = [
        "qc_layer",
        "overall_status",
        "score",
        "summary",
        "findings",
        "recommended_changes",
        "strengths",
        "missing_elements"
    ]

    for field in required_fields:
        if field not in report:
            raise ValueError(
                f"Instructional QC report is missing: {field}"
            )

    if report["qc_layer"] != "Instructional Quality":
        raise ValueError("Incorrect QC layer name.")

    if report["overall_status"] not in (
        "pass", "needs_review", "fail"
    ):
        raise ValueError("Invalid instructional QC status.")

    if (
        not isinstance(report["score"], int)
        or isinstance(report["score"], bool)
        or not 0 <= report["score"] <= 100
    ):
        raise ValueError("QC score must be an integer from 0 to 100.")

    if not isinstance(report["summary"], str):
        raise ValueError("QC summary must be text.")

    for field in (
        "findings",
        "recommended_changes",
        "strengths",
        "missing_elements"
    ):
        if not isinstance(report[field], list):
            raise ValueError(f"{field} must be a list.")

    for finding in report["findings"]:
        if not isinstance(finding, dict):
            raise ValueError("Each finding must be an object.")

        for field in (
            "segment_number",
            "dimension",
            "status",
            "observation",
            "recommendation"
        ):
            if field not in finding:
                raise ValueError(
                    f"Finding is missing field: {field}"
                )

        if finding["status"] not in (
            "good", "needs_improvement", "poor"
        ):
            raise ValueError("Invalid finding status.")

    for change in report["recommended_changes"]:
        if not isinstance(change, dict):
            raise ValueError("Each recommended change must be an object.")

        for field in (
            "segment_number",
            "dimension",
            "original_issue",
            "suggested_change"
        ):
            if field not in change:
                raise ValueError(
                    f"Recommended change is missing: {field}"
                )

    return report


def run_instructional_qc(lesson: dict) -> dict:
    if not isinstance(lesson, dict):
        raise ValueError("Lesson must be a dictionary.")

    if not lesson.get("segments"):
        raise ValueError("Lesson must contain segments.")

    prompt = build_instructional_qc_prompt(lesson)

    response = generate_text(prompt)

    report = _parse_instructional_qc_response(response)

    return validate_instructional_report(report)
