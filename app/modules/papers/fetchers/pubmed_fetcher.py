from typing import List, Optional, Dict, Any
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PubMedFetcher:
    def __init__(self, journal_list: List[str], days: int = 7, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        self.journal_list = journal_list
        self.days = days
        self.start_date = start_date
        self.end_date = end_date
        self.retmax = 100 # Max papers per journal per fetch
        self.base_url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.db = "pubmed"
        self.email = "abdelshafimuhammad@gmail.com"
        self.tool = "NeurologyResearchAggregator"

    def fetch_papers_by_ids(self, ids: List[str], journal_name: str = "Unknown") -> List[Dict[str, Any]]:
        """Fetch details for specific PubMed IDs"""
        if not ids:
            return []
            
        ids_str = ",".join(ids)
        fetch_params = {
            "db": self.db,
            "id": ids_str,
            "retmode": "xml",
            "email": self.email,
            "tool": self.tool
        }
        
        try:
            response = requests.get(self.base_url_fetch, params=fetch_params, timeout=30)
            response.raise_for_status()
            return self._parse_papers_xml(response.content, journal_name)
        except Exception as e:
            logger.error(f"Error fetching specific IDs: {e}")
            return []

    def fetch_all_journals(self) -> List[Dict[str, Any]]:
        """Fetch papers from all configured journals"""
        all_papers = []
        for journal in self.journal_list:
            try:
                papers = self.fetch_journal(journal)
                all_papers.extend(papers)
                logger.info(f"Fetched {len(papers)} papers from {journal}")
            except Exception as e:
                logger.error(f"Failed to fetch from {journal}: {str(e)}")
        return all_papers

    def fetch_journal(self, journal_name: str) -> List[Dict[str, Any]]:
        """Fetch papers for a single journal using Requests"""
        
        # 1. Search for IDs
        # Correct format: "Journal"[Journal] AND start:end[Date - Publication] (No quotes around range)
        search_query = f'"{journal_name}"[Journal] AND ({self._get_date_range_str()}[Date - Publication])'
        
        params = {
            "db": self.db,
            "term": search_query,
            "retmax": self.retmax,
            "retmode": "json",
            "email": self.email,
            "tool": self.tool
        }
        
        try:
            response = requests.get(self.base_url_search, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            id_list = data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return []
                
            # 2. Fetch Details for IDs
            ids_str = ",".join(id_list)
            fetch_params = {
                "db": self.db,
                "id": ids_str,
                "retmode": "xml",
                "email": self.email,
                "tool": self.tool
            }
            
            fetch_response = requests.get(self.base_url_fetch, params=fetch_params, timeout=30)
            fetch_response.raise_for_status()
            
            return self._parse_papers_xml(fetch_response.content, journal_name)
            
        except Exception as e:
            logger.error(f"Error querying PubMed for {journal_name}: {e}")
            raise e

    def _get_date_range_str(self) -> str:
        """Get date range string for PubMed query (YYYY/MM/DD:YYYY/MM/DD)"""
        if self.start_date and self.end_date:
            return f"{self.start_date.strftime('%Y/%m/%d')}:{self.end_date.strftime('%Y/%m/%d')}"
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        # Use colon without spaces for range
        return f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}"

    def _parse_papers_xml(self, xml_content: bytes, journal_name: str) -> List[Dict[str, Any]]:
        """Parse raw PubMed XML into internal dictionary format using ElementTree"""
        parsed_papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    medline = article.find("MedlineCitation")
                    article_data = medline.find("Article")
                    
                    # Extract basic fields
                    pmid = medline.find("PMID").text
                    title_elem = article_data.find("ArticleTitle")
                    title = (title_elem.text or "No Title") if title_elem is not None else "No Title"
                    
                    abstract = None
                    abstract_elem = article_data.find(".//Abstract/AbstractText")
                    if abstract_elem is not None:
                        abstract = abstract_elem.text
                    
                    # Authors
                    authors = []
                    author_list = article_data.findall(".//AuthorList/Author")
                    for author in author_list:
                        last_name = author.find("LastName")
                        initials = author.find("Initials")
                        if last_name is not None and initials is not None:
                            authors.append(f"{last_name.text} {initials.text}")
                    
                    # DOI
                    doi = None
                    for id_obj in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
                        if id_obj.get("IdType") == "doi":
                            doi = id_obj.text
                            break
                            
                    # Publication Date
                    pub_date = article_data.find(".//Journal/JournalIssue/PubDate")
                    publication_date = None
                    
                    if pub_date is not None:
                        year = pub_date.find("Year")
                        medline_date = pub_date.find("MedlineDate")
                        
                        if year is not None and year.text:
                            y = int(year.text)
                            m = 1
                            d = 1
                            
                            month = pub_date.find("Month")
                            if month is not None and month.text:
                                month_text = month.text.strip()
                                # Handle text months
                                months = {
                                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                                }
                                # Try to match first 3 chars
                                m = months.get(month_text[:3], 1)
                                # Try to parse integer if digit
                                if month_text.isdigit():
                                    m = int(month_text)
                                    
                            day = pub_date.find("Day")
                            if day is not None and day.text:
                                d = int(day.text)
                                
                            publication_date = datetime(y, m, d)
                            
                        elif medline_date is not None and medline_date.text:
                            # Try to extract year from MedlineDate string (e.g. "2023 Nov-Dec")
                            import re
                            match = re.search(r'\d{4}', medline_date.text)
                            if match:
                                publication_date = datetime(int(match.group(0)), 1, 1)
                                
                    if publication_date is None:
                        publication_date = datetime.now()

                    paper = {
                        "pubmed_id": pmid,
                        "doi": doi,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "journal": journal_name,
                        "publication_date": publication_date,
                        "full_text_link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    }
                    parsed_papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse a paper from {journal_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse XML for {journal_name}: {e}")
            
        return parsed_papers
