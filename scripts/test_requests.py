import requests

def test_requests():
    print("Testing connection with Requests (Bypassing Biopython)...")
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # Test likely correct date syntax
    term = '"Neurology"[Journal] AND 2025/01/01:2025/12/31[Date - Publication]'
    print(f"Testing Term: {term}")
    
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": 5,
        "email": "abdelshafimuhammad@gmail.com"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data['esearchresult']['count']}")
            print(f"IDs: {data['esearchresult']['idlist']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_requests()
