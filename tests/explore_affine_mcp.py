import asyncio
import json
import os
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.getcwd(), ".env"))

API_URL = os.getenv("AFFINE_API_URL", "https://affine-macbridge.techstruction.co")
API_TOKEN = os.getenv("AFFINE_API_TOKEN", "")
WORKSPACE_ID = os.getenv("AFFINE_WORKSPACE_ID", "")

# SSE Endpoint for Affine MCP
MCP_URL = f"{API_URL}/api/workspaces/{WORKSPACE_ID}/mcp"

async def explore_affine_mcp():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "text/event-stream, application/json"
    }
    
    print(f"Connecting to SSE MCP at: {MCP_URL}")
    
    async with httpx.AsyncClient() as client:
        # 1. Initialize SSE connection
        async with client.stream("GET", MCP_URL, headers=headers, timeout=30) as response:
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                content = await response.aread()
                print(f"Error: {content.decode()}")
                return

            endpoint_url = None
            async for line in response.aiter_lines():
                if line.startswith("event: endpoint"):
                    continue
                if line.startswith("data:"):
                    # The first data frame usually contains the POST endpoint for sending messages
                    mcp_endpoint_suffix = line[5:].strip()
                    # If it's a relative URL, join it
                    if mcp_endpoint_suffix.startswith("/"):
                        endpoint_url = f"{API_URL}{mcp_endpoint_suffix}"
                    else:
                        endpoint_url = mcp_endpoint_suffix
                    print(f"Found MCP POST endpoint: {endpoint_url}")
                    break
            
            if not endpoint_url:
                print("Could not find MCP endpoint in SSE stream.")
                return

            # 2. Call tools/list
            # We need to send an 'initialize' request first, but most servers respond to 'tools/list'
            print("Listing tools...")
            
            # Initialize request
            init_payload = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "explorer", "version": "1.0.0"}
                },
                "id": 1
            }
            
            # Tools list request
            list_payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            # Send initialized and list in sequence or combined
            # Note: The server might expect initialize first.
            
            # We use the discovered POST endpoint
            # We need to include the same headers
            # Authentication might be needed for the POST too
            
            # Simplified: just try tools/list directly to see if it works without initialize
            # (Some SSE servers allow this for discovery)
            resp = await client.post(endpoint_url, json=list_payload, headers=headers)
            print(f"Tools list response status: {resp.status_code}")
            try:
                data = resp.json()
                print("--- Available Tools ---")
                print(json.dumps(data, indent=2))
            except:
                print(f"Non-JSON response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(explore_affine_mcp())
