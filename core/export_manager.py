
import json
import re
from pathlib import Path

from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from config import EXPORT_DIR


def _safe_filename(title):
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", title)
    return name.strip("_") or "lesson"


def export_json(lesson, filename=None):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = filename or f"{_safe_filename(lesson.get('title'))}.json"
    path = EXPORT_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(lesson, file, indent=4, ensure_ascii=False)

    return path


def export_docx(lesson, filename=None):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = filename or f"{_safe_filename(lesson.get('title'))}.docx"
    path = EXPORT_DIR / filename

    document = Document()
    document.add_heading(lesson.get("title", "Lesson"), 0)

    document.add_paragraph(
        f"Learning Objective: {lesson.get('learning_objective', '')}"
    )
    document.add_paragraph(
        f"Target Audience: {lesson.get('target_audience', 'Beginner')}"
    )
    document.add_paragraph(
        f"Duration: {lesson.get('duration_minutes', 45)} minutes"
    )

    document.add_heading("Learning Outcomes", level=1)
    for outcome in lesson.get("learning_outcomes", []):
        document.add_paragraph(str(outcome), style="List Bullet")

    document.add_heading("Prerequisites", level=1)
    for item in lesson.get("prerequisites", []):
        document.add_paragraph(str(item), style="List Bullet")

    for segment in lesson.get("segments", []):
        number = segment.get("segment_number", "")
        heading = (
            f"Segment {number}: {segment.get('title', 'Untitled')} "
            f"({segment.get('duration_minutes', 0)} minutes)"
        )
        document.add_heading(heading, level=1)

        for field, label in [
            ("explanation", "Explanation"),
            ("example", "Example"),
            ("teacher_actions", "Teacher Actions"),
            ("learner_actions", "Learner Actions"),
            ("activity", "Activity")
        ]:
            value = segment.get(field)
            if value:
                document.add_heading(label, level=2)
                if isinstance(value, list):
                    for item in value:
                        document.add_paragraph(str(item), style="List Bullet")
                else:
                    document.add_paragraph(str(value))

        checks = segment.get("knowledge_check", [])
        if checks:
            document.add_heading("Knowledge Check", level=2)
            for index, check in enumerate(checks, start=1):
                document.add_paragraph(
                    f"Q{index}. {check.get('question', '')}"
                )
                document.add_paragraph(
                    f"Expected Answer: {check.get('expected_answer', '')}"
                )

    document.add_heading("References", level=1)
    for reference in lesson.get("references", []):
        document.add_paragraph(
            f"{reference.get('title', 'Untitled')} "
            f"({reference.get('type', 'Source')}) - "
            f"{reference.get('url', '')}"
        )

    document.save(path)
    return path


def export_pdf(lesson, filename=None):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = filename or f"{_safe_filename(lesson.get('title'))}.pdf"
    path = EXPORT_DIR / filename

    styles = getSampleStyleSheet()
    story = []

    def add_paragraph(value, style="BodyText"):
        if value is None:
            return
        safe_value = (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )
        story.append(Paragraph(safe_value, styles[style]))
        story.append(Spacer(1, 6))

    add_paragraph(lesson.get("title", "Lesson"), "Title")
    add_paragraph(
        f"<b>Learning Objective:</b> "
        f"{lesson.get('learning_objective', '')}"
    )
    add_paragraph(
        f"<b>Duration:</b> {lesson.get('duration_minutes', 45)} minutes"
    )
    add_paragraph(
        f"<b>Target Audience:</b> "
        f"{lesson.get('target_audience', 'Beginner')}"
    )

    add_paragraph("Learning Outcomes", "Heading1")
    for outcome in lesson.get("learning_outcomes", []):
        add_paragraph(f"• {outcome}")

    for segment in lesson.get("segments", []):
        add_paragraph(
            f"Segment {segment.get('segment_number', '')}: "
            f"{segment.get('title', '')} "
            f"({segment.get('duration_minutes', 0)} minutes)",
            "Heading2"
        )

        for field, label in [
            ("explanation", "Explanation"),
            ("example", "Example"),
            ("teacher_actions", "Teacher Actions"),
            ("learner_actions", "Learner Actions"),
            ("activity", "Activity")
        ]:
            value = segment.get(field)
            if value:
                add_paragraph(f"<b>{label}:</b>")
                if isinstance(value, list):
                    for item in value:
                        add_paragraph(f"• {item}")
                else:
                    add_paragraph(value)

        for index, check in enumerate(
            segment.get("knowledge_check", []), start=1
        ):
            add_paragraph(
                f"<b>Question {index}:</b> {check.get('question', '')}"
            )
            add_paragraph(
                f"<b>Expected Answer:</b> "
                f"{check.get('expected_answer', '')}"
            )

    add_paragraph("References", "Heading1")
    for reference in lesson.get("references", []):
        add_paragraph(
            f"{reference.get('title', 'Untitled')} - "
            f"{reference.get('url', '')}"
        )

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    document.build(story)

    return path
