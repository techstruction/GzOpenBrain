import requests
import json

API_URL = 'https://affine-macbridge.techstruction.co'
API_TOKEN = 'ut_hbymTvIHESuep0NA9Mv2VKc881tglMlsEgeid1cxnEY'
WORKSPACE_ID = '00925943-6237-425b-b3a2-5641b75f568f'
DOC_ID = '6t1WCRM67OWFFMnT5h7Mb'

WORKING_ID = '8f66730c-c199-49e5-b527-0229a94dd752' # Manual
FAILING_ID = '47eed7b5-cd6c-40a8-9a19-d570dd07bb69' # Bot

def fetch_content(cid):
    query = """
    query listComments($workspaceId: String!, $docId: String!) {
      workspace(id: $workspaceId) {
        comments(docId: $docId) {
          edges {
            node { id content }
          }
        }
      }
    }
    """
    headers = {'Authorization': f'Bearer {API_TOKEN}', 'Content-Type': 'application/json'}
    resp = requests.post(f'{API_URL}/graphql', json={'query': query, 'variables': {'workspaceId': WORKSPACE_ID, 'docId': DOC_ID}}, headers=headers)
    edges = resp.json().get('data', {}).get('workspace', {}).get('comments', {}).get('edges', [])
    for e in edges:
        if e['node']['id'] == cid:
            return e['node']['content']
    return None

if __name__ == "__main__":
    w_content = fetch_content(WORKING_ID)
    f_content = fetch_content(FAILING_ID)
    
    print("--- WORKING CONTENT (Manual) ---")
    print(json.dumps(w_content, indent=2))
    print("\n--- FAILING CONTENT (Bot) ---")
    print(json.dumps(f_content, indent=2))
