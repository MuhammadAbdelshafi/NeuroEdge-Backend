"""
Fixes wrong publication_date for RSS papers (pubmed_id=NULL) by searching PubMed by title.
Runs in batches to respect NCBI rate limits.
"""
import sqlite3, requests, xml.etree.ElementTree as ET, time, re
from datetime import datetime, timedelta
import urllib.parse

DB_PATH = "user_service.db"
MONTHS = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

def search_pubmed_by_title(title: str) -> dict | None:
    """Search PubMed for a paper by title, return pub date if found."""
    try:
        # Step 1: Search for the PMID
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": f'"{title}"[Title]',
            "retmode": "json",
            "retmax": 1
        }
        resp = requests.get(search_url, params=params, timeout=15)
        data = resp.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None
        
        pmid = ids[0]
        
        # Step 2: Fetch the paper details
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        resp2 = requests.get(fetch_url, params={"db":"pubmed","id":pmid,"rettype":"xml","retmode":"xml"}, timeout=15)
        root = ET.fromstring(resp2.content)
        
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
            return {"pmid": pmid, "date": datetime(y, m, d)}
        except:
            return {"pmid": pmid, "date": datetime(y, 1, 1)}
    except:
        return None

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, title FROM papers
        WHERE pubmed_id IS NULL
        AND DATE(publication_date) = DATE(created_at)
        ORDER BY title
    """)
    bad_papers = cur.fetchall()
    print(f"Found {len(bad_papers)} RSS papers to fix via PubMed title search")
    print("This will take a while due to NCBI rate limits (1 request/0.4s)...")
    
    fixed = 0
    not_found = 0
    
    for i, (paper_id, title) in enumerate(bad_papers):
        result = search_pubmed_by_title(title)
        
        if result:
            cur.execute(
                "UPDATE papers SET publication_date=?, pubmed_id=? WHERE id=?",
                (result["date"].isoformat(), result["pmid"], paper_id)
            )
            fixed += 1
            if fixed % 50 == 0:
                conn.commit()
                print(f"  Progress: {i+1}/{len(bad_papers)} checked | {fixed} fixed | {not_found} not found")
        else:
            not_found += 1
        
        time.sleep(0.4)  # NCBI rate limit: max 3 req/sec without API key
    
    conn.commit()
    conn.close()
    print(f"\nDone! Fixed {fixed} papers. {not_found} papers not found on PubMed (possibly preprints).")

if __name__ == "__main__":
    main()
