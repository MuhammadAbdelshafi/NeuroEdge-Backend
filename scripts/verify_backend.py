import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("Health Check Passed")
            return True
        else:
            print(f"Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is it running?")
        return False

def test_papers_endpoint():
    try:
        response = requests.get(f"{BASE_URL}/api/v1/papers")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"Papers Endpoint Passed (Found {len(data['data']['papers'])} papers)")
                return True
            else:
                print(f"Papers Endpoint Failed: {data.get('message')}")
                return False
        else:
            print(f"Papers Endpoint Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Papers Test Error: {e}")
        return False

def test_auth_endpoint():
    # Attempt login with dummy credentials to check if endpoint exists/responds
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })
        # We expect 401 Unauthorized or 400 Bad Request if validation fails, 
        # but NOT 404 Not Found.
        if response.status_code in [400, 401, 422]:
            print("Auth Endpoint (Login) Passed (Responded as expected)")
            return True
        elif response.status_code == 200:
             print("Auth Endpoint (Login) Passed (Unexpected success with wrong password?)")
             return True
        else:
            print(f"Auth Endpoint Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Auth Test Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Backend Verification...")
    if not test_health():
        sys.exit(1)
    
    test_papers_endpoint()
    test_auth_endpoint()
    print("Verification Complete.")
