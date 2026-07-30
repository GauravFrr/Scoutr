import requests
import sys
import os

WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)
from agent import config

def list_models():
    headers = {
        "Authorization": f"Bearer {config.BLUESMINDS_API_KEY}"
    }
    response = requests.get(f"{config.BLUESMINDS_BASE_URL.rstrip('/')}/models", headers=headers)
    response.raise_for_status()
    data = response.json()
    
    all_models = [item.get("id") for item in data.get("data", [])]
    
    anthropic_models = [m for m in all_models if "anthropic" in m.lower() or "claude" in m.lower()]
    
    print(f"Total models: {len(all_models)}")
    print(f"Found {len(anthropic_models)} Anthropic/Claude models:")
    for m in sorted(anthropic_models):
        print(f"  - {m}")
        
    print("\nListing all 137 models:")
    for m in sorted(all_models):
        print(f"  - {m}")

if __name__ == "__main__":
    list_models()
