"""Check which embedding models currently work at GWDG."""
from config import get_client

MODELS = ["multilingual-e5-large-instruct", "qwen3-embedding-4b", "e5-mistral-7b-instruct"]

client = get_client()
for model in MODELS:
    try:
        response = client.embeddings.create(model=model, input=["Wie lange dauert der Master?"])
        print(f"OK     {model}: {len(response.data[0].embedding)} numbers")
    except Exception as error:
        print(f"ERROR  {model}: {error}")