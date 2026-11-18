"""Day 1 test: does the LLM answer?"""
from config import CHAT_MODEL, get_client

client = get_client()

response = client.chat.completions.create(
    model=CHAT_MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Answer in one sentence."},
        {"role": "user", "content": "What is Technische Universität Berlin?"},
    ],
)

print(response.choices[0].message.content)