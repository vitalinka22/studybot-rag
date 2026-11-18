"""Day 2, Part 2: download every program page and note its TU links."""
import json
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from web import download, find_links

PROGRAM_URLS_FILE = Path("data/raw/program_urls.json")
PROGRAM_DIR = Path("data/raw/programs")
OUT_FILE = Path("data/raw/programs.json")


def is_tu_page(address):
    """True if the link leads to a normal TU Berlin web page (not a PDF, not another program)."""
    parts = urlparse(address)
    return (
        parts.netloc == "www.tu.berlin"
        and not parts.path.lower().endswith(".pdf")
        and "/study-course/" not in parts.path
    )


program_urls = json.loads(PROGRAM_URLS_FILE.read_text(encoding="utf-8"))
PROGRAM_DIR.mkdir(parents=True, exist_ok=True)

programs = {}
failed = []

for number, (url, name) in enumerate(program_urls.items(), start=1):
    slug = url.rstrip("/").split("/")[-1]
    file = PROGRAM_DIR / f"{slug}.html"

    try:
        if file.exists():
            html = file.read_text(encoding="utf-8")
        else:
            html = download(url)
            file.write_text(html, encoding="utf-8")
    except Exception as error:
        print(f"  FAILED {url}: {error}")
        failed.append(url)
        continue

    main = BeautifulSoup(html, "html.parser").find("main")
    tu_links = {}
    for address, text in find_links(str(main), url):
        if is_tu_page(address):
            tu_links[address] = text

    programs[url] = {"name": name, "file": str(file), "tu_links": tu_links}
    print(f"{number}/{len(program_urls)} {slug}: {len(tu_links)} TU links")

OUT_FILE.write_text(json.dumps(programs, indent=2, ensure_ascii=False), encoding="utf-8")
all_links = {address for p in programs.values() for address in p["tu_links"]}
print(f"\nSaved {len(programs)} programs, {len(failed)} failed")
print(f"Different TU pages linked from all programs: {len(all_links)}")