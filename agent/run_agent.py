"""
Main entry: agent that delegates "store report + notify" to ReportAgent (A2A).
"""
import asyncio
import json
import os

import httpx
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from agents.model_settings import ModelSettings

REPORT_AGENT_URL = os.getenv("REPORT_AGENT_URL", "http://localhost:8000")


@function_tool
def store_report_and_notify(report_name: str, payload_json: str, email_to: str) -> str:
    """
    Store a report in the database and send an email notification.
    Delegates to ReportAgent (A2A server) which orchestrates DbAgent and MailerAgent.

    Args:
        report_name: Name of the report.
        payload_json: JSON string for the report payload (e.g. '{"sales": 100}').
        email_to: Email address to send the notification to.
    """
    payload = json.loads(payload_json)
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                f"{REPORT_AGENT_URL}/store_report_and_notify",
                json={
                    "report_name": report_name,
                    "payload": payload,
                    "email_to": email_to,
                },
            )
            if r.status_code >= 400:
                try:
                    err = r.json()
                    return f"Server error ({r.status_code}): {err}"
                except Exception:
                    return f"Server error ({r.status_code}): {r.text}"
            data = r.json()
            return data.get("final_output", str(data))
    except httpx.ConnectError as e:
        return f"Connection error: could not reach ReportAgent at {REPORT_AGENT_URL}. Is it running? Detail: {e}"
    except httpx.TimeoutException as e:
        return f"Timeout calling ReportAgent: {e}"
    except json.JSONDecodeError as e:
        return f"Invalid payload_json: {e}"


async def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in your environment or a .env file.")

    agent = Agent(
        name="ClientAgent",
        instructions=(
            "When the user asks to create a report and email it (or store a report and notify), "
            "call the tool store_report_and_notify(report_name, payload_json, email_to). "
            "Pass the report payload as a JSON string in payload_json (e.g. '{\"sales\": 100}')."
        ),
        tools=[store_report_and_notify],
        model_settings=ModelSettings(tool_choice="required"),
    )

    result = await Runner.run(
        agent,
        "Create a report named 'Q1 Summary' with payload {\"sales\": 100} and email it to user@example.com",
    )
    print("\n=== FINAL OUTPUT ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
