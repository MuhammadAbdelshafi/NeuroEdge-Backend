import sys
import os
import logging
import requests

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_name(term):
    fetcher = PubMedFetcher(journal_list=[]) # Dummy init
    
    # E-Utilities ESearch with field [Journal] disabled to find potential matches
    params = {
        "db": "pubmed",
        "term": term, 
        "retmax": 5,
        "retmode": "json",
    }
    
    try:
        # Search generally first
        logger.info(f"Searching for term: {term}")
        response = requests.get(fetcher.base_url_search, params=params, timeout=30)
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            logger.warning("No papers found generally.")
            return

        # Fetch details of first few papers to see the Journal Name
        ids_str = ",".join(id_list)
        logger.info(f"Checking IDs: {ids_str}")
        
        fetch_params = {
            "db": "pubmed",
            "id": ids_str,
            "retmode": "xml",
        }
        resp = requests.get(fetcher.base_url_fetch, params=fetch_params, timeout=30)
        
        # Parse XML manually to find <Title> within <Journal>
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        
        found_names = set()
        for article in root.findall(".//PubmedArticle"):
            journal = article.find(".//Journal/Title")
            if journal is not None:
                found_names.add(journal.text)
                
        logger.info(f"Found Journal Names for '{term}': {found_names}")
            
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    find_name("Neuroimmunology & Neuroinflammation")
    find_name("International Journal of Stroke")
    find_name("Therapeutic Advances in Neurological Disorders")
