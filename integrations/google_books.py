
import requests


GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


def search_books(query: str, max_results: int = 5) -> list:
    """Find relevant books using the Google Books API."""

    if not query or not query.strip():
        return []

    try:
        response = requests.get(
            GOOGLE_BOOKS_URL,
            params={
                "q": query,
                "maxResults": min(max_results, 40),
                "printType": "books"
            },
            timeout=20
        )

        response.raise_for_status()

        items = response.json().get("items", [])
        books = []

        for item in items:
            info = item.get("volumeInfo", {})

            books.append({
                "title": info.get("title", "Unknown title"),
                "authors": info.get("authors", []),
                "publisher": info.get("publisher", ""),
                "published_date": info.get("publishedDate", ""),
                "description": info.get("description", ""),
                "url": info.get("infoLink", ""),
                "source": "Google Books"
            })

        return books

    except requests.RequestException:
        return []
