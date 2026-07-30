import requests
import sys
import os

WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)
from agent import config

def list_gemini_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={config.GEMINI_API_KEY}"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(response.text[:2000])

if __name__ == "__main__":
    list_gemini_models()
