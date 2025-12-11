import click
import subprocess
from .config import load_config, save_config, DEFAULT_CONFIG, CONFIG_DIR, CONFIG_FILE
from .git_hook import post_commit
import requests
import json
import os
from pathlib import Path
from tqdm import tqdm

def ensure_git_repo():
    try:
        subprocess.run("git rev-parse --is-inside-work-tree",
                       shell=True, check=True, stdout=subprocess.PIPE)
    except Exception:
        click.echo("Not inside a git repo.")
        raise click.Abort()


@click.group()
def cli():
    """Code Memory CLI - AI that remembers your codebase."""


@cli.command()
@click.option("--api", "api_url", default="http://localhost:8000", help="Code Memory API URL")
def init(api_url):
    """Initialize Code Memory inside this repo."""
    ensure_git_repo()

    repo_name = subprocess.check_output(
        "git rev-parse --show-toplevel", shell=True).decode().strip().split("/")[-1]

    cfg = DEFAULT_CONFIG.copy()
    cfg["api_url"] = api_url
    cfg["repo_name"] = repo_name

    save_config(cfg)
    click.echo(f"Created {CONFIG_FILE}")

    # Install post-commit hook
    hooks_dir = Path(".git/hooks")
    hook_path = hooks_dir / "post-commit"

    script = f"""#!/bin/bash
python3 - << 'EOF'
from codemem.git_hook import post_commit
post_commit("{api_url}")
EOF
"""
    hook_path.write_text(script)
    hook_path.chmod(0o755)

    click.echo("Installed post-commit hook.")
    click.echo(f"🎉 Code Memory enabled for repo: {repo_name}")


@cli.command()
def status():
    """Check configuration and API connectivity."""
    cfg = load_config()
    if not cfg:
        click.echo("Not initialized. Run `codemem init`.")
        return

    click.echo(f"Repo: {cfg['repo_name']}")
    click.echo(f"API:  {cfg['api_url']}")

    try:
        r = requests.get(cfg["api_url"] + "/health", timeout=2)
        click.echo("API status: " + ("OK" if r.ok else "ERROR"))
    except Exception:
        click.echo("API status: unreachable")


@cli.command()
@click.argument("question")
def ask(question):
    """Ask Code Memory a question about this codebase."""
    ensure_git_repo()
    cfg = load_config()
    if not cfg:
        click.echo("Not initialized. Run `codemem init`.")
        return

    req = {
        "query": question,
        "repo": cfg["repo_name"],
        "top_k": 5
    }
    res = requests.post(cfg["api_url"] + "/search", json=req).json()

    click.echo("\n📌 Answer:")
    click.echo(res["answer"].strip())
    click.echo("\n🔍 Relevant Memories:")
    for m in res["memories"]:
        click.echo(f"- {m['commit_hash'][:7]}: {m['summary']}")


@cli.command()
@click.option("--limit", default=None, help="Only backfill latest N commits")
@click.option("--concurrency", default=8, help="Number of parallel workers")
def backfill(limit, concurrency):
    """Index entire git history into Code Memory (parallel + ETA)."""
    ensure_git_repo()
    cfg = load_config()
    if not cfg:
        click.echo("Not initialized. Run `codemem init`.")
        return

    repo = cfg["repo_name"]
    api = cfg["api_url"]

    import subprocess
    import requests
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    # --- Fetch commit list ---
    cmd = "git rev-list --all"
    if limit:
        cmd += f" | head -n {limit}"

    commit_hashes = subprocess.check_output(
        cmd, shell=True
    ).decode().splitlines()

    total = len(commit_hashes)
    click.echo(f"📚 Found {total} commits in {repo}\n")

    # --- Helper: process one commit ---
    def process_commit(h):
        try:
            msg = subprocess.check_output(
                f"git log -1 --pretty=%B {h}", shell=True
            ).decode().strip()

            files_raw = subprocess.check_output(
                f"git diff-tree --no-commit-id --name-only -r {h}",
                shell=True
            ).decode()
            changed_files = files_raw.splitlines()

            # commit diff
            try:
                diff = subprocess.check_output(
                    f"git diff {h}^ {h}",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode()
            except subprocess.CalledProcessError:
                diff = subprocess.check_output(
                    f"git show {h}",
                    shell=True
                ).decode()

            # ✂️ truncate huge diffs (speeds ingest)
            MAX_DIFF = 15000
            if len(diff) > MAX_DIFF:
                diff = diff[:MAX_DIFF] + "\n[...diff truncated...]"

            payload = {
                "repo": repo,
                "commit_hash": h,
                "author": subprocess.check_output(
                    f"git log -1 --pretty=format:'%an <%ae>' {h}",
                    shell=True
                ).decode().strip(),
                "branch": "backfill",
                "commit_message": msg,
                "changed_files": changed_files,
                "diff": diff,
            }

            # 🔁 Retry-friendly POST
            for attempt in range(3):
                try:
                    requests.post(
                        f"{api}/ingest",
                        json=payload,
                        timeout=45  # higher timeout for generation
                    )
                    return (h, True)
                except Exception:
                    time.sleep(2)
            return (h, False)

        except Exception:
            return (h, False)

    # --- Execute in parallel ---
    errors = 0
    futures = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # launch all tasks first
        for h in commit_hashes:
            futures.append(executor.submit(process_commit, h))

        for f in tqdm(as_completed(futures),
                      total=total,
                      desc="Ingesting",
                      unit="commit"):
            h, ok = f.result()
            if not ok:
                errors += 1
                tqdm.write(f"⚠️ Failed on {h[:7]}")

    click.echo("\n🎉 Backfill finished!")
    if errors:
        click.echo(f"⚠️ {errors} commits failed.")
    else:
        click.echo("💪 No errors detected.")
