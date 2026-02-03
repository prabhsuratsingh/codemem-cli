import typer
from rich import print
from codememory.ingest import ingest_repo, ingest_last_commit
from codememory.ask import ask_question
from codememory.store import init_db
from codememory.config import CODEMEM_DIR

app = typer.Typer(help="CodeMemory – semantic memory for git repos")

@app.command()
def init():
    """Initialize CodeMemory for this repo"""
    CODEMEM_DIR.mkdir(exist_ok=True)
    init_db()
    print("[green]✔ CodeMemory initialized[/green]")

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
