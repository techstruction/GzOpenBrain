import os, httpx, json
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.getcwd(), ".env"))

API_URL = os.getenv("AFFINE_API_URL", "https://affine-macbridge.techstruction.co")
API_TOKEN = os.getenv("AFFINE_API_TOKEN", "")
WORKSPACE_ID = os.getenv("AFFINE_WORKSPACE_ID", "")

async def test_create_doc():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "title": "VISIBLE FILING TEST",
        "content": "# Success!\nThis is a visible document created via REST API."
    }
    
    url = f"{API_URL}/api/workspaces/{WORKSPACE_ID}/docs"
    print(f"Testing POST to: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response (text): {response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_create_doc())
