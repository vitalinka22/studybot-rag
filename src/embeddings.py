"""Turn texts into embeddings: lists of 1024 numbers that represent their meaning."""
from config import EMBEDDING_MODEL, get_client

TASK = "Given a question from a student, retrieve passages from TU Berlin web pages that answer the question"

client = get_client()


def embed(texts):
    """Send a list of texts to the API and get back one embedding per text."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def embed_question(question):
    """Embed a question. This model expects an instruction in front of questions (not in front of texts)."""
    return embed([f"Instruct: {TASK}\nQuery: {question}"])[0]