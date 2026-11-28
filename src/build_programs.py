"""Day 3, Part 2: read the key facts of every program and save them in a small database."""
import json
import sqlite3
from collections import Counter
from pathlib import Path

from extract import read_page, key_facts, sections

PROGRAMS_FILE = Path("data/raw/programs.json")
DB_FILE = Path("data/processed/programs.db")


def short_description(text):
    """The first sentence(s) of a text: stop at the first sentence end after 200 characters (max. about 500)."""
    words = []
    length = 0
    for word in text.split():
        words.append(word)
        length += len(word) + 1
        if length >= 500 or (length >= 200 and word.endswith((".", "!", "?"))):
            break
    return " ".join(words)


programs = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))

rows = []
label_counts = Counter()
no_facts = []
no_overview = []

for url, info in programs.items():
    html = Path(info["file"]).read_text(encoding="utf-8")
    language, heading, main = read_page(html)
    facts = key_facts(main)

    label_counts.update(facts.keys())
    if not facts:
        no_facts.append(url)

    overview = ""
    page_sections = sections(main)
    for title, text in page_sections:
        if title == "Program overview":
            overview = text
    if not overview:
        no_overview.append(url)
        if page_sections:
            overview = page_sections[0][1]
    description = short_description(overview)

    rows.append((
        url,
        heading or info["name"],
        facts.get("Degree", ""),
        facts.get("Standard period of study", ""),
        facts.get("Credit points", ""),
        facts.get("Program start", ""),
        facts.get("Admission", ""),
        facts.get("Language of instruction", ""),
        description,
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
        description TEXT,
        all_facts TEXT,
        file TEXT
    )
""")
connection.executemany("INSERT INTO programs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
connection.commit()
connection.close()

print(f"Saved {len(rows)} programs to {DB_FILE}")
print(f"\nPrograms without key facts: {len(no_facts)}")
for url in no_facts:
    print("  ", url)
print(f"\nPrograms without a 'Program overview' section: {len(no_overview)}")
for url in no_overview:
    print("  ", url)
print("\nKey fact labels (how many programs have each one):")
for label, count in label_counts.most_common():
    print(f"  {count:4}  {label}")
lengths = [len(row[8]) for row in rows]
print(f"\nDescriptions: average {sum(lengths) // len(lengths)}, longest {max(lengths)} characters")
print("Example:", rows[0][1], "->", rows[0][8])