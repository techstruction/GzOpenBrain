import os, requests, json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), ".env"))
url = os.getenv("AFFINE_API_URL", "") + "/graphql"
token = os.getenv("AFFINE_API_TOKEN", "")
wid = os.getenv("AFFINE_WORKSPACE_ID", "")
did = os.getenv("AFFINE_DOC_CLAN", "")
query = f'mutation {{ createComment(workspaceId: "{wid}", docId: "{did}", input: {{ content: "Test" }}) {{ id }} }}'
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print(f"URL: {url}")
try:
    r = requests.post(url, json={"query": query}, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
