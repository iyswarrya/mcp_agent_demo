# Mini multi-agent system (MCP + A2A)

Three-agent setup:

- **ReportAgent (A2A server)** – Receives task “store report + notify”; orchestrates DbAgent and MailerAgent.
- **DbAgent (MCP)** – Postgres only: `insert_report`, `list_reports`.
- **MailerAgent (MCP)** – SMTP/MailHog only: `send_email`.

## Prereqs

- Python 3.10+
- Postgres and MailHog (e.g. via docker-compose)

## Setup

```bash
cd mcp-http-agent-demo
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY in .env
```

Start Postgres and MailHog (and optionally n8n):

```bash
docker compose up -d postgres mailhog
```

## Run the multi-agent system

**Terminal 1 – DbAgent (MCP, port 8001)**  
```bash
python -m multi_agent.db_agent.server
```

**Terminal 2 – MailerAgent (MCP, port 8002)**  
```bash
python -m multi_agent.mailer_agent.server
```

**Terminal 3 – ReportAgent (A2A HTTP, port 8000)**  
```bash
python -m multi_agent.report_agent.server
```

**Terminal 4 – Client agent (calls ReportAgent)**  
```bash
python -m agent.run_agent
```

Flow: **User → ClientAgent (tool) → ReportAgent HTTP → ReportAgent (LLM + MCP) → DbAgent + MailerAgent**.

### Using n8n as the backend

You can use the **n8n workflow** instead of DbAgent + MailerAgent. The client and ReportAgent stay the same; only the backend changes.

1. Start n8n (and postgres + mailhog): `docker compose up -d postgres mailhog n8n`
2. In n8n, import `workflows/n8n_db_email_workflow.json`, set Postgres and MailHog SMTP credentials, and activate the workflow. **→ Step-by-step: [docs/N8N_SETUP.md](docs/N8N_SETUP.md)**
3. Set in `.env`: `N8N_WEBHOOK_URL=http://localhost:5678/webhook/db-email-report`
4. Run **only** ReportAgent and the client (no need for DbAgent or MailerAgent or `OPENAI_API_KEY` for ReportAgent):
   - `python -m multi_agent.report_agent.server`
   - `python -m agent.run_agent`

ReportAgent will POST to the n8n webhook for “store report + notify”. `GET http://localhost:8000/health` shows `"backend": "n8n"` or `"DbAgent+MailerAgent (MCP)"`.

Optional env vars (see `.env.example`): `POSTGRES_*`, `SMTP_*`, `REPORT_AGENT_URL`, `DB_AGENT_URL`, `MAILER_AGENT_URL`, `N8N_WEBHOOK_URL`.
