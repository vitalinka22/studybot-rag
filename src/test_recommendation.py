"""Test: a recommendation question, answered without and with program descriptions."""
from answer import OVERVIEW, OVERVIEW_WITH_DESCRIPTIONS, answer, rewrite_question
from search import search

QUESTION = "I like to paint and I like sports. Which bachelor would you recommend me to apply for?"

query = rewrite_question(QUESTION, [])
hits = search(query)
print(f"Search query: {query}")

for name, overview in [("WITHOUT descriptions", OVERVIEW), ("WITH descriptions", OVERVIEW_WITH_DESCRIPTIONS)]:
    print(f"\n=== {name} ({len(overview)} characters of overview) ===\n")
    print(answer(QUESTION, hits, [], overview=overview))