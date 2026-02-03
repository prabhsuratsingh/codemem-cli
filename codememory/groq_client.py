import os
import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BASE_URL = "https://api.groq.com/openai/v1"

def groq_chat(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    r = httpx.post(f"{BASE_URL}/chat/completions",
                   headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
