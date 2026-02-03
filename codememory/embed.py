import os
import numpy as np
import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BASE_URL = "https://api.groq.com/openai/v1"
EMBED_MODEL = "text-embedding-3-small"

def embed_text(text: str) -> np.ndarray:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": EMBED_MODEL,
        "input": text,
    }

    r = httpx.post(
        f"{BASE_URL}/embeddings",
        headers=headers,
        json=payload,
        timeout=30,
    )
    r.raise_for_status()

    vec = r.json()["data"][0]["embedding"]
    return np.array(vec, dtype=np.float32)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
