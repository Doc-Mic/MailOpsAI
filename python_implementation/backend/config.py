"""Application settings for MailOpsAI."""

from __future__ import annotations

from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    from llm_service import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
ROOT_DIR = PROJECT_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"


def load_settings() -> dict[str, str]:
    """Load local environment values for runtime configuration."""
    for dotenv_path in (ROOT_DIR / ".env", PROJECT_DIR / ".env", BASE_DIR / ".env"):
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=False)

    return {
        "app_name": "MailOpsAI",
        "llm_provider": "groq",
        "primary_model": "llama-3.3-70b-versatile",
        "fallback_model": "gemini-2.5-flash",
    }

