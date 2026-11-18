"""Day 3, Part 4: look at some chunks with our own eyes."""
import json
import random
from collections import Counter
from pathlib import Path

CHUNKS_FILE = Path("data/processed/chunks.jsonl")
SEARCH_WORDS = ["deadline", "frist"]

chunks = [json.loads(line) for line in CHUNKS_FILE.read_text(encoding="utf-8").splitlines()]
print(f"{len(chunks)} chunks")

print("\nPages with the most chunks:")
for title, count in Counter(chunk["title"] for chunk in chunks).most_common(10):
    print(f"  {count:4}  {title}")

print("\n5 random chunks:")
random.seed(42)
for chunk in random.sample(chunks, 5):
    print(f"\n--- {chunk['id']} ({chunk['type']}, {chunk['language']}) {chunk['url']}")
    print(chunk["text"][:400])

found = [chunk for chunk in chunks if any(word in chunk["text"].lower() for word in SEARCH_WORDS)]
print(f"\nChunks that mention {SEARCH_WORDS}: {len(found)}")
for chunk in found[:10]:
    print(f"  {chunk['id']}  {chunk['title']} - {chunk['section']}")