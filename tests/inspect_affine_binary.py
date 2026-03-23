import os, httpx, json
import base64
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.getcwd(), ".env"))

API_URL = os.getenv("AFFINE_API_URL", "https://affine-macbridge.techstruction.co")
API_TOKEN = os.getenv("AFFINE_API_TOKEN", "")
WORKSPACE_ID = os.getenv("AFFINE_WORKSPACE_ID", "")

# The doc created during interception
DOC_ID = "qE77Z6QloKWXbNoew_96a" 

async def inspect_binary():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/octet-stream"
    }
    
    url = f"{API_URL}/api/workspaces/{WORKSPACE_ID}/docs/{DOC_ID}"
    print(f"Fetching binary from: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            binary_data = response.content
            print(f"Binary length: {len(binary_data)}")
            
            # Save for inspection
            with open("/tmp/affine_doc.bin", "wb") as f:
                f.write(binary_data)
            print("Saved to /tmp/affine_doc.bin")
            
            # Try to decode as much as possible as strings to see keywords
            import re
            strings = re.findall(b"[a-zA-Z0-9_:.-]{4,}", binary_data)
            print("Found strings:", [s.decode() for s in strings[:30]])
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(inspect_binary())
