
import requests

from config import TAVILY_API_KEY


def search_web(query: str, max_results: int = 5) -> list:
    """Search the web using Tavily when configured, otherwise DuckDuckGo."""

    if not query or not query.strip():
        return []

    # Try Tavily if an API key is configured.
    if TAVILY_API_KEY:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results
                },
                timeout=20
            )
            response.raise_for_status()

            results = response.json().get("results", [])

            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "source": "Tavily"
                }
                for item in results
            ]

        except requests.RequestException:
            pass

    # DuckDuckGo fallback.
    try:
        from ddgs import DDGS

        results = DDGS().text(
            query,
            max_results=max_results
        )

        return [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
                "source": "DuckDuckGo"
            }
            for item in results
        ]

    except Exception:
        return []
