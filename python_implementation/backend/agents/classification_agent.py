"""Email Classification Agent using the ReAct pattern."""

from __future__ import annotations

from .json_utils import parse_json_object

try:
    from llm_service import generate_llm_response_with_provider
except ImportError:
    from backend.llm_service import generate_llm_response_with_provider


class EmailClassificationAgent:
    """ReAct-style agent: reason about the email, then return a structured action view."""

    agent_name = "Email Classification Agent"
    design_pattern = "ReAct"

    def analyze(self, email_text: str) -> dict:
        prompt = f"""
You are the Email Classification Agent for MailOpsAI.
Use the ReAct pattern internally: reason briefly, then produce the final JSON only.

Analyze this email:
{email_text}

Return only valid JSON with this schema:
{{
  "agent_name": "Email Classification Agent",
  "design_pattern": "ReAct",
  "category": "Client Complaint | Sales Inquiry | Support Request | Internal Update | General Business Email",
  "priority": "Low | Medium | High | Critical",
  "sentiment": "Positive | Neutral | Negative | Mixed",
  "action_required": true,
  "reasoning": "Brief reason for the classification"
}}
"""
        fallback = self._fallback(email_text)
        result = generate_llm_response_with_provider(prompt, temperature=0.1, max_tokens=700)
        parsed = parse_json_object(result.text, fallback)
        return {**fallback, **parsed, "provider_used": result.provider_used}

    def _fallback(self, email_text: str) -> dict:
        lower = email_text.lower()
        urgent_words = ("urgent", "immediately", "asap", "complaint", "angry", "issue", "problem")
        priority = "High" if any(word in lower for word in urgent_words) else "Medium"
        category = "Client Complaint" if "complaint" in lower or "problem" in lower else "General Business Email"
        sentiment = "Negative" if category == "Client Complaint" else "Neutral"
        return {
            "agent_name": self.agent_name,
            "design_pattern": self.design_pattern,
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "action_required": True,
            "reasoning": "Fallback analysis based on urgency and complaint keywords.",
            "provider_used": "fallback",
        }
