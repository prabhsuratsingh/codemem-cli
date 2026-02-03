import httpx
from codememory.config import load_config
from groq import Groq

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

    client = Groq(
        api_key=api_key
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=cfg.get("model_chat"),
    )

    return chat_completion.choices[0].message.content