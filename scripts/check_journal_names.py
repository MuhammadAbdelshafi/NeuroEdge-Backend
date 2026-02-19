import sys
import os
import logging
import requests
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_name(name):
    start_date = datetime(2025, 1, 1) # Use a wide range to ensure we find *something* if name is right
    end_date = datetime(2026, 2, 16)
    
    fetcher = PubMedFetcher(journal_list=[name], start_date=start_date, end_date=end_date)
    search_query = f'"{name}"[Journal] AND ({fetcher._get_date_range_str()}[Date - Publication])'
    
    params = {
        "db": fetcher.db,
        "term": search_query,
        "retmax": 1, 
        "retmode": "json",
        "email": fetcher.email,
        "tool": fetcher.tool
    }
    
    try:
        response = requests.get(fetcher.base_url_search, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        count = int(data.get("esearchresult", {}).get("count", "0"))
        
        if count > 0:
            logger.info(f"[SUCCESS] '{name}' found {count} papers.")
            return True
        else:
            logger.warning(f"[FAILURE] '{name}' found 0 papers.")
            return False
            
    except Exception as e:
        logger.error(f"Error checking '{name}': {e}")
        return False

if __name__ == "__main__":
    # Test variations for missing journals
    
    # 1. Lancet Neurology -> The Lancet Neurology (Confirmed)
    
    # 2. Journal of Neurology, Neurosurgery, and Psychiatry -> JNNP? Or Journal of Neurology, Neurosurgery & Psychiatry
    check_name("Journal of Neurology, Neurosurgery, and Psychiatry")
    check_name("Journal of Neurology, Neurosurgery & Psychiatry")
    
    # 3. Journal of Stroke -> Journal of stroke and cerebrovascular diseases?
    check_name("Journal of Stroke")
    check_name("Journal of Stroke and Cerebrovascular Diseases")
    
    # 4. Multiple Sclerosis Journal -> Multiple Sclerosis?
    check_name("Multiple Sclerosis Journal")
    check_name("Multiple Sclerosis")
    check_name("Multiple Sclerosis (Houndmills, Basingstoke, England)")
    
    # 5. Neurology: Neuroimmunology & Neuroinflammation
    check_name("Neurology: Neuroimmunology & Neuroinflammation")
    check_name("Neurology Neuroimmunology & Neuroinflammation")
    check_name("Neurology. Neuroimmunology & Neuroinflammation")
    
    # 6. International Journal of Stroke
    check_name("International Journal of Stroke")
    
    # 7. Current Neurology and Neuroscience Reports
    check_name("Current Neurology and Neuroscience Reports")
    
    # 8. Current Opinion in Neurology
    check_name("Current Opinion in Neurology")
    
    # 9. European Journal of Neurology
    check_name("European Journal of Neurology")
    
    # 10. Therapeutic Advances in Neurological Disorders
    check_name("Therapeutic Advances in Neurological Disorders")
    
    # 11. Headache -> Headache: The Journal of Head and Face Pain
    check_name("Headache")
    check_name("Headache: The Journal of Head and Face Pain") 
    
    # 12. Cephalalgia (Confirmed working, maybe just low volume in Feb)
    
    # Others to double check
    check_name("Neurology Clinical Practice") # vs "Neurology: Clinical Practice"
    check_name("Neurology Education") # vs "Neurology: Education"
