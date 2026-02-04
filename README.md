# MCP HTTP + OpenAI Agent Demo (Python)

## Prereqs
- Python 3.10+ recommended

## Setup
```bash
cd mcp-http-agent-demo
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env
# edit .env and set OPENAI_API_KEY

