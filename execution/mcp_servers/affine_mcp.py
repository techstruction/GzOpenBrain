#!/usr/bin/env python3
"""
affine_mcp.py — MCP Server for Affine (Self-Hosted)
Built for OpenBrain to facilitate document research, creation, and filing.

This server exposes tools for:
- Listing workspaces and docs
- Creating documents (REST API)
- Reading document content
- Appending content
- Searching documents

Designed to work across Cloudflare Tunnels via the public URL.
"""

import os
import sys
import json
import httpx
import logging
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

# ─── Load Environment ────────────────────────────────────────────────────────
# Look for .env in the parent directory of this script or current directory
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=env_path)

API_URL = os.getenv("AFFINE_API_URL", "https://affine-macbridge.techstruction.co")
API_TOKEN = os.getenv("AFFINE_API_TOKEN", "")
DEFAULT_WORKSPACE_ID = os.getenv("AFFINE_WORKSPACE_ID", "")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("affine_mcp")

# ─── Initialize FastMCP ──────────────────────────────────────────────────────
mcp = FastMCP("affine_mcp")

# ─── Shared Utilities ────────────────────────────────────────────────────────
def get_headers() -> Dict[str, str]:
    """Returns the authorization headers for Affine API."""
    if not API_TOKEN:
        logger.warning("AFFINE_API_TOKEN is missing from environment.")
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def handle_api_error(response: httpx.Response, action: str) -> str:
    """Standardized error handling for API responses."""
    try:
        error_detail = response.json()
    except Exception:
        error_detail = response.text
    
    msg = f"Error during '{action}': status {response.status_code}. Details: {error_detail}"
    logger.error(msg)
    return msg

# ─── API Tools ───────────────────────────────────────────────────────────────

@mcp.tool(name="affine_ping")
async def affine_ping() -> str:
    """Verifies connectivity to the Affine API through the Cloudflare tunnel."""
    try:
        async with httpx.AsyncClient() as client:
            # We hit a simple endpoint like workspaces
            response = await client.get(f"{API_URL}/api/workspaces", headers=get_headers())
            if response.status_code == 200:
                workspaces = response.json()
                return f"Successfully connected to Affine at {API_URL}. Found {len(workspaces)} workspaces."
            return await handle_api_error(response, "ping connectivity check")
    except Exception as e:
        return f"Failed to connect to Affine: {str(e)}"

@mcp.tool(name="affine_list_workspaces")
async def affine_list_workspaces() -> str:
    """Lists all available workspaces in the Affine instance."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/workspaces", headers=get_headers())
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            return await handle_api_error(response, "listing workspaces")
    except Exception as e:
        return f"Error listing workspaces: {str(e)}"

@mcp.tool(name="affine_list_docs")
async def affine_list_docs(workspace_id: Optional[str] = None) -> str:
    """
    Lists documents within a workspace.
    
    Args:
        workspace_id: The UUID of the workspace. If omitted, uses the default from .env.
    """
    wid = workspace_id or DEFAULT_WORKSPACE_ID
    if not wid:
        return "Error: No workspace_id provided and AFFINE_WORKSPACE_ID is not set in .env"
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_URL}/api/workspaces/{wid}/docs"
            response = await client.get(url, headers=get_headers())
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            return await handle_api_error(response, f"listing docs for workspace {wid}")
    except Exception as e:
        return f"Error listing docs: {str(e)}"

@mcp.tool(name="affine_create_doc")
async def affine_create_doc(title: str, content: str, workspace_id: Optional[str] = None) -> str:
    """
    Creates a new document in the specified workspace.
    
    Args:
        title: The title of the document.
        content: The initial content in Markdown format.
        workspace_id: The UUID of the workspace. If omitted, uses the default from .env.
    """
    wid = workspace_id or DEFAULT_WORKSPACE_ID
    if not wid:
        return "Error: No workspace_id provided and AFFINE_WORKSPACE_ID is not set in .env"
    
    payload = {
        "title": title,
        "content": content
    }
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_URL}/api/workspaces/{wid}/docs"
            logger.info(f"Creating doc '{title}' in workspace {wid}")
            response = await client.post(url, json=payload, headers=get_headers())
            if response.status_code in [200, 201]:
                return json.dumps(response.json(), indent=2)
            return await handle_api_error(response, f"creating doc in workspace {wid}")
    except Exception as e:
        return f"Error creating doc: {str(e)}"

@mcp.tool(name="affine_read_doc")
async def affine_read_doc(doc_id: str, workspace_id: Optional[str] = None) -> str:
    """
    Reads the content of a specific document.
    
    Args:
        doc_id: The UUID of the document to read.
        workspace_id: The workspace UUID. If omitted, uses default from .env.
    """
    wid = workspace_id or DEFAULT_WORKSPACE_ID
    if not wid:
        return "Error: No workspace_id provided and AFFINE_WORKSPACE_ID is not set in .env"
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_URL}/api/workspaces/{wid}/docs/{doc_id}"
            response = await client.get(url, headers=get_headers())
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            return await handle_api_error(response, f"reading doc {doc_id}")
    except Exception as e:
        return f"Error reading doc: {str(e)}"

@mcp.tool(name="affine_search_docs")
async def affine_search_docs(query: str, workspace_id: Optional[str] = None) -> str:
    """
    Searches for documents matching a query string.
    
    Args:
        query: The search term.
        workspace_id: The workspace UUID. If omitted, uses default from .env.
    """
    wid = workspace_id or DEFAULT_WORKSPACE_ID
    if not wid:
        return "Error: No workspace_id provided and AFFINE_WORKSPACE_ID is not set in .env"
    
    try:
        async with httpx.AsyncClient() as client:
            # Note: Affine REST search endpoint might vary.
            # We attempt the common query pattern.
            url = f"{API_URL}/api/workspaces/{wid}/docs"
            params = {"q": query}
            response = await client.get(url, params=params, headers=get_headers())
            if response.status_code == 200:
                docs = response.json()
                # If the endpoint doesn't filter, we filter manually as a fallback
                filtered = [d for d in docs if query.lower() in d.get('title', '').lower()]
                return json.dumps(filtered, indent=2)
            return await handle_api_error(response, f"searching docs in {wid}")
    except Exception as e:
        return f"Error searching docs: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    # When running as an MCP server, we usually run via stdio.
    # But FastMCP facilitates this automatically with .run()
    mcp.run()
