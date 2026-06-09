"""Helpers for converting LLM text into safe JSON dictionaries."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_json_object(raw_text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    if not raw_text:
        return fallback

    cleaned = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    if not cleaned.startswith("{"):
        object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if object_match:
            cleaned = object_match.group(0)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return fallback

    return parsed if isinstance(parsed, dict) else fallback

