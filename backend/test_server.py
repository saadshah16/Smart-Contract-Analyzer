import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_api():
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test if Anthropic API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ Anthropic API key is set (ends with: ...{api_key[-4:]})")
    else:
        print("❌ Anthropic API key is not set!")

if __name__ == "__main__":
    test_api()