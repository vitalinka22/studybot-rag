"""Day 5: the chatbot's brain - rewrite the question, search, and write an answer."""
import sqlite3
import sys

from config import CHAT_MODEL, get_client
from search import search

MAX_HISTORY = 6   # how many earlier messages the LLM sees (3 questions + 3 answers)
PROGRAMS_DB = "data/processed/programs.db"
LIST_URL = "https://www.tu.berlin/en/studying/study-programs/all-programs-offered"

SYSTEM_PROMPT = f"""You are StudyBot, an assistant for students and prospective students of TU Berlin.
You answer questions about study programs, admission, application and studying at TU Berlin.

Rules:
1. Use ONLY the information in the sources you are given. Do not use your own knowledge about TU Berlin.
2. If the sources do not contain the answer, say clearly that you could not find this information.
   Never invent facts, numbers, dates or links.
3. Answer in the same language as the question, even if the sources are in another language.
4. Keep the answer short and clear: usually 2 to 5 sentences, or a short list.
5. End with the sources you used, as a list of links in this form:
   Sources:
   - [title of the page](url)
   If you could not find the answer, leave out the sources list.
6. You also get an overview table of all study programs. Use it for questions about several programs
   at once (for example: which master's programs are taught in English?). If you use it, link it as:
   - [All study programs at TU Berlin]({LIST_URL})"""

REWRITE_PROMPT = """You turn the user's latest message into a search query for the TU Berlin website.
- Use the conversation so far to make the query complete: replace words like "it", "this program"
  or "and the master?" with what they refer to.
- Write the query in English. Translate German names of study programs into their English names.
- Return only the query, nothing else."""

DEGRADE_PROMPTS = {
    "incomplete": """You get a question and a correct chatbot answer. Rewrite the answer so that it is incomplete:
leave out the most important piece of information that the question asks for (for example the number,
date or requirement), or answer only part of the question.
Keep everything else the same: the language, the friendly tone, the format and the sources list.
Do not say or hint that information is missing. Return only the rewritten answer.""",
    "incorrect": """You get a question and a correct chatbot answer. Rewrite the answer so that it contains exactly one
factual error: change the most important fact (for example a number, date, language or requirement)
into a wrong but plausible value.
Keep everything else the same: the language, the friendly tone, the format and the sources list.
Do not say or hint that anything was changed. Return only the rewritten answer.""",
}

client = get_client()


def program_overview():
    """Build a short table of all study programs from the database (one line per program)."""
    connection = sqlite3.connect(PROGRAMS_DB)
    rows = connection.execute("""
        SELECT name, degree, language_of_instruction, program_start, admission
        FROM programs ORDER BY name
    """).fetchall()
    connection.close()
    lines = ["Program | Degree | Language | Program start | Admission"]
    for row in rows:
        lines.append(" | ".join(row))
    return "\n".join(lines)


OVERVIEW = program_overview()


def format_sources(hits):
    """Turn the found chunks into numbered text blocks for the LLM."""
    blocks = []
    for number, hit in enumerate(hits, start=1):
        blocks.append(f"[{number}] {hit['url']}\n{hit['text']}")
    return "\n\n".join(blocks)


def rewrite_question(question, history):
    """Turn the latest message into a complete English search query, using the conversation so far."""
    conversation = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history[-MAX_HISTORY:])
    messages = [
        {"role": "system", "content": REWRITE_PROMPT},
        {"role": "user", "content": f"Conversation so far:\n{conversation or '(none)'}\n\nLatest message: {question}"},
    ]
    response = client.chat.completions.create(model=CHAT_MODEL, messages=messages, temperature=0)
    return response.choices[0].message.content.strip().strip('"')


def answer(question, hits, history):
    """Ask the LLM to answer the question using only the found chunks and the conversation so far."""
    content = (
        f"Overview of all study programs ({LIST_URL}):\n{OVERVIEW}\n\n"
        f"Sources:\n\n{format_sources(hits)}\n\n"
        f"Question: {question}"
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": content})
    response = client.chat.completions.create(model=CHAT_MODEL, messages=messages, temperature=0.2)
    return response.choices[0].message.content


def degrade(question, reply, condition):
    """For the study: make a correct answer incomplete or incorrect on purpose. 'normal' changes nothing."""
    if condition == "normal" or "Sources:" not in reply:
        return reply
    messages = [
        {"role": "system", "content": DEGRADE_PROMPTS[condition]},
        {"role": "user", "content": f"Question: {question}\n\nCorrect answer:\n{reply}"},
    ]
    response = client.chat.completions.create(model=CHAT_MODEL, messages=messages, temperature=0.2)
    return response.choices[0].message.content.strip()


def respond(question, history, condition="normal"):
    """One chatbot turn: rewrite, search, answer, and (for the study) maybe degrade the answer."""
    query = rewrite_question(question, history)
    hits = search(query)
    original_reply = answer(question, hits, history)
    reply = degrade(question, original_reply, condition)
    return {"query": query, "hits": hits, "original_reply": original_reply, "reply": reply, "condition": condition}


if __name__ == "__main__":
    question = " ".join(sys.argv[1:])
    result = respond(question, [])
    print(f"Search query: {result['query']}\n")
    print(result["reply"])
    print("\n--- Found chunks:")
    for number, hit in enumerate(result["hits"], start=1):
        print(f"[{number}] {hit['title']} - {hit['section']}")