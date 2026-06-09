"""Centralized LLM access for MailOpsAI agents.

All agents should call generate_llm_response(prompt) instead of importing
provider SDKs directly. Real credentials are loaded from .env; no API keys
belong in source code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, NamedTuple

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path: str | Path | None = None, override: bool = False) -> bool:
        """Small setup-time fallback; install python-dotenv for normal usage."""
        path = Path(dotenv_path) if dotenv_path else Path(".env")
        if not path.exists():
            return False

        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if override or key not in os.environ:
                os.environ[key] = value

        return True


GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_PROVIDER = "groq"


class LLMResult(NamedTuple):
    text: str
    provider_used: str


def _load_environment() -> None:
    """Load .env from common project locations without failing if absent."""
    current_file = Path(__file__).resolve()
    candidates = [
        Path.cwd() / ".env",
        current_file.parent / ".env",
        current_file.parent.parent / ".env",
    ]

    for dotenv_path in candidates:
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=False)

    load_dotenv(override=False)


_load_environment()


def _provider_order() -> list[str]:
    provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()

    if provider == "gemini":
        return ["gemini"]

    return ["groq", "gemini"]


def _build_messages(prompt: str, system_prompt: str | None = None) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


def _call_groq(
    prompt: str,
    *,
    system_prompt: str | None,
    temperature: float,
    max_tokens: int,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    from groq import Groq

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=_build_messages(prompt, system_prompt),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    message = completion.choices[0].message.content
    if not message:
        raise RuntimeError("Groq returned an empty response.")

    return message.strip()


def _call_gemini(
    prompt: str,
    *,
    system_prompt: str | None,
    temperature: float,
    max_tokens: int,
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = model.generate_content(
        full_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text.strip()


def _safe_demo_response(prompt: str) -> str:
    """Return a deterministic fallback so demos still work without providers."""
    lower_prompt = prompt.lower()

    if "classif" in lower_prompt:
        is_complaint = any(word in lower_prompt for word in ("complaint", "issue", "problem", "wrong", "angry"))
        is_urgent = any(word in lower_prompt for word in ("urgent", "asap", "immediately", "today", "critical"))
        return json.dumps(
            {
                "agent_name": "Email Classification Agent",
                "design_pattern": "ReAct",
                "category": "Client Complaint" if is_complaint else "General Business Email",
                "priority": "High" if is_urgent or is_complaint else "Medium",
                "sentiment": "Negative" if is_complaint else "Neutral",
                "action_required": True,
                "reasoning": "Demo mode: configure GROQ_API_KEY in .env for live LLM analysis.",
            }
        )

    if "draft" in lower_prompt or "reply" in lower_prompt:
        return json.dumps(
            {
                "agent_name": "Response Drafting Agent",
                "design_pattern": "Planner / Chain",
                "tone": "Professional and helpful",
                "subject": "Re: Your Email",
                "draft_reply": (
                    "Dear Customer, thank you for your message. We have received your request "
                    "and will review it promptly. Best regards, MailOpsAI Team"
                ),
            }
        )

    if "task" in lower_prompt or "follow" in lower_prompt:
        return json.dumps(
            {
                "agent_name": "Task and Follow-up Agent",
                "design_pattern": "Reflection",
                "tasks": [
                    {
                        "task": "Review the email and respond to the sender",
                        "deadline": "Within 1 business day",
                        "suggested_owner": "Operations Team",
                    }
                ],
                "follow_up_recommendation": "Follow up within 2 business days.",
                "reflection": (
                    "Demo mode: live task extraction is available when an LLM provider is configured."
                ),
            }
        )

    return (
        "Demo mode response: configure GROQ_API_KEY in .env to enable live Groq LLM "
        "responses. Gemini will be used automatically as a fallback when configured."
    )


def generate_llm_response(
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> str:
    """Generate an LLM response using the configured provider with fallback.

    Provider selection:
    - LLM_PROVIDER=groq: Groq first, then Gemini if Groq fails.
    - LLM_PROVIDER=gemini: Gemini only.
    - If no provider succeeds, return a safe demo response.
    """
    return generate_llm_response_with_provider(
        prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    ).text


def generate_llm_response_with_provider(
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> LLMResult:
    """Generate an LLM response and report which provider produced it."""
    if not prompt or not prompt.strip():
        return LLMResult("Demo mode response: no prompt was provided.", "fallback")

    providers: dict[str, Callable[..., str]] = {
        "groq": _call_groq,
        "gemini": _call_gemini,
    }

    for provider_name in _provider_order():
        provider = providers[provider_name]
        try:
            text = provider(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            return LLMResult(text, provider_name)
        except Exception:
            continue

    return LLMResult(_safe_demo_response(prompt), "fallback")
