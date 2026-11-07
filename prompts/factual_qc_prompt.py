
import json


def build_factual_qc_prompt(lesson: dict, research: dict) -> str:
    """Build an evidence-focused factual accuracy review prompt."""

    lesson_json = json.dumps(
        lesson,
        indent=2,
        ensure_ascii=False
    )

    research_json = json.dumps(
        {
            "websites": research.get("websites", []),
            "books": research.get("books", []),
            "videos": research.get("videos", [])
        },
        indent=2,
        ensure_ascii=False
    )

    return f"""
You are an independent factual accuracy and research quality reviewer.

Your job is to review a generated educational lesson against the supplied
research evidence.

LESSON:
{lesson_json}

RESEARCH EVIDENCE:
{research_json}

REVIEW REQUIREMENTS:

1. Check important factual claims in the lesson.
2. Identify statements that contradict the supplied evidence.
3. Identify claims that are unsupported by the supplied evidence.
4. Identify misleading, incomplete, or ambiguous explanations.
5. Check whether examples are technically accurate.
6. Check whether the lesson addresses its stated learning objective.
7. Do not invent sources, URLs, quotations, or evidence.
8. Do not treat a search-result title or snippet as proof of every
   detailed claim.
9. Distinguish between:
   - verified
   - unsupported
   - incorrect
   - needs_review
10. If evidence is insufficient, say so rather than guessing.
11. Provide actionable corrections, including the affected segment.

Return ONLY valid JSON. Do not use Markdown code fences.

Use this exact structure:

{{
  "qc_layer": "Factual and Research Accuracy",
  "overall_status": "pass, needs_review, or fail",
  "score": 0,
  "summary": "Brief explanation of the review",
  "findings": [
    {{
      "segment_number": 1,
      "claim": "The claim being reviewed",
      "status": "verified, unsupported, incorrect, or needs_review",
      "evidence": "What the supplied research does or does not establish",
      "recommendation": "Specific correction or action"
    }}
  ],
  "missing_information": [
    "Important information that needs stronger evidence"
  ],
  "recommended_changes": [
    {{
      "segment_number": 1,
      "original_issue": "What is wrong or missing",
      "suggested_change": "How to improve it"
    }}
  ],
  "sources_consulted": [
    {{
      "title": "Exact title from supplied research",
      "url": "Exact URL from supplied research"
    }}
  ]
}}

SCORING:
- 90-100: Strong factual quality.
- 75-89: Mostly accurate, minor improvements needed.
- 50-74: Significant unsupported or unclear content.
- 0-49: Major factual problems.

A high score must not be awarded merely because the lesson sounds convincing.

If no adequate evidence is supplied, clearly state that the lesson
could not be fully verified.
"""
