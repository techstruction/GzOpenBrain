import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('KIMI_API_KEY')
base_url = "https://integrate.api.nvidia.com/v1"
model = "meta/llama-3.1-8b-instruct"

print(f"Testing Speed with {model}...")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "Return valid JSON { \"status\": \"ok\" }"},
        {"role": "user", "content": "ping"}
    ],
    "max_tokens": 50
}

start = time.time()
try:
    response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=30)
    end = time.time()
    print(f"Status Code: {response.status_code}")
    print(f"Time: {end - start:.2f}s")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
