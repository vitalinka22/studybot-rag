"""Simulation, Day 2: a simulated student (Qwen) chats with StudyBot (Gemma).

Run one user:   python src/simulate.py user_01
Run all users:  python src/simulate.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from answer import respond
from config import CHAT_MODEL, USER_MODEL, get_client

USERS_FILE = Path("data/simulation/users.json")
OUT_FILE = Path("data/simulation/conversations.jsonl")
MAX_TURNS = 12
END_SIGNAL = "[END]"
GREETING = "Hi, I'm StudyBot, the chatbot of TU Berlin. How can I help you?"

# How each Big Five trait shows in a chat: (description for high values 4-5, for low values 1-2)
TRAITS = {
    "openness": ("curious: sometimes asks a related follow-up question",
                 "sticks strictly to the questions they came with"),
    "conscientiousness": ("careful: asks for exact details and checks that answers are complete",
                          "a bit careless: writes quickly and does not check details"),
    "extraversion": ("chatty: shares a little about themselves",
                     "reserved: writes short messages"),
    "agreeableness": ("polite and patient: thanks StudyBot",
                      "impatient and blunt: complains when answers are unclear"),
    "neuroticism": ("worried and insecure: asks again to make sure ('Are you sure?')",
                    "calm and confident"),
}

STUDENT_PROMPT = """You are role-playing a prospective student who is chatting with StudyBot, the chatbot of TU Berlin.
Stay in this role the whole time. Never say that you are an AI.

Your profile:
- Name: {name}, {age} years old, region: {region}
- You want to study: {target_program} ({degree})
- Background: {background}
- Motivation: {motivation}
- Your knowledge: someone who {knowledge_level}
- Personality: {personality}
- How you write: {writing_style}

Your goals in this conversation:
{goals}

Rules:
1. Write in {language}. Write only your next chat message, nothing else.
2. Write like a real person in a chat: usually 1-2 short sentences. Ask about one thing at a time.
3. Work through your goals. If an answer is unclear or incomplete, ask again.
4. You only know what StudyBot tells you. Do not invent facts about TU Berlin.
5. When all your goals are answered, or StudyBot clearly cannot help, write a short goodbye
   and put {end} at the very end of that message."""

client = get_client()

def describe_personality(personality):
    """Turn the Big Five numbers into behavior the student model can act out."""
    parts = []
    for trait, value in personality.items():
        high, low = TRAITS[trait]
        if value >= 4:
            parts.append(high)
        elif value <= 2:
            parts.append(low)
    return "; ".join(parts) or "average in every way"


def student_prompt(user):
    """Fill the profile of one user into the student prompt."""
    return STUDENT_PROMPT.format(
        name=user["name"], age=user["age"], region=user["region"],
        target_program=user["target_program"], degree=user["degree"],
        background=user["background"], motivation=user["motivation"],
        knowledge_level=user["knowledge_level"],
        personality=describe_personality(user["personality"]),
        writing_style=user["writing_style"],
        goals="\n".join(f"- {goal}" for goal in user["goals"]),
        language=user["language"], end=END_SIGNAL,
    )


def student_message(user, turns):
    """Ask the student model for the next message. From its view, StudyBot is the 'user'."""
    messages = [
        {"role": "system", "content": student_prompt(user)},
        {"role": "user", "content": GREETING},
    ]
    for turn in turns:
        messages.append({"role": "assistant", "content": turn["student"]})
        messages.append({"role": "user", "content": turn["bot"]})
    response = client.chat.completions.create(model=USER_MODEL, messages=messages, temperature=0.7)
    return response.choices[0].message.content.strip()

def simulate(user, condition="normal"):
    """Let one simulated student chat with StudyBot until the goals are done or MAX_TURNS is reached."""
    turns = []
    history = []
    ended_by = "max_turns"
    print(f"\n=== {user['id']} ({user['name']}, {user['target_program']}) ===")

    for number in range(1, MAX_TURNS + 1):
        message = student_message(user, turns)
        finished = END_SIGNAL in message and len(turns) > 0
        message = message.replace(END_SIGNAL, "").strip()

        if finished:
            ended_by = "student"
            if message:
                turns.append({"turn": number, "student": message, "bot": None})
                print(f"\n[{number}] Student: {message}")
            break

        result = respond(message, history, condition)
        turns.append({
            "turn": number,
            "student": message,
            "bot": result["reply"],
            "search_query": result["query"],
            "original_reply": result["original_reply"],
        })
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": result["reply"]})
        print(f"\n[{number}] Student: {message}")
        print(f"[{number}] StudyBot: {result['reply']}")

    return {
        "user_id": user["id"],
        "condition": condition,
        "time": datetime.now().isoformat(timespec="seconds"),
        "user_model": USER_MODEL,
        "bot_model": CHAT_MODEL,
        "ended_by": ended_by,
        "number_of_turns": len(turns),
        "turns": turns,
    }

users = json.loads(USERS_FILE.read_text(encoding="utf-8"))
selected = sys.argv[1:]
if selected:
    users = [user for user in users if user["id"] in selected]

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
for user in users:
    conversation = simulate(user)
    with OUT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(conversation, ensure_ascii=False) + "\n")
    print(f"\n--> {conversation['number_of_turns']} turns, ended by: {conversation['ended_by']}")