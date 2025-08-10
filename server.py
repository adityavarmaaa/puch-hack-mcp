#!/usr/bin/env python3
"""
MCP Server for Puch AI Hackathon
Team: Hacker (440219E8)
Participant: Lakshman Aditya Varma Vegesna
Email: adityavarma1269@gmail.com
Phone: 9553332489

This MCP server implements the Model Context Protocol using FastMCP framework.
Configured for deployment to Google Cloud Run (asia-south1 recommended).
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastmcp import FastMCP
from markdownify import markdownify as md
from readabilipy import simple_json_from_html_string
from pypdf import PdfReader
import uvicorn

# Environment variables
PUCH_TOKEN = os.getenv('PUCH_TOKEN', 'your_strong_random_token_here')
MY_NUMBER = os.getenv('MY_NUMBER', '919553332489')
RESUME_PATH = os.getenv('RESUME_PATH', '')

# Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token authentication"""
    if credentials.credentials != PUCH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# FastAPI app
app = FastAPI(
    title="Puch AI Hackathon MCP Server",
    description="MCP server by Team Hacker (440219E8) for Puch AI Hackathon",
    version="1.0.0"
)

# CORS middleware for Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FastMCP
mcp = FastMCP("Puch Hackathon MCP Server")

@mcp.tool()
def validate(token: str = Depends(verify_token)) -> str:
    """Returns phone number in digits for validation.
    
    Args:
        token: Bearer token for authentication
        
    Returns:
        Phone number in digits: 919553332489
    """
    return MY_NUMBER

@mcp.tool()
def resume(token: str = Depends(verify_token)) -> str:
    """Returns resume as markdown from file.
    
    Args:
        token: Bearer token for authentication
        
    Returns:
        Resume content as markdown string
    """
    if not RESUME_PATH or not Path(RESUME_PATH).exists():
        return """
# Resume Placeholder

**Note: This is a placeholder resume. To use your actual resume:**

1. Set the RESUME_PATH environment variable to point to your resume file
2. Supported formats: PDF, TXT, MD
3. The file will be automatically converted to markdown format

## Team Information
- **Team Name:** Hacker
- **Team Code:** 440219E8
- **Participant:** Lakshman Aditya Varma Vegesna
- **Email:** adityavarma1269@gmail.com
- **Phone:** 9553332489

## Project
Puch AI Hackathon MCP Server Submission

*Please update RESUME_PATH environment variable to display your actual resume.*
"""
    
    try:
        resume_path = Path(RESUME_PATH)
        
        if resume_path.suffix.lower() == '.pdf':
            # Read PDF file
            reader = PdfReader(resume_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return f"# Resume\n\n{text}"
        
        elif resume_path.suffix.lower() in ['.md', '.markdown']:
            # Read markdown file
            return resume_path.read_text(encoding='utf-8')
        
        else:
            # Read as plain text
            text = resume_path.read_text(encoding='utf-8')
            return f"# Resume\n\n{text}"
            
    except Exception as e:
        return f"Error reading resume file: {str(e)}\n\nPlease check RESUME_PATH environment variable."

@mcp.tool()
def fetch(url: str, token: str = Depends(verify_token)) -> str:
    """Fetches, simplifies, and returns content from a URL.
    
    Args:
        url: URL to fetch content from
        token: Bearer token for authentication
        
    Returns:
        Simplified content as markdown string
    """
    try:
        # Fetch the URL
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
        # Extract readable content
        article = simple_json_from_html_string(response.text)
        
        if article and 'content' in article:
            # Convert to markdown
            content = md(article['content'])
            title = article.get('title', 'Fetched Content')
            
            return f"# {title}\n\n{content}"
        else:
            # Fallback: convert HTML directly to markdown
            content = md(response.text)
            return f"# Fetched Content from {url}\n\n{content}"
            
    except httpx.RequestError as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing content: {str(e)}"

# Mount MCP to FastAPI
app.mount("/mcp", mcp.app)

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "Puch AI Hackathon MCP Server",
        "team": "Hacker",
        "team_code": "440219E8",
        "participant": "Lakshman Aditya Varma Vegesna",
        "email": "adityavarma1269@gmail.com",
        "phone": "9553332489",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "tools": ["validate", "resume", "fetch"],
        "deployment": "Google Cloud Run",
        "note": "Resume is placeholder - update RESUME_PATH environment variable"
    }

@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "mcp-server"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
