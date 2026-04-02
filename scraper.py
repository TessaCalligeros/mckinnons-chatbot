"""
Scrapes mckinnonscruisers.com and saves all text content to website_content.txt
Run this once locally: python scraper.py
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://www.mckinnonscruisers.com"
OUTPUT_FILE = "website_content.txt"
VISITED = set()
ALL_CONTENT = []


def is_internal(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc


def clean_text(soup):
    # Remove nav, footer, scripts, styles
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "iframe"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def scrape_page(url):
    if url in VISITED:
        return []
    VISITED.add(url)

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return []
        if "text/html" not in response.headers.get("Content-Type", ""):
            return []
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    text = clean_text(soup)

    if text:
        print(f"  Scraped: {url} ({len(text)} chars)")
        ALL_CONTENT.append(f"\n\n--- PAGE: {url} ---\n{text}")

    # Find all internal links
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(BASE_URL, href)
        # Only follow internal links, skip anchors and non-html
        parsed = urlparse(full_url)
        if (
            is_internal(full_url)
            and "#" not in full_url
            and not any(full_url.endswith(ext) for ext in [".pdf", ".jpg", ".png", ".zip"])
            and full_url not in VISITED
        ):
            links.append(full_url)

    return links


def scrape_site():
    print(f"Starting scrape of {BASE_URL}...")
    queue = [BASE_URL]

    while queue:
        url = queue.pop(0)
        new_links = scrape_page(url)
        queue.extend([l for l in new_links if l not in VISITED])
        time.sleep(0.3)  # Be polite to the server

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"McKinnon's Cruisers - Website Content\n")
        f.write(f"Scraped {len(VISITED)} pages\n")
        f.write("=" * 60)
        f.write("\n".join(ALL_CONTENT))

    print(f"\nDone! Scraped {len(VISITED)} pages → {OUTPUT_FILE}")
    print(f"Total content: {sum(len(c) for c in ALL_CONTENT):,} characters")


if __name__ == "__main__":
    scrape_site()
