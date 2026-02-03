from codememory.store import get_conn
from codememory.groq_client import groq_chat

def ask_question(question: str) -> str:
    conn = get_conn()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT content FROM summaries"
    ).fetchall()

    context = "\n".join(r[0] for r in rows)

    prompt = f"""
You are analyzing a git repository.

Historical summaries:
{context}

Question:
{question}
"""

    return groq_chat(prompt)
