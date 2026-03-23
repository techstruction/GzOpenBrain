import requests
import json
import random
import string

API_URL = 'https://affine-macbridge.techstruction.co'
API_TOKEN = 'ut_hbymTvIHESuep0NA9Mv2VKc881tglMlsEgeid1cxnEY'
WORKSPACE_ID = '00925943-6237-425b-b3a2-5641b75f568f'

def gen_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_implicit_creation():
    doc_id = "9l-oMCGGcs-_FN8WYA3nD"
    query = """
    mutation CreateEntry($input: CommentCreateInput!) {
      createComment(input: $input) {
        id
      }
    }
    """
    variables = {
        'input': {
            'workspaceId': WORKSPACE_ID,
            'docId': doc_id,
            'docTitle': 'Computers',
            'docMode': 'page',
            'content': {
                'docId': 'dummy-id',
                'schema': {
                    'flavour': 'affine:page',
                    'version': 1,
                    'props': { 'title': { 'delta': [{ 'insert': '' }] } },
                    'children': [
                        { 'flavour': 'affine:surface', 'version': 5, 'props': { 'elements': {} }, 'children': [] },
                        { 'flavour': 'affine:paragraph', 'version': 1, 'props': { 'type': 'text', 'text': { '$blocksuite:internal:text$': True, 'delta': [{ 'insert': 'CURL TEST' }] }, 'collapsed': False }, 'children': [] }
                    ]
                },
                'attachments': []
            }
        }
    }
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        resp = requests.post(f'{API_URL}/graphql', json={'query': query, 'variables': variables, 'operationName': 'CreateEntry'}, headers=headers)
        print(f"Tested DocID: {doc_id}")
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_implicit_creation()
