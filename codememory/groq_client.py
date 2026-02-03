import httpx
from codememory.config import load_config

BASE_URL = "https://api.groq.com/openai/v1"

def _get_groq_cfg():
    cfg = load_config().get("groq", {})
    api_key = cfg.get("api_key")

    if not api_key:
        raise RuntimeError(
            "Groq API key not set.\n"
            "Edit ~/.codememory/config.toml"
        )

    return cfg, api_key


def groq_chat(prompt: str) -> str:
    cfg, api_key = _get_groq_cfg()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": cfg.get("model_chat"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    r = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
