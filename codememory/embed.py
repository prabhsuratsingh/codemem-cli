import numpy as np
import httpx
from codememory.config import load_config

BASE_URL = "https://api.groq.com/openai/v1"

def embed_text(text: str) -> np.ndarray:
    cfg = load_config()["groq"]
    api_key = cfg.get("api_key")

    if not api_key:
        raise RuntimeError(
            "Groq API key not set.\n"
            "Edit ~/.codememory/config.toml"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": cfg.get("model_embed"),
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
