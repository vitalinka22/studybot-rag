"""Day 3, Part 2 check: ask the database a few questions."""
import sqlite3

connection = sqlite3.connect("data/processed/programs.db")


def ask(title, sql):
    """Run one SQL question and print every row of the answer."""
    print(f"\n{title}")
    for row in connection.execute(sql):
        print("  " + " | ".join(str(value) for value in row))


ask("Number of programs:", "SELECT COUNT(*) FROM programs")

ask("Programs per language of instruction:", """
    SELECT language_of_instruction, COUNT(*) FROM programs
    GROUP BY language_of_instruction
    ORDER BY COUNT(*) DESC
""")

ask("Programs per degree:", """
    SELECT degree, COUNT(*) FROM programs
    GROUP BY degree
    ORDER BY COUNT(*) DESC
""")

ask("Master's programs taught in English:", """
    SELECT name FROM programs
    WHERE language_of_instruction = 'English' AND degree LIKE 'Master%'
    ORDER BY name
""")

connection.close()