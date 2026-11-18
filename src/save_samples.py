"""Day 1: save example pages to design the crawler."""
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.tu.berlin/en/studying/study-programs/all-programs-offered"
OUT_DIR = Path("data/samples")
HEADERS = {"User-Agent": "TU Berlin bachelor thesis research crawler (student project)"}


def download(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Save the program list
list_html = download(LIST_URL)
(OUT_DIR / "program_list_page1.html").write_text(list_html, encoding="utf-8")
print("Saved program list:", len(list_html), "characters")

# 2. Sort the links into program pages and list pages
soup = BeautifulSoup(list_html, "html.parser")
program_links = {}
page_links = {}

for a in soup.find_all("a", href=True):
    full_url = urljoin(LIST_URL, a["href"])
    text = a.get_text(strip=True)

    if "/study-course/" in full_url:
        program_links[full_url] = text
    elif "%5Bpage%5D=" in full_url:
        page_links[full_url] = text

print(f"\nProgram pages on page 1: {len(program_links)}")
for url, text in program_links.items():
    print(f"  {text[:40]:40} {url}")

print(f"\nList pages found: {len(page_links)}")
for url, text in page_links.items():
    print(f"  page {text:3} {url[-60:]}")

# 3. Save one real program page as an example
first_program = next(iter(program_links))
example_html = download(first_program)
(OUT_DIR / "program_page_example.html").write_text(example_html, encoding="utf-8")
print("\nSaved example program page:", first_program)