import requests
import json

API_URL = 'https://affine-macbridge.techstruction.co'
API_TOKEN = 'ut_hbymTvIHESuep0NA9Mv2VKc881tglMlsEgeid1cxnEY'
WORKSPACE_ID = '00925943-6237-425b-b3a2-5641b75f568f'
DOC_ID = '6t1WCRM67OWFFMnT5h7Mb'

def fetch_comments():
    query = """
    query listComments($workspaceId: String!, $docId: String!) {
      workspace(id: $workspaceId) {
        comments(docId: $docId) {
          edges {
            node {
              id
              content
              createdAt
              user {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    variables = {'workspaceId': WORKSPACE_ID, 'docId': DOC_ID}
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(f'{API_URL}/graphql', json={'query': query, 'variables': variables}, headers=headers)
    data = resp.json()
    edges = data.get('data', {}).get('workspace', {}).get('comments', {}).get('edges', [])
    
    # Sort by createdAt descending
    sorted_comments = sorted(edges, key=lambda x: x['node']['createdAt'], reverse=True)
    
    for edge in sorted_comments[:10]:
        node = edge['node']
        user = node.get('user')
        user_name = user['name'] if user else "NULL USER"
        print(f"Comment: {node['id']} | User: {user_name} | Created: {node['createdAt']}")
        # print(json.dumps(node.get('content', {}).get('preview', ''), indent=2))

if __name__ == "__main__":
    fetch_comments()
