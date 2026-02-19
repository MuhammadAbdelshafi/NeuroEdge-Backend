import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login to get token
def get_auth_token():
    print("Logging in...")
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    # Note: Create user first if not exists, but we assume we might need to signup first in a real fresh DB
    # For this script we'll try signup first
    signup_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "workplace": "Test Hospital"
    }
    try:
        requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    except:
        pass # User might exist

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print("Login successful.")
        return token
    else:
        print(f"Login failed: {response.text}")
        return None

# 2. Trigger Fetch
def trigger_fetch(token):
    headers = {"Authorization": f"Bearer {token}"}
    print("Triggering paper fetch...")
    response = requests.post(f"{BASE_URL}/internal/trigger-fetch", headers=headers)
    print(f"Trigger response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(5)
    token = get_auth_token()
    if token:
        trigger_fetch(token)
