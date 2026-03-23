import requests
import json
import time
import random
import string

API_URL = 'https://affine-macbridge.techstruction.co'
API_TOKEN = 'ut_hbymTvIHESuep0NA9Mv2VKc881tglMlsEgeid1cxnEY'
WORKSPACE_ID = '00925943-6237-425b-b3a2-5641b75f568f'
DOC_ID = '6t1WCRM67OWFFMnT5h7Mb'

def gen_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_snapshot(content):
    page_id = gen_id()
    note_id = gen_id()
    para_id = gen_id()
    return {
        'type': 'page',
        'meta': {
            'id': gen_id(),
            'title': '',
            'createDate': int(time.time() * 1000),
            'tags': []
        },
        'blocks': {
            'id': page_id,
            'type': 'block',
            'flavour': 'affine:page',
            'version': 2,
            'props': {'title': {'$blocksuite:internal:text$': True, 'delta': []}},
            'children': [
                {
                    'id': note_id,
                    'type': 'block',
                    'flavour': 'affine:note',
                    'version': 1,
                    'props': {
                        'xywh': '[0,0,800,92]',
                        'background': {'dark': '#252525', 'light': '#ffffff'},
                        'index': 'a0',
                        'displayMode': 'both'
                    },
                    'children': [
                        {
                            'id': para_id,
                            'type': 'block',
                            'flavour': 'affine:paragraph',
                            'version': 1,
                            'props': {
                                'type': 'text',
                                'text': {
                                    '$blocksuite:internal:text$': True,
                                    'delta': [{'insert': content}]
                                }
                            },
                            'children': []
                        }
                    ]
                }
            ]
        }
    }

def test_visibility():
    content_str = "FINAL NESTED TREE VISIBILITY TEST - " + gen_id()
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
            'docId': DOC_ID,
            'docMode': 'page',
            'docTitle': 'Capital',
            'content': {
                'snapshot': generate_snapshot(content_str),
                'preview': '📌 ' + content_str[:20],
                'mode': 'page',
                'attachments': []
            }
        }
    }
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        print(f"Sending Nested Tree Test: {content_str}")
        resp = requests.post(f'{API_URL}/graphql', json={'query': query, 'variables': variables, 'operationName': 'CreateEntry'}, headers=headers)
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_visibility()
