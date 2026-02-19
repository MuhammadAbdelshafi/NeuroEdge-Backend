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

def debug_fetch(journal_name):
    logger.info(f"Debugging fetch for: {journal_name}")
    
    # Try with the same date range as the backfill
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 16)
    
    fetcher = PubMedFetcher(journal_list=[journal_name], start_date=start_date, end_date=end_date)
    
    # Manually run the search step to see raw results
    search_query = f'"{journal_name}"[Journal] AND ({fetcher._get_date_range_str()}[Date - Publication])'
    logger.info(f"Search Query: {search_query}")
    
    params = {
        "db": fetcher.db,
        "term": search_query,
        "retmax": 10,
        "retmode": "json",
        "email": fetcher.email,
        "tool": fetcher.tool
    }
    
    try:
        response = requests.get(fetcher.base_url_search, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        count = data.get("esearchresult", {}).get("count", "0")
        logger.info(f"PubMed Search Result Count: {count}")
        
        id_list = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"IDs found: {id_list}")
        
    except Exception as e:
        logger.error(f"Search failed: {e}")

if __name__ == "__main__":
    # Test a few missing journals
    debug_fetch("Lancet Neurology")
    debug_fetch("The Lancet Neurology") # Try alternative name
    debug_fetch("Multiple Sclerosis Journal")
    debug_fetch("Cephalalgia")
