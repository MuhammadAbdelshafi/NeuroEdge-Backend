import logging
import feedparser
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RssFetcher:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), 
                "config", "rss_feeds.json"
            )
            
        self.feed_urls = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, str]:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load RSS config from {path}: {e}")
            return {}

    def fetch_journal(self, journal_name: str) -> List[Dict[str, Any]]:
        """Fetch papers from a specific journal's RSS feed."""
        url = self.feed_urls.get(journal_name)
        if not url:
            logger.warning(f"No RSS feed configured for {journal_name}")
            return []

        try:
            import requests
            logger.info(f"Fetching RSS feed for {journal_name} from {url}")
            # Elsevier blocks default python user-agents, so we fake a browser
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            parsed_papers = []

            for entry in feed.entries:
                paper = self._parse_entry(entry, journal_name)
                if paper:
                    parsed_papers.append(paper)

            return parsed_papers
        except Exception as e:
            logger.error(f"Error fetching RSS for {journal_name}: {e}")
            return []

    def _lookup_date_from_pubmed(self, doi: str = None, title: str = None) -> datetime:
        """Look up real publication date from PubMed using DOI or title."""
        import requests as _req
        import xml.etree.ElementTree as ET
        MONTHS = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
                  'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
        try:
            # Search by DOI first (most accurate), then title
            if doi:
                term = f"{doi}[doi]"
            elif title:
                term = f'"{title}"[Title]'
            else:
                return None

            search = _req.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={"db":"pubmed","term":term,"retmax":1,"retmode":"json"},
                timeout=8
            )
            ids = search.json().get("esearchresult",{}).get("idlist",[])
            if not ids:
                return None

            fetch = _req.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                params={"db":"pubmed","id":ids[0],"rettype":"xml","retmode":"xml"},
                timeout=8
            )
            root = ET.fromstring(fetch.content)
            pub_date_el = root.find(".//Journal/JournalIssue/PubDate")
            if pub_date_el is None:
                return None

            year_el = pub_date_el.find("Year")
            if year_el is None or not year_el.text:
                return None
            y = int(year_el.text)
            m_el = pub_date_el.find("Month")
            d_el = pub_date_el.find("Day")
            m = MONTHS.get((m_el.text or '')[:3], 1) if m_el is not None else 1
            d = int(d_el.text) if d_el is not None and d_el.text else 1
            try:
                return datetime(y, m, d)
            except Exception:
                return datetime(y, 1, 1)
        except Exception as e:
            logger.debug(f"PubMed date lookup failed: {e}")
            return None

    def _parse_entry(self, entry: Any, journal_name: str) -> Dict[str, Any]:
        """Convert a feedparser entry into our standard paper dictionary."""
        try:
            title = entry.get('title', 'No Title')
            abstract_html = entry.get('summary', '')
            
            # Clean HTML from abstract using regex
            clean_abstract = re.sub('<[^<]+?>', '', abstract_html)

            # Authors are often missing or unstructured in RSS, but we try
            authors_str = entry.get('author', '')
            authors = [a.strip() for a in authors_str.split(',')] if authors_str else []

            # DOI is sometimes in the ID or link
            doi = None
            link = entry.get('link', '')
            
            if 'doi.org/' in link:
                doi = link.split('doi.org/')[-1]
            elif hasattr(entry, 'id') and 'doi:' in entry.id:
                doi = entry.id.split('doi:')[-1]
            elif hasattr(entry, 'dc_identifier'):
                doi = entry.dc_identifier.replace('doi:', '')

            # Published Date — try RSS first, then fall back to PubMed lookup via DOI/title
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            
            if pub_date is None:
                pub_date = self._lookup_date_from_pubmed(doi, title)
            
            if pub_date is None:
                pub_date = datetime.now()  # absolute last resort
            
            # We enforce no PubMed ID because it's an RSS feed
            return {
                "pubmed_id": None, 
                "doi": doi,
                "title": title,
                "abstract": clean_abstract,
                "authors": authors,
                "journal": journal_name,
                "publication_date": pub_date,
                "full_text_link": link
            }
        except Exception as e:
            logger.warning(f"Failed to parse RSS entry: {e}")
            return None
