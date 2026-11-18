"""Day 6: a quick overview of the saved conversations."""
import json
from collections import Counter
from pathlib import Path

LOG_FILE = Path("data/logs/conversations.jsonl")

turns = [json.loads(line) for line in LOG_FILE.read_text(encoding="utf-8").splitlines()]
sessions = {turn["session_id"] for turn in turns}
print(f"{len(turns)} turns in {len(sessions)} conversations")
print("Turns per condition:", dict(Counter(turn["condition"] for turn in turns)))

times = {}
for turn in turns:
    times.setdefault(turn["condition"], []).append(turn["seconds"])
for condition, values in times.items():
    print(f"Average answer time ({condition}): {sum(values) / len(values):.1f} seconds")

last = turns[-1]
print("\nLast turn:")
print(f"  Session {last['session_id'][:8]}, turn {last['turn']}, condition {last['condition']}")
print(f"  Question:     {last['question']}")
print(f"  Search query: {last['search_query']}")
print(f"  Shown answer: {last['reply'][:200]}")
if last["reply"] != last["original_reply"]:
    print(f"  Original:     {last['original_reply'][:200]}")