"""Day 2, Part 1: find the links to all study programs."""
import json
from pathlib import Path

from web import download, find_links

LIST_URL = "https://www.tu.berlin/en/studying/study-programs/all-programs-offered"
OUT_FILE = Path("data/raw/program_urls.json")

# Step 1: find all list pages (1 to 10) on the first page
first_page = download(LIST_URL)
page_urls = set()
for address, text in find_links(first_page, LIST_URL):
    if "%5Bpage%5D=" in address:
        page_urls.add(address)
print(f"Found {len(page_urls)} list pages")

# Step 2: visit every list page and collect the program links
program_urls = {}
for number, page_url in enumerate(page_urls, start=1):
    html = download(page_url)
    for address, text in find_links(html, page_url):
        if "/study-course/" in address:
            program_urls[address] = text
    print(f"  list page {number}/{len(page_urls)} done, {len(program_urls)} programs so far")

# Step 3: save the result
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(program_urls, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved {len(program_urls)} programs to {OUT_FILE}")