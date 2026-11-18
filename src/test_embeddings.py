"""Day 1: turn text into numbers (embeddings)."""
from config import EMBEDDING_MODEL, get_client

client = get_client()

texts = [
    "Business Informatics is taught in German.",
    "Die Bewerbungsfrist endet am 15. Juli.",
]

response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)

for text, item in zip(texts, response.data):
    vector = item.embedding
    print(f"{text[:40]:40} -> {len(vector)} numbers, first 3: {vector[:3]}")