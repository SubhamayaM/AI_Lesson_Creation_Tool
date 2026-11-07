from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key not found. Please configure GEMINI_API_KEY in .env."
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()


_client = None


def get_llm():
    global _client

    if _client is None:
        _client = GeminiClient()

    return _client


def generate_text(prompt: str) -> str:
    return get_llm().generate(prompt)