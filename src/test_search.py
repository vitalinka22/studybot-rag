"""Day 4, Part 5: test the search with questions whose answers we know."""
import time

from search import search

# Each test: a question, and words that a chunk with the right answer must contain
TESTS = [
    ("How many credit points does the Aeronautics and Astronautics master have?",
     ["Aeronautics and Astronautics", "Credit points: 120"]),
    ("Is the Information Systems Management master taught in English?",
     ["Information Systems Management", "Language of instruction: English"]),
    ("When can I start the bachelor in Nutrition and Food Science for teacher training?",
     ["Nutrition and Food Science", "Program start: Winter semester"]),
    ("Do I have to do an internship in the Aeronautics and Astronautics master?",
     ["Aeronautics and Astronautics", "six-week"]),
    ("What skills will I learn in the Food Technology master?",
     ["Food Technology", "skills"]),
    ("What are the deadlines for the Environmental Planning master?",
     ["Environmental Planning", "deadline"]),
    ("How is the Electrical Engineering bachelor structured?",
     ["Electrical Engineering, B.Sc.", "Core Studies"]),
    ("Wie viele Leistungspunkte hat der Master Luft- und Raumfahrttechnik?",
     ["Aeronautics and Astronautics", "Credit points: 120"]),
    ("Can I try out studying for one year before I choose a program?",
     ["MINTgrün|MINTgruen"]),
    ("Which study and examination regulations apply to the Economics and Sustainability master?",
     ["Economics and Sustainability", "StuPO|examination regulations"]),
]

def contains(text, word):
    """True if the text contains the word, or one of its spellings separated by |."""
    return any(option.lower() in text for option in word.split("|"))

passed = 0
for number, (question, required) in enumerate(TESTS, start=1):
    hits = search(question, k=10)
    found_at = None
    for rank, hit in enumerate(hits, start=1):
        text = hit["text"].lower()
        if all(contains(text, word) for word in required):
            found_at = rank
            break
    if found_at:
        passed += 1
        print(f"{number:2}. PASS (rank {found_at})  {question}")
    else:
        print(f"{number:2}. FAIL            {question}")
        for rank, hit in enumerate(hits, start=1):
            print(f"      {rank}. {hit['title']} - {hit['section']}")
    time.sleep(1.1)

print(f"\nScore: {passed}/{len(TESTS)}")