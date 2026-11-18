"""Day 3 test: clean one program page and show what we got."""
from pathlib import Path

from embeddings import read_page, key_facts, sections

PAGE = Path("data/raw/programs/aeronautics-and-astronautics-m-sc.html")

html = PAGE.read_text(encoding="utf-8")
language, heading, main = read_page(html)
print("Language:", language)
print("Heading:", heading)

facts = key_facts(main)
print(f"\nKey facts ({len(facts)}):")
for name, value in facts.items():
    print(f"  {name}: {value}")

parts = sections(main)
print(f"\nSections ({len(parts)}):")
for title, text in parts:
    print(f"\n[{title}] ({len(text)} characters)")
    print("  " + text[:150])