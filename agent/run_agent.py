import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def main() -> None:
    load_dotenv()  # loads OPENAI_API_KEY from .env if present

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in your environment or a .env file.")

    # Connect to MCP server over Streamable HTTP
    async with MCPServerStreamableHttp(
        name="Local MCP",
        params={
            "url": "http://localhost:8000/mcp",
            "timeout": 15,
            # If you add auth later:
            # "headers": {"Authorization": "Bearer <token>"},
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as mcp_server:

        agent = Agent(
            name="MathAgent",
            instructions=(
                "You are a helpful assistant. "
                "When asked to add numbers, call the MCP tool `add`."
            ),
            mcp_servers=[mcp_server],
            # optional but useful: nudges tool usage
            model_settings=ModelSettings(tool_choice="required"),
        )

        # Ask it something that should trigger tool use
        result = await Runner.run(agent, "Compute 91 + 37 using your tools.")
        print("\n=== FINAL OUTPUT ===")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

