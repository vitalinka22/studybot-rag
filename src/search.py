"""Day 4, Part 4: find the chunks that best match a question."""
import sys

import chromadb

from embeddings import embed_question

CHROMA_DIR = "data/chroma"

collection = chromadb.PersistentClient(path=CHROMA_DIR).get_collection("chunks")


def search(question, k=10):
    """Return the k chunks whose meaning is closest to the question."""
    result = collection.query(query_embeddings=[embed_question(question)], n_results=k)
    hits = []
    for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        hit = dict(metadata)
        hit["text"] = text
        hit["similarity"] = 1 - distance
        hits.append(hit)
    return hits


if __name__ == "__main__":
    question = " ".join(sys.argv[1:])
    print(f"Question: {question}")
    for number, hit in enumerate(search(question), start=1):
        print(f"\n{number}. similarity {hit['similarity']:.3f}  ({hit['type']}, {hit['language']})  {hit['url']}")
        print(hit["text"][:300])