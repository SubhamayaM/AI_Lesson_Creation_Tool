
import os
from pathlib import Path
from dotenv import load_dotenv

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from the project root
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

# API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

# Application configuration
DATABASE_PATH = BASE_DIR / "lessons.db"
EXPORT_DIR = BASE_DIR / "exports"

LESSON_DURATION_MINUTES = 45
APP_TITLE = "AI Lesson Creation Tool"

# Ensure export directory exists
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def validate_config():
    """Check that the required Gemini configuration is present."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. Please check your .env file."
        )

    if GEMINI_API_KEY == "PASTE_YOUR_NEW_API_KEY_HERE":
        raise ValueError(
            "Replace the placeholder in .env with your new Gemini API key."
        )

    if not GEMINI_MODEL:
        raise ValueError("GEMINI_MODEL is missing from .env.")

    return True
