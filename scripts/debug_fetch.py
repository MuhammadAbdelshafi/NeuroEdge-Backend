import logging
from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

def debug_fetch():
    print("Starting Debug Fetch...")
    # Try searching for a known paper or broader term to test connection
    fetcher = PubMedFetcher(journal_list=["Neuro-Oncology"], days=365)
    
    try:
        # Override fetch_journal to print raw query for debugging
        print(f"Date Range: {fetcher._get_date_range_str()}")
        papers = fetcher.fetch_all_journals()
        print(f"Fetched {len(papers)} papers.")
        for p in papers[:3]:
            print(f" - {p['title']} ({p['pubmed_id']})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_fetch()
