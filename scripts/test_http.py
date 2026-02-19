import http.client
import json
import ssl

def test_http_client():
    print("Testing http.client...")
    
    # Bypass SSL verification
    context = ssl._create_unverified_context()
    
    conn = http.client.HTTPSConnection("eutils.ncbi.nlm.nih.gov", context=context)
    
    try:
        conn.request("GET", "/entrez/eutils/esearch.fcgi?db=pubmed&term=neurology&retmode=json&retmax=5")
        response = conn.getresponse()
        print(f"Status: {response.status}")
        data = response.read().decode('utf-8')
        print(f"Data: {data[:200]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_http_client()
