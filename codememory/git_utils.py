import subprocess

def git(cmd: str) -> str:
    return subprocess.check_output(
        cmd, shell=True, text=True
    ).strip()

def get_commits():
    log = git('git log --reverse --format="%H|%an|%at|%s"')
    for line in log.splitlines():
        yield line.split("|", 3)

def get_diff(commit_hash: str) -> str:
    return git(f"git show {commit_hash} --format=")
