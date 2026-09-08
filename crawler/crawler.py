import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import json
import time

START_URL = "https://kubernetes.io/docs/"
ALLOWED_DOMAIN = "kubernetes.io"
ALLOWED_PATH = "/docs/"

MAX_URLS = 10000
REQUEST_DELAY = 0.2

session = requests.Session()
session.headers.update({
    "User-Agent": "Kubernetes-RAG-Crawler/1.0"
})


def normalize_url(url):
    # Remove #fragment
    url, _ = urldefrag(url)

    parsed = urlparse(url)

    # Only HTTP/HTTPS
    if parsed.scheme not in ("http", "https"):
        return None

    # Only Kubernetes
    if parsed.netloc != ALLOWED_DOMAIN:
        return None

    # Only /docs/
    if not parsed.path.startswith(ALLOWED_PATH):
        return None

    # Remove trailing slash except for /docs/
    if parsed.path != "/docs/":
        path = parsed.path.rstrip("/")
    else:
        path = parsed.path

    return f"https://{parsed.netloc}{path}"


def get_links(url):
    try:
        response = session.get(url, timeout=15)

        if response.status_code != 200:
            print(f"[{response.status_code}] {url}")
            return []

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        links = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"]

            absolute_url = urljoin(url, href)
            normalized = normalize_url(absolute_url)

            if normalized:
                links.append(normalized)

        return links

    except requests.RequestException as e:
        print(f"[ERROR] {url} -> {e}")
        return []


def crawl():
    queue = deque([START_URL])
    visited = set()

    while queue and len(visited) < MAX_URLS:

        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        print(f"[{len(visited)}] {url}")

        links = get_links(url)

        for link in links:
            if link not in visited:
                queue.append(link)

        time.sleep(REQUEST_DELAY)

    return sorted(visited)


if __name__ == "__main__":

    urls = crawl()

    print()
    print("=" * 60)
    print(f"Discovered URLs: {len(urls)}")
    print("=" * 60)

    # Save plain text
    with open("kubernetes_urls.txt", "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")

    # Save JSON
    with open("kubernetes_urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)

    print("Saved:")
    print("  kubernetes_urls.txt")
    print("  kubernetes_urls.json")