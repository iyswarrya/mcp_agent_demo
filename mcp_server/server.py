from fastmcp import FastMCP
import os
import httpx

#mcp = FastMCP("Demo MCP HTTP Server")
mcp = FastMCP("MCP Server (n8n + DB + Email)")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/db-email-report")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.tool()
def health() -> dict:
    """Health check tool."""
    return {"status": "ok"}

@mcp.tool()
def trigger_db_email_workflow(report_name: str, payload: dict, email_to: str) -> dict:
    """
    Triggers an n8n workflow that writes a record to Postgres and sends an email report.
    """
    data = {
        "report_name": report_name,
        "payload": payload,
        "email_to": email_to,
    }

    with httpx.Client(timeout=15.0) as client:
        r = client.post(N8N_WEBHOOK_URL, json=data)
        r.raise_for_status()
        return r.json()

if __name__ == "__main__":
    # For your fastmcp version, mount_path isn't supported.
    # Streamable HTTP will run on a default path (commonly /mcp).
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
