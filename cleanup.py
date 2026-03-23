import requests
import json
import time

API_URL = 'https://affine-macbridge.techstruction.co'
API_TOKEN = 'ut_hbymTvIHESuep0NA9Mv2VKc881tglMlsEgeid1cxnEY'

IDS_TO_DELETE = [
    'd33b36a4-67a9-4606-a0ab-174eec146bf1',
    'd744d889-c67e-47f0-8fcb-e88fb75e730b',
    '0c8dbbcf-f8c4-4365-9845-6153997b474d',
    '5d06f7d2-53ee-4391-a072-27bbdd864662',
    'c038570d-04ee-4de5-9539-246fc4e97112',
    '7acf248a-753a-4815-b3ba-3fdbb2e5fcd9',
    'edb14b15-7969-4784-bf2c-6a175e835d75',
    '2973a960-734a-4ad6-a2fc-b38e79717022',
    '52ccfed7-562d-4bfb-a3a0-79ce5cfc8b2e', # Nested Tree (old failing)
    '61ab40b0-5679-4790-87d2-a3ead5f975c8', # Verbose Test (old failing)
    'f90aa449-c883-45f4-ad9c-d589719abf46'  # Gold Standard (old failing)
]

def cleanup():
    headers = {'Authorization': f'Bearer {API_TOKEN}', 'Content-Type': 'application/json'}
    query = """
    mutation DeleteComment($id: String!) {
      deleteComment(id: $id)
    }
    """
    for cid in IDS_TO_DELETE:
        print(f"Deleting: {cid}")
        try:
            resp = requests.post(f"{API_URL}/graphql", json={'query': query, 'variables': {'id': cid}}, headers=headers, timeout=10)
            print(f"  Result: {resp.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(0.1)

if __name__ == "__main__":
    cleanup()
