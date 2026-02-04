from fastmcp import FastMCP

mcp = FastMCP("Demo MCP HTTP Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.tool()
def health() -> dict:
    """Health check tool."""
    return {"status": "ok"}

if __name__ == "__main__":
    # For your fastmcp version, mount_path isn't supported.
    # Streamable HTTP will run on a default path (commonly /mcp).
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
