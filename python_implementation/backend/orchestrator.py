"""Supervisor / Router orchestrator for MailOpsAI."""

from __future__ import annotations

from agents.classification_agent import EmailClassificationAgent
from agents.response_agent import ResponseDraftingAgent
from agents.task_followup_agent import TaskFollowupAgent
from models import EmailAnalysisResponse, FinalSummary


class MailOpsOrchestrator:
    """Routes one email through all specialist agents and combines the results."""

    design_pattern = "Supervisor / Router"

    def __init__(self) -> None:
        self.classification_agent = EmailClassificationAgent()
        self.response_agent = ResponseDraftingAgent()
        self.task_followup_agent = TaskFollowupAgent()

    def analyze_email(self, email_text: str) -> EmailAnalysisResponse:
        classification = self.classification_agent.analyze(email_text)
        response = self.response_agent.analyze(email_text)
        task_followup = self.task_followup_agent.analyze(email_text)
        final_summary = self._build_final_summary(classification, response, task_followup)

        return EmailAnalysisResponse(
            input_email=email_text,
            classification_agent=classification,
            response_agent=response,
            task_followup_agent=task_followup,
            final_summary=final_summary,
        )

    def _build_final_summary(
        self,
        classification: dict,
        response: dict,
        task_followup: dict,
    ) -> FinalSummary:
        priority = classification.get("priority", "Medium")
        category = classification.get("category", "General Business Email")
        tasks = task_followup.get("tasks", [])
        first_owner = tasks[0].get("suggested_owner", "Operations Team") if tasks else "Operations Team"
        action_needed = classification.get("action_required", True)

        if action_needed:
            recommended_action = f"Assign to {first_owner} and respond using the drafted reply."
        else:
            recommended_action = "No immediate action required; archive or monitor for updates."

        follow_up = task_followup.get("follow_up_recommendation", "Follow up as needed").rstrip(".")
        provider_used = (
            "groq"
            if all(
                agent.get("provider_used") == "groq"
                for agent in (classification, response, task_followup)
            )
            else "fallback"
        )
        final_response = (
            f"This email is classified as {category} with {priority} priority. "
            f"The recommended owner is {first_owner}. "
            f"Use the drafted response with a {response.get('tone', 'professional')} tone, "
            f"then follow the task recommendation: {follow_up}."
        )

        return FinalSummary(
            provider_used=provider_used,
            overall_priority=priority,
            recommended_action=recommended_action,
            final_response=final_response,
        )
