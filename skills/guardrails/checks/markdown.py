from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath

from repo import files, git, git_bytes, merge_base, run, worktree_index

SUFFIXES = (".md", ".markdown", ".mdx", ".rst")
INSTRUCTIONS = "AGENTS.md"
SUPPORTED = (
    "put the content in code instead: a name, a type, a test, a lint rule, CLI help, "
    "or the commit message or PR body"
)


def _markdown(paths: set[str]) -> set[str]:
    return {
        path
        for path in paths
        if path.lower().endswith(SUFFIXES) and PurePosixPath(path).name != INSTRUCTIONS
    }


def _renamed_from(repo: Path, base_commit: str) -> dict[str, str]:
    with worktree_index(repo) as env:
        listing = subprocess.run(
            ["git", "diff", "--cached", "--name-status", "-M", "-z", base_commit],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    fields = iter(listing.split("\0"))
    renames = {}
    for status in fields:
        if status.startswith(("R", "C")):
            old, new = next(fields), next(fields)
            if status.startswith("R"):
                renames[new] = old
        elif status:
            next(fields)
    return renames


def check(repo: Path, base: str) -> list[str]:
    base_commit = merge_base(repo, base)
    listing = git(repo, "ls-tree", "-r", "-z", "--name-only", base_commit)
    before = _markdown(set(filter(None, listing.split("\0"))))
    after = _markdown(set(files(repo)))
    renamed_from = {
        new: old for new, old in _renamed_from(repo, base_commit).items() if old in before
    }
    failures = [
        f"{path}: new Markdown files are not allowed; {SUPPORTED}."
        for path in sorted(after - before - renamed_from.keys())
    ]
    was = {path: len(git_bytes(repo, "show", f"{base_commit}:{path}")) for path in before}
    now = {
        renamed_from.get(path, path): len((repo / path).read_bytes())
        for path in after
        if renamed_from.get(path, path) in before
    }
    total_before = sum(was.values())
    if sum(now.values()) > total_before:
        grown = ", ".join(
            f"{path} (+{now[path] - was[path]})" for path in sorted(now) if now[path] > was[path]
        )
        failures.append(
            f"kept Markdown grew from {total_before} to {sum(now.values())} bytes in {grown}; "
            f"it may only shrink. Remove at least {sum(now.values()) - total_before} bytes, "
            f"or {SUPPORTED}. {INSTRUCTIONS} files are outside the limit."
        )
    return failures


if __name__ == "__main__":
    run(
        "markdown",
        "Fail when a change adds a Markdown file or grows the Markdown it keeps. A renamed "
        "file counts as kept.",
        check,
        takes_base=True,
    )
