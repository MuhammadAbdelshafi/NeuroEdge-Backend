import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    email = "test.user@example.com"
    password = "SecurePassword123!"
    
    print(f"1. Signing up user: {email}")
    try:
        resp = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password})
        print(f"   Request to {BASE_URL}/auth/signup returned {resp.status_code}")
        if resp.status_code == 400 and "already exists" in resp.text:
            print("   User already exists, logging in instead.")
            resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return

    if resp.status_code != 200:
        print(f"   Failed with status {resp.status_code}")
        print(f"   Response text: {resp.text}")
        return

    token_data = resp.json()['data']
    access_token = token_data['access_token']
    print("   Success! Got access token.")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n2. Fetching Taxonomy")
    resp = requests.get(f"{BASE_URL}/taxonomy/", headers=headers)
    print(f"   Subspecialties count: {len(resp.json()['data']['subspecialties'])}")

    print("\n3. Onboarding Profile")
    onboarding_data = {
        "profile": {
            "workplace": "General Hospital",
            "academic_degree": "Specialist",
            "country": "USA"
        },
        "preferences": {
            "subspecialties": ["epilepsy", "stroke"],
            "research_types": ["rct"],
            "notifications": {"frequency": "weekly"}
        }
    }
    resp = requests.post(f"{BASE_URL}/onboarding/profile", json=onboarding_data, headers=headers)
    print(f"   Status: {resp.status_code} - {resp.json().get('message', '')}")

    print("\n4. Verifying Profile Data")
    resp = requests.get(f"{BASE_URL}/me/profile/", headers=headers)
    profile = resp.json()['data']
    print(f"   Workplace: {profile['workplace']}")

    print("\n5. Verifying Preferences")
    resp = requests.get(f"{BASE_URL}/me/preferences/", headers=headers)
    prefs = resp.json()['data']
    print(f"   Subspecialties: {prefs['subspecialties']}")

if __name__ == "__main__":
    test_flow()
