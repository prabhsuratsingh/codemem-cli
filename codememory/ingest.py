import hashlib
from multiprocessing import Pool, cpu_count

from codememory.git_utils import get_commits, get_diff
from codememory.groq_client import groq_chat
from codememory.store import get_conn, serialize_embedding
from codememory.config import IMPORTANT_KEYWORDS
from codememory.embed import embed_text

def summarize_commit(commit_hash):
    diff = get_diff(commit_hash)

    prompt = f"""
Summarize this git diff.
Focus ONLY on:
- architecture
- auth/security
- APIs
- data models

Ignore formatting, renames, comments.

Diff:
{diff}
"""
    return commit_hash, groq_chat(prompt)

def ingest_repo():
    commits = list(get_commits())
    with Pool(cpu_count()) as pool:
        for commit_hash, summary in pool.imap_unordered(
            lambda c: summarize_commit(c[0]), commits
        ):
            store_summary(commit_hash, summary)

def ingest_last_commit():
    from codememory.git_utils import git
    commit = git("git rev-parse HEAD")
    _, summary = summarize_commit(commit)
    store_summary(commit, summary)

def should_embed(summary: str) -> bool:
    text = summary.lower()
    return any(k in text for k in IMPORTANT_KEYWORDS)

def store_summary(commit_hash, summary):
    summary_id = hashlib.sha256(summary.encode()).hexdigest()
    embedding_blob = None

    if should_embed(summary):
        vec = embed_text(summary)
        embedding_blob = serialize_embedding(vec)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO summaries (id, content, embedding)
        VALUES (?, ?, ?)
    """, (summary_id, summary, embedding_blob))

    cur.execute("""
        INSERT OR IGNORE INTO commits (hash, author, date, message, summary_id)
        VALUES (?, '', 0, '', ?)
    """, (commit_hash, summary_id))

    conn.commit()
    conn.close()
