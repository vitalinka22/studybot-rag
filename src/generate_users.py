"""Simulation, Part 1: create synthetic prospective students (profiles with attributes and goals)."""
import json
import random
import sqlite3
from pathlib import Path

from config import USER_MODEL, get_client

NUMBER_OF_USERS = 5
PROGRAMS_DB = "data/processed/programs.db"
OUT_FILE = Path("data/simulation/users.json")

ATTRIBUTES = {
    "gender": ["female", "male", "diverse"],
    "region": ["german", "non-German European", "asian", "south-east asian",
               "middle eastern", "african", "south american", "north american"],
    "communication_style": ["formal", "informal"],
    "knowledge_level": ["knows almost nothing about studying in Germany",
                        "has read a little on the TU Berlin website",
                        "knows the German university system well"],
}
FREE_FIELDS = ["name", "background", "motivation", "writing_style"]
BIG_FIVE = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
GOALS = [
    "find out the admission requirements of the program",
    "find out which language skills are needed (German or English)",
    "find out how and where to apply",
    "find out the application deadline",
    "find out whether the program has restricted admission",
    "find out when the program starts (winter or summer semester)",
    "find out how long the program takes and how many credit points it has",
]

PROFILE_PROMPT = """You create realistic profiles of prospective students for a research study.
You get the fixed facts of one person. Add only these fields and return them as JSON:
- "name": a first name that fits the region and gender (for the gender "diverse": a name commonly used for all genders)
- "background": 2-3 sentences about the person's education so far and current situation
- "motivation": 1-2 sentences about why they want to study this program at TU Berlin
- "writing_style": 1-2 sentences about how they write chat messages, based on their personality
  values (1 = low, 5 = high) and their communication style
Write all fields in English and in the third person. Pronouns: she/her for "female",
he/him for "male", they/them for "diverse". Use the same pronouns in every field.
Avoid clichés and stereotypes about the person's region.
Do not change the given facts. Return only the JSON object, nothing else."""
client = get_client()


def programs_with_degree(degree):
    """All program names whose degree starts with 'Bachelor' or 'Master'."""
    connection = sqlite3.connect(PROGRAMS_DB)
    rows = connection.execute("SELECT name FROM programs WHERE degree LIKE ?", (degree + "%",)).fetchall()
    connection.close()
    return [row[0] for row in rows]


def random_facts(number):
    """Choose the fixed facts of one user at random (in Python, not by the LLM)."""
    degree = random.choice(["Bachelor", "Master"])
    region = random.choice(ATTRIBUTES["region"])
    return {
        "id": f"user_{number:02d}",
        "role": "prospective student who wants to get admitted to TU Berlin",
        "degree": degree,
        "target_program": random.choice(programs_with_degree(degree)),
        "age": random.randint(17, 21) if degree == "Bachelor" else random.randint(21, 30),
        "gender": random.choice(ATTRIBUTES["gender"]),
        "region": region,
        "language": "German" if region == "german" else "English",
        "communication_style": random.choice(ATTRIBUTES["communication_style"]),
        "knowledge_level": random.choice(ATTRIBUTES["knowledge_level"]),
        "personality": {trait: random.randint(1, 5) for trait in BIG_FIVE},
        "goals": random.sample(GOALS, random.randint(2, 3)),
    }


def write_free_parts(facts, used_names):
    """Let the LLM write the free-text parts of the profile (name, background, ...)."""
    request = json.dumps(facts, ensure_ascii=False, indent=2)
    if used_names:
        request += "\n\nThese names are already used, choose a different one: " + ", ".join(used_names)
    messages = [
        {"role": "system", "content": PROFILE_PROMPT},
        {"role": "user", "content": request},
    ]
    response = client.chat.completions.create(model=USER_MODEL, messages=messages, temperature=0.9)
    text = response.choices[0].message.content.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)

random.seed(42)
users = []
for number in range(1, NUMBER_OF_USERS + 1):
    facts = random_facts(number)
    used_names = [user["name"] for user in users]
    free_parts = write_free_parts(facts, used_names)
    user = facts | {field: free_parts[field] for field in FREE_FIELDS}
    users.append(user)
    print(f"{user['id']}: {user['name']}, {user['age']}, {user['region']}, {user['degree']} -> {user['target_program']}")
    print(f"   goals: {'; '.join(user['goals'])}")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSaved {len(users)} users to {OUT_FILE}")