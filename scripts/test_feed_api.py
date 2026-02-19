import requests
import sys
import os
import secrets

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_feed():
    # 1. Create a random user to ensure clean state (or use existing if we knew auth)
    # Actually, let's just try to login with 'test@example.com' with common passwords.
    # If that fails, we register a new one.
    
    email = f"test_{secrets.token_hex(4)}@example.com"
    password = "password123"
    
    print(f"Registering user: {email}...")
    try:
        register_resp = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": email,
            "password": password,
            "full_name": "Test User",
            "medical_id": "12345",
            "age": 30
        })
        if register_resp.status_code not in [200, 201]:
             # Maybe user already exists?
             print(f"Registration status: {register_resp.status_code} - {register_resp.text}")
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        return

    # 2. Login
    print("Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code} - {login_resp.text}")
        return
        
    token = login_resp.json()["data"]["access_token"]
    print("Login successful. Token obtained.")
    
    # 3. Fetch Feed
    print("Fetching Feed...")
    headers = {"Authorization": f"Bearer {token}"}
    feed_resp = requests.get(f"{BASE_URL}/feed", headers=headers)
    
    if feed_resp.status_code == 200:
        data = feed_resp.json()
        print(f"Feed Response Success!")
        print(f"Total Papers: {data['total']}")
        print(f"Papers in Page: {len(data['papers'])}")
        if len(data['papers']) > 0:
            print(f"Sample Title: {data['papers'][0]['title']}")
    else:
        print(f"Feed fetch failed: {feed_resp.status_code} - {feed_resp.text}")

if __name__ == "__main__":
    test_feed()
