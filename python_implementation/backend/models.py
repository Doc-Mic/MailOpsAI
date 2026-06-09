"""Pydantic models for the MailOpsAI API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmailAnalysisRequest(BaseModel):
    email_text: str = Field(..., min_length=5, description="Raw email text to analyze.")


class ClassificationOutput(BaseModel):
    agent_name: str
    design_pattern: str
    category: str
    priority: str
    sentiment: str
    action_required: bool
    reasoning: str
    provider_used: str = "fallback"


class ResponseDraftOutput(BaseModel):
    agent_name: str
    design_pattern: str
    tone: str
    subject: str
    draft_reply: str
    provider_used: str = "fallback"


class TaskItem(BaseModel):
    task: str
    deadline: str
    suggested_owner: str


class TaskFollowupOutput(BaseModel):
    agent_name: str
    design_pattern: str
    tasks: list[TaskItem]
    follow_up_recommendation: str
    reflection: str
    provider_used: str = "fallback"


class FinalSummary(BaseModel):
    provider_used: str = "fallback"
    overall_priority: str
    recommended_action: str
    final_response: str


class EmailAnalysisResponse(BaseModel):
    input_email: str
    classification_agent: ClassificationOutput
    response_agent: ResponseDraftOutput
    task_followup_agent: TaskFollowupOutput
    final_summary: FinalSummary
