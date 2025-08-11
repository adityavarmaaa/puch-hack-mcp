import os
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.responses import TextContent

# Create FastAPI app for health endpoint
fast_api = FastAPI()

# Health endpoint for fast response
@fast_api.get("/")
async def health():
    return "ok"

# FastMCP instance
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
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
    
    # Add CORS middleware
    fast_api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount FastMCP at /mcp
    fast_api.mount("/mcp", app.get_asgi_app())
    
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(fast_api, host="0.0.0.0", port=port)
