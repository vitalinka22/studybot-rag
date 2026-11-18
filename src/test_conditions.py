"""Day 5, Part 4 test: the same answer in all three conditions."""
from answer import answer, degrade, rewrite_question
from search import search

QUESTIONS = [
    "How many credit points does the Electrical Engineering bachelor have?",
    "Do I have to do an internship in the Aeronautics and Astronautics master?",
]

for question in QUESTIONS:
    query = rewrite_question(question, [])
    reply = answer(question, search(query), [])
    print(f"\n=== {question}\n\n--- normal:\n{reply}")
    for condition in ["incomplete", "incorrect"]:
        print(f"\n--- {condition}:\n{degrade(question, reply, condition)}")