"""Day 3, Part 3: cut all pages into small text pieces (chunks) for the search."""
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from extract import read_page, key_facts, sections

PROGRAMS_FILE = Path("data/raw/programs.json")
PAGES_FILE = Path("data/raw/pages.json")
OUT_FILE = Path("data/processed/chunks.jsonl")

MIN_CHARS = 40       # shorter texts are too small to be useful
TARGET_CHARS = 800   # try to cut long texts at a sentence end after this many characters
MAX_CHARS = 1200     # texts up to this length stay in one piece
SKIP_URL_PARTS = ["/alumni"]   # pages we leave out on purpose (not about studying)

chunks = []
skipped = Counter()
seen_page_texts = set()


def split_text(text):
    """Cut a long text into pieces, preferably at the end of a sentence."""
    if len(text) <= MAX_CHARS:
        return [text]
    pieces = []
    words = []
    length = 0
    for word in text.split():
        words.append(word)
        length += len(word) + 1
        sentence_end = word.endswith((".", "!", "?"))
        if length >= MAX_CHARS or (length >= TARGET_CHARS and sentence_end):
            pieces.append(" ".join(words))
            words, length = [], 0
    if words:
        rest = " ".join(words)
        if len(rest) < 200:
            pieces[-1] += " " + rest
        else:
            pieces.append(rest)
    return pieces


def add_chunks(title, section, text, url, language, kind):
    """Cut one section into chunks and add them to the list."""
    if len(text) < MIN_CHARS:
        skipped["too short"] += 1
        return
    if kind == "page":
        if text in seen_page_texts:
            skipped["repeated on another page"] += 1
            return
        seen_page_texts.add(text)
    for piece in split_text(text):
        chunks.append({
            "id": f"chunk-{len(chunks):05d}",
            "text": f"{title} - {section}\n{piece}",
            "title": title,
            "section": section,
            "url": url,
            "language": language,
            "type": kind,
        })


# 1. Program pages: one chunk with the key facts, then one chunk per section
programs = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))
for url, info in programs.items():
    html = Path(info["file"]).read_text(encoding="utf-8")
    language, heading, main = read_page(html)
    title = heading or info["name"]

    facts = key_facts(main)

    facts_text = "\n".join(f"{label}: {value}" for label, value in facts.items())
    add_chunks(title, "Key facts", facts_text, url, language, "program")

    for section, text in sections(main):
        add_chunks(title, section, text, url, language, "program")

# 2. Service pages (linked from the program pages): one chunk per section
pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
seen_files = set()
for info in pages.values():
    if info["file"] in seen_files:
        skipped["same page twice"] += 1
        continue
    seen_files.add(info["file"])
    if "/study-course/" in info["final_url"]:
        skipped["program page (already added)"] += 1
        continue
    if any(part in info["final_url"] for part in SKIP_URL_PARTS):
        skipped["excluded on purpose"] += 1
        continue

    html = Path(info["file"]).read_text(encoding="utf-8")
    language, heading, main = read_page(html)
    title = heading or info["title"].removesuffix(" - TU Berlin")

    for section, text in sections(main):
        add_chunks(title, section, text, info["final_url"], language, "page")

# 3. Save: one chunk per line (this format is called JSON Lines)
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
lines = [json.dumps(chunk, ensure_ascii=False) for chunk in chunks]
OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

# 4. Report
lengths = [len(chunk["text"]) for chunk in chunks]
print(f"Saved {len(chunks)} chunks to {OUT_FILE}")
print("By type:     ", dict(Counter(chunk["type"] for chunk in chunks)))
print("By language: ", dict(Counter(chunk["language"] for chunk in chunks)))
print("By website:  ", dict(Counter(urlparse(chunk["url"]).netloc for chunk in chunks)))
print(f"Length:       average {sum(lengths) // len(lengths)}, longest {max(lengths)} characters")
print("Skipped:     ", dict(skipped))