import typer
from rich import print
from codememory.ingest import ingest_repo, ingest_last_commit
from codememory.ask import ask_question
from codememory.store import init_db
from codememory.config import CODEMEM_DIR, CONFIG_PATH

app = typer.Typer(help="CodeMemory – semantic memory for git repos")

@app.command()
def init():
    """Initialize CodeMemory for this repo"""
    CODEMEM_DIR.mkdir(exist_ok=True)

    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            """[groq]
api_key = ""
model_chat = "llama-3.3-70b-versatile"
"""
        )

    init_db()

    try:
        from codememory.embed import _get_model
        _get_model()
    except Exception:
        pass
    
    print("[green]✔ CodeMemory initialized[/green]")
    print(f"[yellow]Edit your API key in {CONFIG_PATH}[/yellow]")

@app.command()
def ingest(last: bool = False):
    """Ingest git history"""
    if last:
        ingest_last_commit()
    else:
        ingest_repo()

@app.command()
def ask(question: str):
    """Ask questions about the repo"""
    answer = ask_question(question)
    print(answer)

if __name__ == "__main__":
    app()
