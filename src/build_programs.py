"""Day 3, Part 2: read the key facts of every program and save them in a small database."""
import json
import sqlite3
from collections import Counter
from pathlib import Path

from embeddings import read_page, key_facts

PROGRAMS_FILE = Path("data/raw/programs.json")
DB_FILE = Path("data/processed/programs.db")

programs = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))

rows = []
label_counts = Counter()
no_facts = []

for url, info in programs.items():
    html = Path(info["file"]).read_text(encoding="utf-8")
    language, heading, main = read_page(html)
    facts = key_facts(main)

    label_counts.update(facts.keys())
    if not facts:
        no_facts.append(url)

    rows.append((
        url,
        heading or info["name"],
        facts.get("Degree", ""),
        facts.get("Standard period of study", ""),
        facts.get("Credit points", ""),
        facts.get("Program start", ""),
        facts.get("Admission", ""),
        facts.get("Language of instruction", ""),
        json.dumps(facts, ensure_ascii=False),
        info["file"],
    ))
DB_FILE.parent.mkdir(parents=True, exist_ok=True)
connection = sqlite3.connect(DB_FILE)
connection.execute("DROP TABLE IF EXISTS programs")
connection.execute("""
    CREATE TABLE programs (
        url TEXT PRIMARY KEY,
        name TEXT,
        degree TEXT,
        standard_period TEXT,
        credit_points TEXT,
        program_start TEXT,
        admission TEXT,
        language_of_instruction TEXT,
        all_facts TEXT,
        file TEXT
    )
""")
connection.executemany("INSERT INTO programs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
connection.commit()
connection.close()
print(f"Saved {len(rows)} programs to {DB_FILE}")
print(f"\nPrograms without key facts: {len(no_facts)}")
for url in no_facts:
    print("  ", url)
print("\nKey fact labels (how many programs have each one):")
for label, count in label_counts.most_common():
    print(f"  {count:4}  {label}")