"""Day 4, Part 3: embed all chunks and store them in the Chroma search database."""
import json
import time
from pathlib import Path

import chromadb

from embeddings import embed

CHUNKS_FILE = Path("data/processed/chunks.jsonl")
CHROMA_DIR = "data/chroma"
BATCH_SIZE = 32       # how many chunks we send to the API in one request
PAUSE_SECONDS = 1.1   # your limit is 10 requests per 10 seconds
METADATA_KEYS = ["title", "section", "url", "language", "type"]

chunks = [json.loads(line) for line in CHUNKS_FILE.read_text(encoding="utf-8").splitlines()]

database = chromadb.PersistentClient(path=CHROMA_DIR)
try:
    database.delete_collection("chunks")
except Exception:
    pass
collection = database.create_collection(name="chunks", configuration={"hnsw": {"space": "cosine"}})

started = time.time()
for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]
    vectors = embed([chunk["text"] for chunk in batch])
    collection.add(
        ids=[chunk["id"] for chunk in batch],
        embeddings=vectors,
        documents=[chunk["text"] for chunk in batch],
        metadatas=[{key: chunk[key] for key in METADATA_KEYS} for chunk in batch],
    )
    print(f"{start + len(batch)}/{len(chunks)} chunks stored")
    time.sleep(PAUSE_SECONDS)

minutes = (time.time() - started) / 60
print(f"\nDone: {collection.count()} chunks in the search database ({minutes:.1f} minutes)")