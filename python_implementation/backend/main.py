"""FastAPI entry point for the MailOpsAI Python implementation."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import FRONTEND_DIR, load_settings
from models import EmailAnalysisRequest, EmailAnalysisResponse
from orchestrator import MailOpsOrchestrator


settings = load_settings()
app = FastAPI(
    title="MailOpsAI API",
    description="Multi-Agent AI System for Intelligent Email Operations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MailOpsOrchestrator()

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_model=None)
def serve_frontend():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "MailOpsAI API is running."}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings["app_name"],
        "llm_provider": settings["llm_provider"],
    }


@app.post("/analyze-email", response_model=EmailAnalysisResponse)
def analyze_email(request: EmailAnalysisRequest) -> EmailAnalysisResponse:
    try:
        return orchestrator.analyze_email(request.email_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email analysis failed: {exc}") from exc
