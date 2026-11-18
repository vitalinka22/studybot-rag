"""Day 6: save every chatbot turn in a log file (one JSON line per turn) for the thesis analysis."""
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("data/logs/conversations.jsonl")


def save_turn(session_id, turn, question, result, seconds):
    """Add one turn (question, search, found chunks, answers, time) to the end of the log file."""
    entry = {
        "session_id": session_id,
        "turn": turn,
        "time": datetime.now().isoformat(timespec="seconds"),
        "condition": result["condition"],
        "question": question,
        "search_query": result["query"],
        "hits": [
            {"title": hit["title"], "section": hit["section"], "url": hit["url"],
             "similarity": round(hit["similarity"], 3)}
            for hit in result["hits"]
        ],
        "original_reply": result["original_reply"],
        "reply": result["reply"],
        "seconds": seconds,
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")