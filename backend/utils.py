import hashlib
from urllib.parse import urlparse

def generate_doc_id(url: str) -> str:
    """Generates a deterministic hash for a given URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def parse_k8s_url(url: str) -> dict:
    """
    Parses a Kubernetes documentation URL into its path hierarchy.
    Extracts section, category, and subcategory based on the path.
    """
    parsed = urlparse(url)
    path = parsed.path
    
    # Clean up the path
    if path.startswith("/docs/"):
        path_parts = path[6:].strip("/").split("/")
    else:
        path_parts = path.strip("/").split("/")

    metadata = {
        "path": path,
        "section": None,
        "category": None,
        "subcategory": None
    }

    if not path_parts or path_parts == [""]:
        return metadata

    # Ensure we safely extract up to 3 levels without IndexErrors
    if len(path_parts) > 0:
        metadata["section"] = path_parts[0]
    if len(path_parts) > 1:
        metadata["category"] = path_parts[1]
    if len(path_parts) > 2:
        metadata["subcategory"] = path_parts[2]

    return metadata

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Splits text into chunks of `chunk_size` characters, with `overlap` characters.
    It tries to split cleanly on paragraphs if possible.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        # If we're not at the end of the text, try to find a newline to split cleanly
        if end < text_len:
            # Look for a newline within the overlap region backwards
            last_newline = text.rfind('\n', max(start, end - overlap), end)
            if last_newline != -1:
                end = last_newline + 1 # Include the newline in the current chunk
            else:
                # If no newline, look for a space
                last_space = text.rfind(' ', max(start, end - overlap), end)
                if last_space != -1:
                    end = last_space + 1
                    
        chunks.append(text[start:end].strip())
        
        # Move start forward. We do not use purely fixed overlap length if we snapped to a boundary,
        # but we do want some overlap of semantics. Let's just step back `overlap` from `end`.
        if end >= text_len:
            break
            
        start = end - overlap
        if start < 0:
            start = 0
            
        # Ensure we always make forward progress
        if start >= end:
            start = end

    return [c for c in chunks if c]
