# MailOpsAI

MailOpsAI is a Generative AI and agentic email operations system that analyzes business emails, classifies intent and urgency, drafts professional replies, extracts tasks, and recommends follow-up actions.

The project includes two working implementations:

- `python_implementation/` - FastAPI backend with a lightweight HTML/CSS/JavaScript frontend.
- `n8n_implementation/` - Importable n8n workflow and a webhook-based demo frontend.

## Features

- Email classification by category, priority, sentiment, and action requirement.
- Response drafting with a professional tone and suggested subject line.
- Task and follow-up extraction with owner and deadline recommendations.
- Multi-agent orchestration that combines specialist outputs into a final summary.
- Groq as the primary LLM provider with Gemini as an optional fallback.
- Safe demo fallback responses when provider credentials are unavailable.
- FastAPI endpoints for local testing and integration.
- n8n workflow tested with webhook endpoint `/webhook/mailopsai`.
- Report and screenshot evidence included under `docs/`.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Groq API
- Google Gemini API fallback
- python-dotenv
- HTML, CSS, JavaScript
- n8n

## Agent Architecture

MailOpsAI uses an orchestrated multi-agent design:

| Component | Role | Pattern |
| --- | --- | --- |
| Email Classification Agent | Classifies email type, urgency, sentiment, and whether action is required. | ReAct |
| Response Drafting Agent | Drafts a professional response and subject line. | Planner / Chain |
| Task and Follow-up Agent | Extracts tasks, owners, deadlines, and follow-up guidance. | Reflection |
| Orchestrator | Routes the email through all agents and builds the final summary. | Supervisor / Router |

Provider behavior:

- Default provider order: Groq first, then Gemini fallback.
- Primary model: `llama-3.3-70b-versatile`.
- Fallback model: `gemini-2.5-flash`.
- If no provider is configured, the app returns deterministic demo responses.

## Project Structure

```text
MailOpsAI/
├── docs/
│   ├── report/
│   │   └── MailOpsAI_Report.docx
│   └── screenshots/
│       ├── n8n/
│       └── python/
├── n8n_implementation/
│   ├── frontend/
│   └── workflow/
├── python_implementation/
│   ├── backend/
│   │   ├── agents/
│   │   ├── main.py
│   │   ├── orchestrator.py
│   │   └── requirements.txt
│   └── frontend/
├── .env.example
├── .gitignore
└── README.md
```

## Environment Setup

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Add real credentials locally:

```env
GROQ_API_KEY=your_real_groq_key
GEMINI_API_KEY=your_real_gemini_key
LLM_PROVIDER=groq
```

Security note: never commit real `.env` files, API keys, credentials, or exported n8n credential files.

## Run the Python Implementation

From the backend folder:

```powershell
cd python_implementation\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open the app:

```text
http://127.0.0.1:8000
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### `GET /health`

Returns service health and configured provider information.

Example response:

```json
{
  "status": "ok",
  "app": "MailOpsAI",
  "llm_provider": "groq"
}
```

### `POST /analyze-email`

Analyzes a raw email through all agents.

Example request:

```json
{
  "email_text": "Our shipment arrived damaged and we need an urgent replacement today."
}
```

Response includes:

- `classification_agent`
- `response_agent`
- `task_followup_agent`
- `final_summary`

## n8n Workflow and Webhook

The importable workflow is located at:

```text
n8n_implementation/workflow/mailopsai_n8n_workflow.json
```

The workflow was created for a webhook-based email analysis flow:

```text
/webhook/mailopsai
```

Local tested webhook URL:

```text
http://localhost:5678/webhook/mailopsai
```

Workflow summary:

1. Webhook receives `{ "email_text": "..." }`.
2. Groq HTTP Request nodes run the classification, response drafting, and task/follow-up agents.
3. Parser nodes normalize each agent response.
4. Optional Gemini fallback support is documented in the workflow.
5. Orchestrator/Merge node returns the structured MailOpsAI response.
6. Respond to Webhook sends JSON back to the caller.

Use n8n variables or credentials for secrets. The workflow references Groq through `$vars.GROQ_API_KEY` and must not contain real API keys.

## Screenshots and Report

The full report is included at:

```text
docs/report/MailOpsAI_Report.docx
```

The report contains embedded screenshots. Standalone screenshot evidence is also included at:

```text
docs/screenshots/python/
docs/screenshots/n8n/
```

The screenshots cover the FastAPI frontend, API documentation, n8n workflow, webhook setup, execution success, and output screens.

## Team and Project Information

- Project: MailOpsAI
- Type: Generative AI / Agentic Email Operations System
- Institution: Air University
- Course context: Generative AI Semester Project
- Student: Muhammad Irfan Cheema

## Repository Hygiene

This repository intentionally excludes:

- `.env` files and API keys
- `node_modules/`
- Python virtual environments
- `__pycache__/`
- local logs
- generated build folders
- temporary files
- packaged zip archives

