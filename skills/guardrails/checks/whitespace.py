from __future__ import annotations

import re
import subprocess
from pathlib import Path

from repo import merge_base, run, worktree_index

WITH_LINE = re.compile(r"^.+:\d+: (?!new blank line at EOF\.$).+\.$")


def _diff_check(repo: Path, *args: str, env: dict[str, str] | None = None) -> list[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "diff", "--check", "--no-color", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 2):
        raise SystemExit(f"git diff --check failed: {result.stderr.strip()}")
    lines = iter(result.stdout.split("\n"))
    failures = []
    for header in lines:
        if header:
            failures.append(header)
        if WITH_LINE.match(header):
            next(lines, None)
    return failures


def check(repo: Path, base: str) -> list[str]:
    committed = _diff_check(repo, merge_base(repo, base), "HEAD")
    with worktree_index(repo) as env:
        uncommitted = _diff_check(repo, "--cached", "HEAD", env=env)
    return committed + uncommitted


if __name__ == "__main__":
    run(
        "whitespace",
        "Fail when the branch's commits or the working tree, untracked files included, add "
        "whitespace errors that git diff --check reports.",
        check,
        takes_base=True,
        after="fix the whitespace errors above (trailing whitespace, a space before a tab in "
        "the indent, blank lines at the end of a file, or a conflict marker)",
    )
