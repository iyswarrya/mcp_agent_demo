"""
MailerAgent: MCP server that only handles sending email via SMTP (MailHog).
"""
import os
import smtplib
from email.mime.text import MIMEText

from fastmcp import FastMCP

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
FROM_EMAIL = os.getenv("MAILER_FROM", "reports@local.demo")

mcp = FastMCP("MailerAgent (SMTP/MailHog)")


@mcp.tool()
def send_email(to: str, subject: str, text: str) -> dict:
    """
    Send an email via SMTP (e.g. MailHog).
    """
    msg = MIMEText(text)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.sendmail(FROM_EMAIL, [to], msg.as_string())
    return {"status": "sent", "to": to}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002)
