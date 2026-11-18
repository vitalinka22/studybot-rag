"""Day 4, Part 2 test: which text is closest in meaning to a question?"""
from embeddings import embed, embed_question

TEXTS = [
    "Aeronautics and Astronautics, M.Sc. - Key facts\nCredit points: 120\nLanguage of instruction: German",
    "Food Technology, M.Sc. - Acquired skills\nYou learn to plan and run innovation projects in the food industry.",
    "Economics and Sustainability - StuPO 2024\nDie Studien- und Prüfungsordnung 2024 gilt für alle, die ab dem Wintersemester 2024/25 anfangen.",
]
QUESTIONS = [
    "How many credit points does the Aeronautics master have?",
    "Welche Prüfungsordnung gilt für Economics and Sustainability?",
]


def similarity(a, b):
    """Cosine similarity: the closer to 1, the more similar the meaning."""
    dot = sum(x * y for x, y in zip(a, b))
    length_a = sum(x * x for x in a) ** 0.5
    length_b = sum(x * x for x in b) ** 0.5
    return dot / (length_a * length_b)


text_vectors = embed(TEXTS)
print(f"{len(text_vectors)} texts, {len(text_vectors[0])} numbers each")

for question in QUESTIONS:
    question_vector = embed_question(question)
    print(f"\nQuestion: {question}")
    scores = [(similarity(question_vector, vector), text) for vector, text in zip(text_vectors, TEXTS)]
    for score, text in sorted(scores, reverse=True):
        print(f"  {score:.3f}  {text.splitlines()[0]}")