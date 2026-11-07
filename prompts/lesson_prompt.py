
import json


def build_lesson_prompt(
    lesson_title: str,
    learning_objective: str,
    research: dict,
    audience: str = "Beginner"
) -> str:
    """Build the prompt for generating a structured 45-minute lesson."""

    research_data = {
        "websites": research.get("websites", [])[:5],
        "books": research.get("books", [])[:5],
        "videos": research.get("videos", [])[:5]
    }

    research_json = json.dumps(
        research_data,
        indent=2,
        ensure_ascii=False
    )

    return f"""
You are an expert instructional designer and subject-matter educator.

Create a complete lesson using the following information.

LESSON TITLE:
{lesson_title}

LEARNING OBJECTIVE:
{learning_objective}

TARGET AUDIENCE:
{audience}

TOTAL LESSON DURATION:
Exactly 45 minutes.

RESEARCH MATERIAL:
{research_json}

INSTRUCTIONS:

1. Design the lesson to achieve the stated learning objective.
2. Divide the lesson into logical teaching segments.
3. Every segment must have a duration in whole minutes.
4. The sum of all segment durations MUST equal exactly 45 minutes.
5. Include:
   - Introduction and learning goals.
   - Detailed explanations.
   - Relevant practical examples.
   - At least one learner activity.
   - Knowledge-check questions.
   - A recap and conclusion.
6. Include teacher actions and learner actions.
7. Provide expected answers for knowledge-check questions.
8. Use accurate, beginner-friendly language.
9. Do not invent research sources.
10. Only include references that appear in the supplied research material.
11. If a resource is not relevant, do not force it into the lesson.
12. Make the lesson detailed enough for an instructor to teach directly.

RETURN ONLY VALID JSON.
Do not use Markdown code fences.

Use exactly this JSON structure:

{{
  "title": "Lesson title",
  "learning_objective": "Learning objective",
  "target_audience": "{audience}",
  "duration_minutes": 45,
  "learning_outcomes": [
    "Outcome 1",
    "Outcome 2"
  ],
  "prerequisites": [
    "Prerequisite 1"
  ],
  "segments": [
    {{
      "segment_number": 1,
      "title": "Introduction",
      "duration_minutes": 5,
      "segment_type": "introduction",
      "teacher_actions": "What the instructor should do",
      "learner_actions": "What learners should do",
      "explanation": "Detailed teaching content",
      "example": "Relevant example",
      "activity": "Activity instructions or null",
      "knowledge_check": [
        {{
          "question": "Question",
          "expected_answer": "Expected answer"
        }}
      ]
    }}
  ],
  "references": [
    {{
      "title": "Resource title",
      "type": "website, book, or video",
      "url": "Resource URL"
    }}
  ]
}}

IMPORTANT:
- The example above shows the structure, not the complete lesson.
- Generate all segments required to cover the full 45 minutes.
- Do not leave segment explanations empty.
- Every segment must have a positive integer duration.
- Ensure all segment durations add up to exactly 45.
"""
