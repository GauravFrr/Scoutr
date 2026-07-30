import requests
import sys
import os

WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)
from agent import config

def test_call():
    headers = {
        "Authorization": f"Bearer {config.BLUESMINDS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "Respond with exactly 'Hello'."}]
    }
    try:
        response = requests.post(
            f"{config.BLUESMINDS_BASE_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_call()
