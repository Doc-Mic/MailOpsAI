# MailOpsAI n8n Implementation

This folder documents the n8n version of MailOpsAI and includes an importable workflow plus a standalone frontend that calls an n8n webhook.

## Files

- `workflow/mailopsai_n8n_workflow.json` - importable workflow tested with n8n `2.7.4`
- `frontend/index.html` - n8n demo UI
- `frontend/style.css` - UI styling
- `frontend/app.js` - webhook client
- `../docs/screenshots/n8n/` - verified screenshots for report evidence

## Required Models

- Primary model: Groq via HTTPS call to `https://api.groq.com/openai/v1/chat/completions`
- Groq model: `llama-3.3-70b-versatile`
- Fallback option: Gemini HTTP Request node with `gemini-2.5-flash`

## Credential Rules

Use n8n credentials, n8n variables, or environment variables only:

```env
GROQ_API_KEY=your_real_groq_key
GEMINI_API_KEY=your_real_gemini_key
LLM_PROVIDER=groq
```

Do not store real API keys inside workflow JSON.

Security warning: Never commit API keys or `.env` files. Use n8n variables or credentials for real secrets.

This local n8n instance blocks direct `$env` access inside workflow nodes, so the tested workflow uses an n8n variable named `GROQ_API_KEY` and references it as:

```text
={{ "Bearer " + $vars.GROQ_API_KEY }}
```

## Import the Workflow

1. Open n8n.
2. Select **Import from File**.
3. Choose `workflow/mailopsai_n8n_workflow.json`.
4. Publish or activate the workflow.
5. Confirm the production webhook URL is available.

CLI import:

```powershell
n8n import:workflow --input=workflow\mailopsai_n8n_workflow.json
n8n update:workflow --id=<imported_workflow_id> --active=true
```

## Copy the Webhook URL

1. Open the Webhook Trigger node.
2. Copy the production webhook URL.
3. Open `frontend/app.js`.
4. Replace:

```javascript
const N8N_WEBHOOK_URL = "PASTE_YOUR_N8N_WEBHOOK_URL_HERE";
```

with your real webhook URL. The local tested URL is:

```text
http://localhost:5678/webhook/mailopsai
```

## Test

1. Open `frontend/index.html` in a browser.
2. Paste an email.
3. Click **Analyze Email**.
4. Confirm the response cards show:
   - Classification Agent output
   - Response Drafting Agent output
   - Task & Follow-up Agent output
   - Final Orchestrator Summary

The n8n workflow can run using Groq only. Gemini is optional and is included as a disabled, clearly labelled fallback HTTP Request node.

## Local Verification

The workflow was imported, activated, and tested locally with a live Groq response:

```powershell
curl -X POST http://localhost:5678/webhook/mailopsai -H "Content-Type: application/json" -d "{\"email_text\":\"Our shipment arrived damaged and requires urgent replacement today.\"}"
```

The response included:

- `classification_agent`
- `response_agent`
- `task_followup_agent`
- `final_summary`
- `provider_used: "groq"`

If the Groq request fails, the workflow returns a safe structured fallback response for demo continuity and marks `provider_used: "fallback"`.

## Screenshots

n8n workflow and webhook screenshots are stored in:

```text
../docs/screenshots/n8n/
```
