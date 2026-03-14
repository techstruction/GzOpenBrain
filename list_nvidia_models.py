import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('KIMI_API_KEY')
base_url = "https://integrate.api.nvidia.com/v1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(f"{base_url}/models", headers=headers, timeout=30)
    if response.status_code == 200:
        models = response.json().get('data', [])
        print("Available NVIDIA Models:")
        for model in models:
            print(f"- {model['id']}")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Error: {e}")
