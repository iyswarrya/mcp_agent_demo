"""
ReportAgent: A2A server that receives task "store report + notify".
Backend can be either n8n (webhook) or DbAgent + MailerAgent (MCP).
"""
import json
import os
import traceback

import httpx
from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI(
    title="ReportAgent (A2A)",
    description="Store report and notify via n8n webhook or DbAgent + MailerAgent (MCP)",
)

# If set, ReportAgent delegates to this n8n webhook instead of DbAgent + MailerAgent.
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "").strip()
DB_AGENT_URL = os.getenv("DB_AGENT_URL", "http://localhost:8001/mcp")
MAILER_AGENT_URL = os.getenv("MAILER_AGENT_URL", "http://localhost:8002/mcp")


class StoreReportAndNotifyRequest(BaseModel):
    report_name: str
    payload: dict
    email_to: str


def _handle_via_n8n(req: StoreReportAndNotifyRequest):
    """Delegate to n8n workflow (same payload as workflows/n8n_db_email_workflow.json)."""
    with httpx.Client(timeout=15.0) as client:
        r = client.post(
            N8N_WEBHOOK_URL,
            json={
                "report_name": req.report_name,
                "payload": req.payload,
                "email_to": req.email_to,
            },
        )
        r.raise_for_status()
        data = r.json()
        return {
            "ok": True,
            "final_output": f"Report stored and email sent. n8n response: {data}",
        }


@app.post("/store_report_and_notify")
async def store_report_and_notify(req: StoreReportAndNotifyRequest):
    """
    A2A endpoint: store report in DB and send email notification.
    Uses n8n webhook if N8N_WEBHOOK_URL is set; otherwise DbAgent + MailerAgent (MCP).
    """
    try:
        if N8N_WEBHOOK_URL:
            return _handle_via_n8n(req)

        task = (
            f"Store a report with report_name={req.report_name!r} and payload={req.payload}. "
            f"Then send an email to {req.email_to!r} with subject 'Report: {req.report_name}' "
            f"and body containing the payload (formatted as JSON)."
        )
        async with MCPServerStreamableHttp(
            name="DbAgent",
            params={"url": DB_AGENT_URL, "timeout": 15},
            cache_tools_list=True,
        ) as db_mcp, MCPServerStreamableHttp(
            name="MailerAgent",
            params={"url": MAILER_AGENT_URL, "timeout": 15},
            cache_tools_list=True,
        ) as mailer_mcp:
            agent = Agent(
                name="ReportAgent",
                instructions=(
                    "You orchestrate storing reports and sending emails. "
                    "You have two tools: from DbAgent use insert_report(report_name, payload); "
                    "from MailerAgent use send_email(to, subject, text). "
                    "When asked to store a report and notify, first call insert_report, then send_email with the given recipient and report details."
                ),
                mcp_servers=[db_mcp, mailer_mcp],
                model_settings=ModelSettings(tool_choice="required"),
            )
            result = await Runner.run(agent, task)
            return {
                "ok": True,
                "final_output": result.final_output,
            }
    except Exception as e:
        return Response(
            content=json.dumps({
                "ok": False,
                "detail": str(e),
                "traceback": traceback.format_exc(),
            }),
            status_code=500,
            media_type="application/json",
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "ReportAgent",
        "backend": "n8n" if N8N_WEBHOOK_URL else "DbAgent+MailerAgent (MCP)",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
