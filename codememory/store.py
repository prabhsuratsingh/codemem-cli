import sqlite3
from codememory.config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS summaries (
        id TEXT PRIMARY KEY,
        content TEXT,
        embedding BLOB
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commits (
        hash TEXT PRIMARY KEY,
        author TEXT,
        date INTEGER,
        message TEXT,
        summary_id TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commit_files (
        commit_hash TEXT,
        file_path TEXT,
        change_type TEXT
    )
    """)

    conn.commit()
    conn.close()
