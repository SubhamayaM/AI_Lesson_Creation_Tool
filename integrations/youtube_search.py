
import requests

from config import YOUTUBE_API_KEY


YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


def search_videos(query: str, max_results: int = 5) -> list:
    """Search YouTube using the API or a web-search fallback."""

    if not query or not query.strip():
        return []

    # Use YouTube Data API if an API key is configured.
    if YOUTUBE_API_KEY:
        try:
            response = requests.get(
                YOUTUBE_API_URL,
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": min(max_results, 50),
                    "key": YOUTUBE_API_KEY
                },
                timeout=20
            )

            response.raise_for_status()

            items = response.json().get("items", [])
            videos = []

            for item in items:
                snippet = item.get("snippet", {})
                video_id = item.get("id", {}).get("videoId")

                if not video_id:
                    continue

                videos.append({
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "source": "YouTube Data API"
                })

            return videos

        except requests.RequestException:
            pass

    # Fallback: search for publicly indexed YouTube videos.
    try:
        from ddgs import DDGS

        results = DDGS().text(
            f"site:youtube.com/watch {query}",
            max_results=max_results
        )

        videos = []

        for item in results:
            url = item.get("href", "")

            if "youtube.com/watch" not in url:
                continue

            videos.append({
                "title": item.get("title", ""),
                "channel": "",
                "description": item.get("body", ""),
                "url": url,
                "source": "DuckDuckGo"
            })

        return videos

    except Exception:
        return []
