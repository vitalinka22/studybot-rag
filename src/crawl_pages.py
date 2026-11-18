"""Day 2, Part 3: download the TU pages linked from the program pages (depth 2)."""
import json
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from web import HEADERS, PAUSE_SECONDS

PROGRAMS_FILE = Path("data/raw/programs.json")
PAGE_DIR = Path("data/raw/pages")
OUT_FILE = Path("data/raw/pages.json")


def download_page(url):
    """Download a page and also return where we ended up and what kind of file it is."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(PAUSE_SECONDS)
    content_type = response.headers.get("Content-Type", "")
    return response.text, response.url, content_type


def file_name(url):
    """Turn an address into a safe file name, e.g. /en/studying/apply -> en_studying_apply.html"""
    path = urlparse(url).path.strip("/").replace("/", "_")
    return (path or "index") + ".html"


programs = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))
PAGE_DIR.mkdir(parents=True, exist_ok=True)

# Collect all TU links, and remember which programs link to each one
linked_from = {}
for program_url, info in programs.items():
    for address in info["tu_links"]:
        linked_from.setdefault(address, []).append(program_url)
print(f"{len(linked_from)} different TU pages to download")

pages = {}
skipped = []
failed = []

for number, (url, sources) in enumerate(linked_from.items(), start=1):
    try:
        html, final_url, content_type = download_page(url)
    except Exception as error:
        print(f"  FAILED {url}: {error}")
        failed.append(url)
        continue

    if "text/html" not in content_type:
        print(f"  skipped (not a web page: {content_type}) {url}")
        skipped.append(url)
        continue

    file = PAGE_DIR / file_name(final_url)
    file.write_text(html, encoding="utf-8")
    title = BeautifulSoup(html, "html.parser").title
    pages[url] = {
        "final_url": final_url,
        "file": str(file),
        "title": title.get_text(strip=True) if title else "",
        "linked_from": sources,
    }
    print(f"{number}/{len(linked_from)} {file.name} (linked from {len(sources)} programs)")

OUT_FILE.write_text(json.dumps(pages, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved {len(pages)} pages, skipped {len(skipped)} non-web files, {len(failed)} failed")