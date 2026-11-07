
import json


def build_instructional_qc_prompt(lesson: dict) -> str:
    lesson_json = json.dumps(
        lesson,
        indent=2,
        ensure_ascii=False
    )

    return f"""
You are an expert instructional designer and educational quality reviewer.

Evaluate the following lesson for instructional quality.
Do NOT evaluate factual correctness; that is handled by a separate QC layer.

LESSON:
{lesson_json}

Evaluate these dimensions:

1. Objective alignment:
   Does every major lesson segment support the learning objective?

2. Instructional sequence:
   Is the lesson arranged logically, from foundational concepts
   to more advanced understanding?

3. Explanation quality:
   Are explanations clear, understandable, and appropriate
   for the stated target audience?

4. Examples:
   Are examples relevant, practical, and useful for understanding?

5. Activities:
   Are learner activities meaningful and do they actively
   involve the learner?

6. Knowledge checks:
   Are questions relevant to the learning outcomes?
   Are expected answers clear and sufficiently complete?

7. Time allocation:
   Are segment durations realistic for the proposed activities,
   explanations, and knowledge checks?
   The total duration must be exactly 45 minutes.

8. Engagement and accessibility:
   Is the lesson engaging, understandable, and appropriately
   scaffolded for the target audience?

Return ONLY valid JSON with this exact structure:

{{
  "qc_layer": "Instructional Quality",
  "overall_status": "pass",
  "score": 85,
  "summary": "Brief overall assessment",
  "findings": [
    {{
      "segment_number": 1,
      "dimension": "Objective alignment",
      "status": "good",
      "observation": "What was observed",
      "recommendation": "How to improve it"
    }}
  ],
  "recommended_changes": [
    {{
      "segment_number": 1,
      "dimension": "Explanation quality",
      "original_issue": "Problem identified",
      "suggested_change": "Specific improvement"
    }}
  ],
  "strengths": [
    "A strength of the lesson"
  ],
  "missing_elements": [
    "An important missing instructional element"
  ]
}}

Rules:
- overall_status must be pass, needs_review, or fail.
- score must be an integer between 0 and 100.
- Finding status must be good, needs_improvement, or poor.
- Evaluate the actual supplied lesson, not an imaginary lesson.
- Do not invent lesson segments or claim that missing elements exist
  when they are present.
- Give specific, actionable recommendations.
- A lesson must not pass merely because its duration is 45 minutes.
- Return JSON only. No Markdown fences or extra text.
"""
