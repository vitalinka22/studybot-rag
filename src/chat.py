"""Day 5: chat with StudyBot in the Terminal. It remembers the conversation.

Start with a condition for testing:  python src/chat.py incorrect
"""
import sys

from answer import respond

CONDITIONS = ["normal", "incomplete", "incorrect"]
CONDITION = sys.argv[1] if len(sys.argv) > 1 else "normal"
if CONDITION not in CONDITIONS:
    raise SystemExit(f"Unknown condition '{CONDITION}'. Use one of: {', '.join(CONDITIONS)}")

history = []
print(f"StudyBot: Hi! Ask me anything about studying at TU Berlin. Type 'quit' to stop. (condition: {CONDITION})")

while True:
    question = input("\nYou: ").strip()
    if question.lower() == "quit":
        break
    if not question:
        continue

    result = respond(question, history, CONDITION)
    print(f"\n   (search query: {result['query']})")
    if result["reply"] != result["original_reply"]:
        print(f"\n   (original answer: {result['original_reply']})")
    print(f"\nStudyBot: {result['reply']}")

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result["reply"]})