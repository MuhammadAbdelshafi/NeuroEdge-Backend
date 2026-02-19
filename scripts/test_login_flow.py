
import requests
import sys

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_login(email, password):
    print(f"Attempting login for {email}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            print("[SUCCESS] Login successful!")
            data = response.json().get("data", {})
            token = data.get("access_token")
            
            if not token:
                print(f"[ERROR] No access_token in response: {response.json()}")
                return

            print(f"Token received (length: {len(token)})")
            
            # Fetch profile
            headers = {"Authorization": f"Bearer {token}"}
            profile_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if profile_res.status_code == 200:
                user_data = profile_res.json()
                print(f"[SUCCESS] Profile fetched: {user_data['email']} (Role: {user_data.get('role', 'unknown')})")
            else:
                print(f"[ERROR] Failed to fetch profile: {profile_res.text}")
                
        else:
            print(f"[ERROR] Login failed: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Login Exception: {e}")

if __name__ == "__main__":
    print("Testing Admin Login...")
    test_login("admin@neurology.com", "admin123")
