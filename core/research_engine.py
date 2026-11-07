
from integrations.web_search import search_web
from integrations.google_books import search_books
from integrations.youtube_search import search_videos


def conduct_research(
    lesson_title: str,
    learning_objective: str,
    max_results: int = 5
) -> dict:
    """
    Research a lesson topic using websites, books and videos.

    Returns a dictionary containing:
        websites
        books
        videos
        errors
    """

    if not lesson_title or not lesson_title.strip():
        raise ValueError("Lesson title cannot be empty.")

    if not learning_objective or not learning_objective.strip():
        raise ValueError("Learning objective cannot be empty.")

    query = f"{lesson_title.strip()} {learning_objective.strip()}"

    research = {
        "lesson_title": lesson_title.strip(),
        "learning_objective": learning_objective.strip(),
        "websites": [],
        "books": [],
        "videos": [],
        "errors": []
    }

    # Search websites.
    try:
        research["websites"] = search_web(
            query,
            max_results=max_results
        )
    except Exception as error:
        research["errors"].append(
            f"Website research failed: {error}"
        )

    # Search books.
    try:
        research["books"] = search_books(
            lesson_title,
            max_results=max_results
        )
    except Exception as error:
        research["errors"].append(
            f"Book research failed: {error}"
        )

    # Search videos.
    try:
        research["videos"] = search_videos(
            lesson_title,
            max_results=max_results
        )
    except Exception as error:
        research["errors"].append(
            f"Video research failed: {error}"
        )

    return research
