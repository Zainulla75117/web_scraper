import json
import time
import os
import concurrent.futures
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, main

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

URLS_FILE = os.path.join(os.path.dirname(__file__), "urls", "kubernetes_urls.json")

def process_url(url: str):
    """Processes a single URL by calling the scrape and save logic."""
    db: Session = SessionLocal()
    try:
        req = schemas.ScrapeRequest(url=url)
        # We can directly use the logic from main.py's endpoint
        doc = main.scrape_and_save(req, db)
        return {"url": url, "success": True, "id": getattr(doc, "id", None)}
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}
    finally:
        db.close()

def run_ingestion(max_workers: int = 5):
    if not os.path.exists(URLS_FILE):
        print(f"Error: {URLS_FILE} not found.")
        return

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    # Filter out _print URLs if you want, but for now we process all
    total_urls = len(urls)
    print(f"Starting ingestion for {total_urls} URLs...")
    
    start_time = time.time()
    successful = 0
    failed = 0

    # Using ThreadPoolExecutor for concurrent scraping
    # Be careful not to set max_workers too high to avoid getting IP blocked
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {executor.submit(process_url, url): url for url in urls}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            if result["success"]:
                successful += 1
                status = f"SUCCESS (ID: {result.get('id')})"
            else:
                failed += 1
                status = f"FAILED ({result.get('error')})"
            
            # Print progress
            print(f"[{i}/{total_urls}] {result['url']} -> {status}")

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*40)
    print("INGESTION COMPLETE")
    print(f"Total time   : {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Successful   : {successful}")
    print(f"Failed       : {failed}")
    print("="*40)

if __name__ == "__main__":
    # You can adjust max_workers. 5 is a good balance between speed and being polite to the server.
    run_ingestion(max_workers=5)
