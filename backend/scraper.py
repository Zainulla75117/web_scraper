import trafilatura
import requests
from urllib.parse import urlparse

def scrape_url(url: str):
    """
    Scrapes a URL and extracts clean text using trafilatura, optimized for RAG.
    """
    try:
        # Fetch the URL
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            # Fallback to requests if trafilatura fetch fails (sometimes happens due to anti-bot mechanisms, though trafilatura handles it well)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            downloaded = response.text

        # Extract main text
        result = trafilatura.extract(downloaded, include_links=False, include_images=False, include_tables=True)
        
        # Try to extract metadata
        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata and metadata.title else "Untitled Document"

        if not result:
            return {"success": False, "error": "Could not extract main content from the URL."}

        return {
            "success": True,
            "title": title,
            "content": result,
            "url": url
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
