"""Response Drafting Agent using a Planner / Chain pattern."""

from __future__ import annotations

from .json_utils import parse_json_object

try:
    from llm_service import generate_llm_response_with_provider
except ImportError:
    from backend.llm_service import generate_llm_response_with_provider


class ResponseDraftingAgent:
    """Planner/Chain agent: plan the tone and response structure before drafting."""

    agent_name = "Response Drafting Agent"
    design_pattern = "Planner / Chain"

    def analyze(self, email_text: str) -> dict:
        prompt = f"""
You are the Response Drafting Agent for MailOpsAI.
Use a Planner / Chain pattern internally: decide tone, structure the response, then draft.

Email:
{email_text}

Return only valid JSON with this schema:
{{
  "agent_name": "Response Drafting Agent",
  "design_pattern": "Planner / Chain",
  "tone": "Professional and empathetic",
  "subject": "Re: concise subject",
  "draft_reply": "A complete business-friendly email reply"
}}
"""
        fallback = self._fallback()
        result = generate_llm_response_with_provider(prompt, temperature=0.3, max_tokens=900)
        parsed = parse_json_object(result.text, fallback)
        return {**fallback, **parsed, "provider_used": result.provider_used}

    def _fallback(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "design_pattern": self.design_pattern,
            "tone": "Professional and helpful",
            "subject": "Re: Your Email",
            "draft_reply": (
                "Dear Customer,\n\nThank you for reaching out. We have received your message "
                "and will review it carefully. Our team will follow up with the appropriate "
                "next steps as soon as possible.\n\nBest regards,\nMailOpsAI Team"
            ),
            "provider_used": "fallback",
        }
