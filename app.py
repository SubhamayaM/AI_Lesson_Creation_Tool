
import json
import re
import streamlit as st

from config import APP_TITLE
from core.research_engine import conduct_research
from core.lesson_generator import generate_lesson, validate_lesson
from core.qc_research import run_research_qc
from core.qc_instructional import run_instructional_qc
from core.export_manager import export_json, export_docx, export_pdf
from database.db import (
    init_db,
    save_lesson,
    get_lesson,
    list_lessons
)
from integrations.llm_client import generate_text


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

init_db()


# ---------------- SESSION STATE ----------------

DEFAULTS = {
    "lesson": None,
    "research": {},
    "factual_report": None,
    "instructional_report": None,
    "lesson_id": None,
    "lesson_editor": "",
    "last_error": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def sync_editor():
    if st.session_state.lesson:
        st.session_state.lesson_editor = json.dumps(
            st.session_state.lesson,
            indent=4,
            ensure_ascii=False
        )


def save_current_lesson():
    lesson_id = save_lesson(
        lesson=st.session_state.lesson,
        research=st.session_state.research,
        factual_report=st.session_state.factual_report,
        instructional_report=st.session_state.instructional_report,
        lesson_id=st.session_state.lesson_id
    )
    st.session_state.lesson_id = lesson_id
    return lesson_id


def parse_json_response(response):
    cleaned = response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


# ---------------- HEADER ----------------

st.title("📚 AI Lesson Creation Tool")
st.caption(
    "Research-backed lesson generation with independent "
    "factual and instructional quality checks."
)

st.divider()


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("📂 Saved Lessons")

    saved_lessons = list_lessons()

    if saved_lessons:
        lesson_options = {
            f"{item['title']} (ID: {item['id']})": item["id"]
            for item in saved_lessons
        }

        selected_label = st.selectbox(
            "Choose a saved lesson",
            list(lesson_options.keys())
        )

        if st.button("Load Selected Lesson", use_container_width=True):
            record = get_lesson(lesson_options[selected_label])

            if record:
                st.session_state.lesson = record["lesson"]
                st.session_state.research = record["research"]
                st.session_state.factual_report = (
                    record["factual_report"] or None
                )
                st.session_state.instructional_report = (
                    record["instructional_report"] or None
                )
                st.session_state.lesson_id = record["id"]
                sync_editor()
                st.success("Lesson loaded.")
                st.rerun()
    else:
        st.info("No saved lessons yet.")

    st.divider()

    if st.session_state.lesson:
        st.metric(
            "Current lesson duration",
            f"{st.session_state.lesson.get('duration_minutes', 0)} min"
        )


# ---------------- TABS ----------------

tab_create, tab_edit, tab_qc, tab_export = st.tabs([
    "🚀 Create Lesson",
    "✏️ Review & Edit",
    "🔍 Quality Control",
    "📤 Preview & Export"
])


# ============================================================
# TAB 1: CREATE LESSON
# ============================================================

with tab_create:
    st.header("Create a New Lesson")

    with st.form("lesson_creation_form"):
        title = st.text_input(
            "Lesson Title",
            placeholder="e.g. HTTP Requests and Responses"
        )

        objective = st.text_area(
            "Learning Objective",
            placeholder="Describe what learners should understand or achieve.",
            height=120
        )

        audience = st.selectbox(
            "Target Audience",
            ["Beginner", "Intermediate", "Advanced"]
        )

        submitted = st.form_submit_button(
            "Research and Generate Lesson",
            use_container_width=True
        )

    if submitted:
        if not title.strip() or not objective.strip():
            st.error("Please provide both the lesson title and objective.")
        else:
            try:
                with st.spinner("Researching websites, books and videos..."):
                    research = conduct_research(title, objective)

                st.session_state.research = research

                with st.spinner("Generating your 45-minute lesson..."):
                    lesson = generate_lesson(
                        title,
                        objective,
                        research
                    )

                lesson["target_audience"] = audience

                # Keep references grounded in actual research results.
                actual_references = []
                for category in ("websites", "books", "videos"):
                    for item in research.get(category, []):
                        if item.get("url"):
                            actual_references.append({
                                "title": item.get("title", "Untitled"),
                                "type": category[:-1],
                                "url": item["url"]
                            })

                lesson["references"] = actual_references

                st.session_state.lesson = lesson
                st.session_state.factual_report = None
                st.session_state.instructional_report = None
                st.session_state.lesson_id = None
                sync_editor()

                saved_id = save_current_lesson()

                st.success(
                    f"Lesson generated and saved successfully. "
                    f"Database ID: {saved_id}"
                )

                st.rerun()

            except Exception as error:
                st.error(f"Lesson generation failed: {error}")

    if st.session_state.research:
        with st.expander("View Research Results"):
            for category in ("websites", "books", "videos"):
                items = st.session_state.research.get(category, [])
                st.subheader(category.title())
                if not items:
                    st.write("No results found.")
                for item in items:
                    st.markdown(
                        f"- [{item.get('title', 'Untitled')}]"
                        f"({item.get('url', '')})"
                    )


# ============================================================
# TAB 2: REVIEW AND EDIT
# ============================================================

with tab_edit:
    st.header("Instructor Review and Editing")

    if not st.session_state.lesson:
        st.info("Generate or load a lesson to begin reviewing.")
    else:
        st.write(
            "Edit the lesson below. The editor uses JSON so you can "
            "modify explanations, activities, questions and timing."
        )

        edited_json = st.text_area(
            "Lesson JSON Editor",
            key="lesson_editor",
            height=550
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Validate and Apply Edits", use_container_width=True):
                try:
                    edited_lesson = json.loads(edited_json)
                    validate_lesson(edited_lesson)

                    st.session_state.lesson = edited_lesson
                    save_current_lesson()

                    st.success("Edits validated and saved.")
                except Exception as error:
                    st.error(f"Could not apply edits: {error}")

        with col2:
            if st.button("Save Current Lesson", use_container_width=True):
                try:
                    edited_lesson = json.loads(edited_json)
                    validate_lesson(edited_lesson)
                    st.session_state.lesson = edited_lesson
                    lesson_id = save_current_lesson()
                    st.success(f"Lesson saved. Database ID: {lesson_id}")
                except Exception as error:
                    st.error(f"Save failed: {error}")

        st.divider()

        st.subheader("Lesson Preview")

        lesson = st.session_state.lesson

        st.markdown(f"### {lesson.get('title', '')}")
        st.write(f"**Objective:** {lesson.get('learning_objective', '')}")
        st.write(f"**Duration:** {lesson.get('duration_minutes', 45)} minutes")

        for segment in lesson.get("segments", []):
            with st.expander(
                f"Segment {segment.get('segment_number', '')}: "
                f"{segment.get('title', '')} "
                f"({segment.get('duration_minutes', 0)} min)"
            ):
                st.markdown("**Explanation**")
                st.write(segment.get("explanation", ""))

                st.markdown("**Example**")
                st.write(segment.get("example", ""))

                st.markdown("**Activity**")
                st.write(segment.get("activity", ""))

                st.markdown("**Knowledge Check**")
                for question in segment.get("knowledge_check", []):
                    st.write(f"Q: {question.get('question', '')}")
                    st.write(
                        f"Expected answer: "
                        f"{question.get('expected_answer', '')}"
                    )


# ============================================================
# TAB 3: QUALITY CONTROL
# ============================================================

with tab_qc:
    st.header("Two-Layer Quality Control")

    if not st.session_state.lesson:
        st.info("Generate or load a lesson first.")
    else:
        st.write(
            "Run the two independent quality checks on the current lesson."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Run Factual QC", use_container_width=True):
                try:
                    with st.spinner("Checking research and factual accuracy..."):
                        report = run_research_qc(
                            st.session_state.lesson,
                            st.session_state.research
                        )

                    st.session_state.factual_report = report
                    save_current_lesson()
                    st.success("Factual QC completed.")
                except Exception as error:
                    st.error(f"Factual QC failed: {error}")

        with col2:
            if st.button("Run Instructional QC", use_container_width=True):
                try:
                    with st.spinner("Checking instructional quality..."):
                        report = run_instructional_qc(
                            st.session_state.lesson
                        )

                    st.session_state.instructional_report = report
                    save_current_lesson()
                    st.success("Instructional QC completed.")
                except Exception as error:
                    st.error(f"Instructional QC failed: {error}")

        reports = [
            ("Factual and Research Accuracy", st.session_state.factual_report),
            ("Instructional Quality", st.session_state.instructional_report)
        ]

        for report_name, report in reports:
            st.divider()
            st.subheader(report_name)

            if report:
                col_a, col_b = st.columns(2)
                col_a.metric("Score", f"{report['score']}/100")
                col_b.metric("Status", report["overall_status"].upper())

                st.write(report["summary"])

                with st.expander("View findings"):
                    st.json(report["findings"])

                with st.expander("View recommendations"):
                    st.json(report["recommended_changes"])
            else:
                st.info("This QC layer has not been run yet.")

        st.divider()
        st.subheader("Apply QC Recommendations")

        available_recommendations = []

        for report_name, report in reports:
            if report:
                for recommendation in report.get(
                    "recommended_changes", []
                ):
                    available_recommendations.append({
                        "layer": report_name,
                        **recommendation
                    })

        if available_recommendations:
            st.write(
                f"{len(available_recommendations)} recommendations "
                "are available."
            )

            if st.button(
                "Apply All Recommendations with AI",
                use_container_width=True
            ):
                try:
                    prompt = f"""
You are an expert lesson editor.

Improve the supplied lesson by applying the instructor-reviewed
quality-control recommendations below.

LESSON:
{json.dumps(st.session_state.lesson, ensure_ascii=False)}

RECOMMENDATIONS:
{json.dumps(available_recommendations, ensure_ascii=False)}

Rules:
- Return the complete revised lesson as valid JSON only.
- Preserve the title and learning objective.
- Preserve the exact total duration of 45 minutes.
- Keep all segments and their structure.
- Improve only where recommendations justify changes.
- Preserve references.
- Do not invent sources.
- Keep knowledge checks and expected answers.
"""

                    with st.spinner("Applying recommendations..."):
                        response = generate_text(prompt)
                        improved_lesson = parse_json_response(response)
                        validate_lesson(improved_lesson)

                    st.session_state.lesson = improved_lesson
                    sync_editor()
                    save_current_lesson()

                    st.success(
                        "Recommendations applied. "
                        "Please review the revised lesson before exporting."
                    )

                except Exception as error:
                    st.error(f"Could not apply recommendations: {error}")
        else:
            st.info(
                "Run at least one QC layer to generate recommendations."
            )


# ============================================================
# TAB 4: EXPORT
# ============================================================

with tab_export:
    st.header("Final Lesson and Export")

    if not st.session_state.lesson:
        st.info("Generate or load a lesson first.")
    else:
        lesson = st.session_state.lesson

        total_minutes = sum(
            segment.get("duration_minutes", 0)
            for segment in lesson.get("segments", [])
        )

        st.subheader(lesson.get("title", "Lesson"))
        st.write(lesson.get("learning_objective", ""))

        col1, col2, col3 = st.columns(3)
        col1.metric("Lesson duration", f"{lesson.get('duration_minutes', 0)} min")
        col2.metric("Segment count", len(lesson.get("segments", [])))
        col3.metric("Calculated time", f"{total_minutes} min")

        if total_minutes == 45:
            st.success("Lesson timing validation passed.")
        else:
            st.error("Lesson segment durations do not total 45 minutes.")

        if not (
            st.session_state.factual_report
            and st.session_state.instructional_report
        ):
            st.warning(
                "Both QC layers have not been completed. "
                "Review the lesson before final submission."
            )

        st.divider()
        st.subheader("Export Lesson")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("Export Word", use_container_width=True):
                try:
                    path = export_docx(lesson)
                    st.success("Word document created.")
                    st.download_button(
                        "Download DOCX",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        )
                    )
                except Exception as error:
                    st.error(f"Word export failed: {error}")

        with col_b:
            if st.button("Export PDF", use_container_width=True):
                try:
                    path = export_pdf(lesson)
                    st.success("PDF created.")
                    st.download_button(
                        "Download PDF",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime="application/pdf"
                    )
                except Exception as error:
                    st.error(f"PDF export failed: {error}")

        with col_c:
            if st.button("Export JSON", use_container_width=True):
                try:
                    path = export_json(lesson)
                    st.success("JSON created.")
                    st.download_button(
                        "Download JSON",
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime="application/json"
                    )
                except Exception as error:
                    st.error(f"JSON export failed: {error}")

        st.divider()
        st.subheader("QC Reports")

        if st.session_state.factual_report:
            st.download_button(
                "Download Factual QC Report",
                data=json.dumps(
                    st.session_state.factual_report,
                    indent=4,
                    ensure_ascii=False
                ),
                file_name="factual_qc_report.json",
                mime="application/json"
            )

        if st.session_state.instructional_report:
            st.download_button(
                "Download Instructional QC Report",
                data=json.dumps(
                    st.session_state.instructional_report,
                    indent=4,
                    ensure_ascii=False
                ),
                file_name="instructional_qc_report.json",
                mime="application/json"
            )
