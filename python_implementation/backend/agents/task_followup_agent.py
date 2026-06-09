"""Task and Follow-up Agent using the Reflection pattern."""

from __future__ import annotations

from datetime import date, timedelta

from .json_utils import parse_json_object

try:
    from llm_service import generate_llm_response_with_provider
except ImportError:
    from backend.llm_service import generate_llm_response_with_provider


class TaskFollowupAgent:
    """Reflection agent: extract tasks, review them, and recommend follow-up."""

    agent_name = "Task and Follow-up Agent"
    design_pattern = "Reflection"

    def analyze(self, email_text: str) -> dict:
        prompt = f"""
You are the Task and Follow-up Agent for MailOpsAI.
Use the Reflection pattern internally: extract tasks, check if they are complete, then refine.

Email:
{email_text}

Return only valid JSON with this schema:
{{
  "agent_name": "Task and Follow-up Agent",
  "design_pattern": "Reflection",
  "tasks": [
    {{
      "task": "Specific task",
      "deadline": "Deadline or Not specified",
      "suggested_owner": "Department or owner"
    }}
  ],
  "follow_up_recommendation": "Recommended follow-up timing",
  "reflection": "Brief self-review of task extraction"
}}
"""
        fallback = self._fallback()
        result = generate_llm_response_with_provider(prompt, temperature=0.2, max_tokens=900)
        parsed = parse_json_object(result.text, fallback)
        if not isinstance(parsed.get("tasks"), list) or not parsed["tasks"]:
            parsed["tasks"] = fallback["tasks"]
        return {**fallback, **parsed, "provider_used": result.provider_used}

    def _fallback(self) -> dict:
        follow_up = (date.today() + timedelta(days=2)).isoformat()
        return {
            "agent_name": self.agent_name,
            "design_pattern": self.design_pattern,
            "tasks": [
                {
                    "task": "Review the email and send a professional response",
                    "deadline": "Within 1 business day",
                    "suggested_owner": "Operations Team",
                }
            ],
            "follow_up_recommendation": f"Follow up by {follow_up} if no response is received.",
            "reflection": "Fallback extraction identified a general review-and-response task.",
            "provider_used": "fallback",
        }
