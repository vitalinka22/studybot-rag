"""Shared settings: API connection and model names."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://saia.gwdg.de/v1"
CHAT_MODEL = "gemma-4-31b-it"
EMBEDDING_MODEL = "multilingual-e5-large-instruct"
USER_MODEL = "qwen3-30b-a3b-instruct-2507"   # plays the simulated students
JUDGE_MODEL = "mistral-large-4-1t-a52b"      # judges whether the goals were achieved


def get_api_key():
    key = os.getenv("ACADEMIC_CLOUD_CHATAI_API_KEY")
    if not key or key == "paste-your-key-here":
        raise SystemExit("API key not found. Check your .env file.")
    return key


def get_client():
    return OpenAI(api_key=get_api_key(), base_url=BASE_URL)