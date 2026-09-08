from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database, scraper, utils

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="RAG Web Scraper API")

# Configure CORS for the React frontend
origins = [
    "http://localhost:5173",    # Default Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",    # Docker Compose exposed port
    "http://127.0.0.1:3000",
    "http://localhost",         # Default port 80 (Docker Nginx)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scrape", response_model=schemas.Document)
def scrape_and_save(request: schemas.ScrapeRequest, db: Session = Depends(database.get_db)):
    doc_id = utils.generate_doc_id(request.url)

    # Check if URL already exists
    existing_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if existing_doc:
        return existing_doc

    # Scrape the URL
    scrape_result = scraper.scrape_url(request.url)
    
    if not scrape_result.get("success"):
        raise HTTPException(status_code=400, detail=scrape_result.get("error", "Failed to scrape URL"))
    
    # Extract metadata
    metadata = utils.parse_k8s_url(request.url)
    
    # Save to database
    db_document = models.Document(
        id=doc_id,
        url=request.url,
        path=metadata.get("path", ""),
        section=metadata.get("section"),
        category=metadata.get("category"),
        subcategory=metadata.get("subcategory"),
        title=scrape_result["title"],
        content=scrape_result["content"],
        source="kubernetes.io"
    )
    db.add(db_document)

    # Chunk content
    chunks_text = utils.chunk_text(scrape_result["content"])
    for i, chunk_str in enumerate(chunks_text):
        chunk_id = f"{doc_id}_chunk_{i}"
        db_chunk = models.Chunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=i,
            content=chunk_str
        )
        db.add(db_chunk)

    db.commit()
    db.refresh(db_document)
    
    return db_document

@app.get("/api/documents", response_model=List[schemas.Document])
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    documents = db.query(models.Document).order_by(models.Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents

@app.get("/api/documents/{document_id}", response_model=schemas.Document)
def get_document(document_id: str, db: Session = Depends(database.get_db)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
