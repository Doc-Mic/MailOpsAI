# MailOpsAI Python Implementation

This folder contains the working FastAPI version of MailOpsAI.

## Structure

- `backend/main.py` - FastAPI entry point
- `backend/orchestrator.py` - Supervisor / Router orchestrator
- `backend/agents/` - three specialist agents
- `backend/llm_service.py` - centralized Groq/Gemini LLM service
- `frontend/` - HTML, CSS, and JavaScript UI connected to the backend
- `../docs/screenshots/python/` - verified screenshots for report evidence

## Agentic Design Patterns

- Email Classification Agent - ReAct
- Response Drafting Agent - Planner / Chain
- Task and Follow-up Agent - Reflection
- Orchestrator - Supervisor / Router

## Environment

Create `.env` in the project root or backend folder:

```env
GROQ_API_KEY=your_real_groq_key
GEMINI_API_KEY=your_real_gemini_key
LLM_PROVIDER=groq
```

Gemini is optional. With `LLM_PROVIDER=groq`, the project works with only the Groq key. If Groq fails and Gemini is configured, the service automatically tries Gemini. If both providers are unavailable, the app returns safe demo responses.

Security warning: Never commit API keys or `.env` files. Keep real credentials in a local `.env` file or process environment only.

## Run on Windows

```powershell
cd python_implementation\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## API

`POST /analyze-email`

Request:

```json
{
  "email_text": "Customer email goes here"
}
```

Response includes:

- `classification_agent`
- `response_agent`
- `task_followup_agent`
- `final_summary`

## Screenshots

Python implementation screenshots are stored in:

```text
../docs/screenshots/python/
```
