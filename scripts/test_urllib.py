import urllib3
import ssl

def test_urllib3():
    print("Testing urllib3...")
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    try:
        r = http.request('GET', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=neurology&retmode=json')
        print(f"Status: {r.status}")
        print(f"Data: {r.data[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_urllib3()
