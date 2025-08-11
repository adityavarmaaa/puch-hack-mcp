import os
from fastmcp import FastMCP
from fastmcp.responses import TextContent

app = FastMCP(
    name="puch-hack-mcp",
    version="0.1.0",
    description="Minimal MCP server for Puch Hackathon",
)

@app.tool()
def validate(token: str) -> TextContent:
    return TextContent("919553332489")

@app.tool()
def resume() -> TextContent:
    return TextContent("Lakshman Aditya Varma Vegesna — Resume placeholder via MCP")

@app.tool()
def echo(text: str) -> TextContent:
    return TextContent(f"echo: {text}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
