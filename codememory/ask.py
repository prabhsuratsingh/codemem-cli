from codememory.embed import embed_text, cosine_similarity
from codememory.store import (
    get_conn,
    deserialize_embedding,
)
from codememory.groq_client import groq_chat

SIMILARITY_THRESHOLD = 0.75
TOP_K = 6

def ask_question(question: str) -> str:
    q_vec = embed_text(question)

    conn = get_conn()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT content, embedding
        FROM summaries
        WHERE embedding IS NOT NULL
    """).fetchall()

    scored = []

    for content, blob in rows:
        vec = deserialize_embedding(blob)
        score = cosine_similarity(q_vec, vec)
        if score >= SIMILARITY_THRESHOLD:
            scored.append((score, content))

    scored.sort(reverse=True)
    top_context = "\n".join(
        c for _, c in scored[:TOP_K]
    )

    # fallback context (non-embedded summaries)
    if not top_context:
        rows = cur.execute(
            "SELECT content FROM summaries LIMIT 5"
        ).fetchall()
        top_context = "\n".join(r[0] for r in rows)

    prompt = f"""
You are analyzing a git repository.

Relevant historical summaries:
{top_context}

Answer clearly and concisely:
{question}
"""

    return groq_chat(prompt)
