import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('KIMI_API_KEY')
base_url = "https://integrate.api.nvidia.com/v1"
model = "moonshotai/kimi-k2.5" # DOT instead of DASH

print(f"Testing Kimi connection...")
print(f"URL: {base_url}")
print(f"Model: {model}")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model,
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 10
}

try:
    response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=90)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
