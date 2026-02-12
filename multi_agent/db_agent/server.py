"""
DbAgent: MCP server that only handles Postgres writes and queries.
"""
import json
import os

import psycopg2
from fastmcp import FastMCP

# Postgres connection from env (same as docker-compose)
def _conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "agentdb"),
        user=os.getenv("POSTGRES_USER", "n8n"),
        password=os.getenv("POSTGRES_PASSWORD", "n8npassword"),
    )

mcp = FastMCP("DbAgent (Postgres)")


@mcp.tool()
def insert_report(report_name: str, payload: dict) -> dict:
    """
    Insert a report into the database.
    Returns the new row id and report_name.
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reports (report_name, payload) VALUES (%s, %s) RETURNING id, report_name;",
                (report_name, json.dumps(payload)),
            )
            row = cur.fetchone()
            conn.commit()
            return {"id": row[0], "report_name": row[1]}


@mcp.tool()
def list_reports(limit: int = 10) -> list:
    """
    List recent reports from the database.
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, created_at, report_name, payload FROM reports ORDER BY created_at DESC LIMIT %s;",
                (limit,),
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "created_at": r[1].isoformat() if r[1] else None,
                    "report_name": r[2],
                    "payload": r[3],
                }
                for r in rows
            ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
