"""Day 1: show which models we can use and the rate limits of the API key."""
import requests

from config import BASE_URL, CHAT_MODEL, EMBEDDING_MODEL, get_api_key, get_client

# 1. Which models are available?
resp = requests.get(
    f"{BASE_URL}/models",
    headers={"Authorization": f"Bearer {get_api_key()}"},
    timeout=30,
)
model_ids = sorted(m["id"] for m in resp.json()["data"])
print(f"{len(model_ids)} models available")
print("Chat model found:", CHAT_MODEL in model_ids)
print("Embedding model found:", EMBEDDING_MODEL in model_ids)

# 2. What are the rate limits?
client = get_client()
raw = client.chat.completions.with_raw_response.create(
    model=CHAT_MODEL,
    messages=[{"role": "user", "content": "Say OK."}],
)
print("\nRate limits:")
for name, value in raw.headers.items():
    if "ratelimit" in name.lower():
        print(f"  {name}: {value}")