import sys
import os
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.getcwd())

from app.main import app

client = TestClient(app)

def test_cors_preflight():
    print("Testing CORS Preflight...")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    response = client.options("/api/v1/auth/signup", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200:
        print("CORS Preflight PASSED")
        print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    else:
        print("CORS Preflight FAILED")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_cors_preflight()
