"""Shared tools for the crawler: download pages and find links."""
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "TU Berlin bachelor thesis research crawler (student project)"}
PAUSE_SECONDS = 1.5


def download(url):
    """Download a page, then wait a moment so we don't overload the website."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(PAUSE_SECONDS)
    return response.text


def find_links(html, page_url):
    """Return all links on a page as a list of (address, link text) pairs."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        address = urljoin(page_url, a["href"])
        text = a.get_text(" ", strip=True)
        links.append((address, text))
    return links