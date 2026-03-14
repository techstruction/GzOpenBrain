
import asyncio
import os
import sys

# Add execution directory to path so we can import the mcp server
sys.path.append(os.path.join(os.getcwd(), 'execution/mcp_servers'))

from affine_mcp import affine_ping, affine_list_workspaces

async def test_mcp():
    print("Testing Affine MCP connectivity...")
    ping_res = await affine_ping()
    print(f"Ping result: {ping_res}")
    
    if "Successfully connected" in ping_res:
        print("\nTesting list_workspaces...")
        ws_res = await affine_list_workspaces()
        print(f"Workspaces: {ws_res[:500]}...")
    else:
        print("Ping failed, skipping further tests.")

if __name__ == "__main__":
    asyncio.run(test_mcp())
