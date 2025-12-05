import subprocess
import requests
import json
import os


def run_git(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def post_commit(api_url: str):
    repo_name = os.path.basename(run_git("git rev-parse --show-toplevel"))
    commit_hash = run_git("git rev-parse HEAD")
    author = run_git("git log -1 --pretty=format:'%an <%ae>'")
    branch = run_git("git rev-parse --abbrev-ref HEAD")
    commit_message = run_git("git log -1 --pretty=%B")
    changed_files_raw = run_git(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
    changed_files = changed_files_raw.splitlines()
    diff = run_git(f"git show {commit_hash}")

    payload = {
        "repo": repo_name,
        "commit_hash": commit_hash,
        "author": author,
        "branch": branch,
        "diff": diff,
        "commit_message": commit_message,
        "changed_files": changed_files,
    }

    try:
        requests.post(f"{api_url}/ingest", json=payload, timeout=2)
    except Exception:
        pass  # never break commit
