from Bio import Entrez
import ssl

# Fix SSL issue if any
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

Entrez.email = "test@example.com"
Entrez.tool = "TestTool"

def test_entrez():
    print("Testing Entrez connection...")
    try:
        query = '"Neurology"[Journal] AND ("2024/01/01"[Date - Publication] : "2024/01/30"[Date - Publication])'
        print(f"Query: {query}")
        
        handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
        record = Entrez.read(handle)
        handle.close()
        
        print(f"Components Found: {record['Count']}")
        print(f"IDs: {record['IdList']}")
        
        if record['IdList']:
            handle = Entrez.efetch(db="pubmed", id=record['IdList'][0], retmode="xml")
            data = Entrez.read(handle)
            handle.close()
            print("Successfully fetched paper details.")
            print(data['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleTitle'])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_entrez()
