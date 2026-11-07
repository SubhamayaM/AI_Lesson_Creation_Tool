
import time

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, validate_config


class GeminiClient:
    """Handles Gemini API requests with temporary-failure retries."""

    def __init__(self):
        validate_config()

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        """Generate text and retry temporary server failures."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        retry_delays = [2, 5, 10]

        for attempt in range(len(retry_delays) + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text.strip()

            except Exception as error:
                status_code = (
                    getattr(error, "code", None)
                    or getattr(error, "status_code", None)
                )

                # Retry only temporary server-side errors.
                if status_code in (500, 502, 503, 504):
                    if attempt < len(retry_delays):
                        delay = retry_delays[attempt]

                        print(
                            f"Gemini temporarily unavailable. "
                            f"Retrying in {delay} seconds..."
                        )

                        time.sleep(delay)
                        continue

                raise RuntimeError(
                    f"Gemini API request failed: {error}"
                ) from error

        raise RuntimeError("Gemini request failed after all retries.")


_client = None


def get_llm():
    """Return a reusable Gemini client."""

    global _client

    if _client is None:
        _client = GeminiClient()

    return _client


def generate_text(prompt: str) -> str:
    """Generate text using the shared Gemini client."""

    return get_llm().generate(prompt)
