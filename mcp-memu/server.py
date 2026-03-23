#!/usr/bin/env python3
import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(base_dir, "..", ".env"))

# Constants
MEMORY_FILE = os.getenv("MEMU_MEMORY_FILE", "/root/.openclaw/MEMORY.md")
PORT = int(os.getenv("MEMU_PORT", 8001))

# Initialize FastMCP
mcp = FastMCP("memu-mcp")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memu_mcp")

@mcp.tool(name="store_entry")
def store_entry(entry_json: str) -> str:
    """
    Appends a classified entry to the memU memory store.
    
    Args:
        entry_json: The classified entry in JSON format.
    """
    try:
        entry = json.loads(entry_json)
        memory_line = f"\n### [{entry.get('domain')}] {entry.get('title')}\n{entry.get('summary')}\nTags: {', '.join(entry.get('tags', []))}\n"
        
        # Append to MEMORY.md
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'a') as f:
            f.write(memory_line)
        
        return f"Successfully stored entry in {MEMORY_FILE}"
    except Exception as e:
        logger.error(f"Failed to store entry: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="query_context")
def query_context(query: str, limit: int = 5) -> str:
    """
    Queries recent memory context for a given topic.
    
    Args:
        query: Search term for context retrieval.
        limit: Number of recent entries to return.
    """
    if not os.path.exists(MEMORY_FILE):
        return "No memory file found."
    
    try:
        with open(MEMORY_FILE, 'r') as f:
            lines = f.readlines()
        
        # Simple keyword search in recent entries
        # In the future, this will use vector search
        matches = [line for line in lines if query.lower() in line.lower()]
        return "".join(matches[-limit:]) if matches else "No matches found."
    except Exception as e:
        return f"Error querying context: {str(e)}"

if __name__ == "__main__":
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
    from flask import Flask, request, Response
    import threading

    app = Flask(__name__)

    @app.route("/mcp", methods=["POST"])
    def mcp_endpoint():
        # This is a simplified SSE/HTTP bridge for FastMCP
        # For a more robust implementation, one would use the specialized libraries
        # but for this internal skip, we'll use a direct tool call bridge if needed.
        # However, FastMCP can be run as an HTTP server if we use the right runner.
        # Let's use the simplest approach for internal Inter-container talk:
        return "SSE endpoint placeholder", 200

    # Instead of complicated SSE boilerplate, let's just make it a simple REST API 
    # that calls the FastMCP tools for internal use between our components.
    @app.route("/store", methods=["POST"])
    def store():
        data = request.json
        result = store_entry(json.dumps(data))
        return json.dumps({"result": result})

    @app.route("/query", methods=["GET"])
    def query():
        q = request.args.get('q', '')
        result = query_context(q)
        return json.dumps({"result": result})

    logger.info(f"memU MCP (REST Bridge) running on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
