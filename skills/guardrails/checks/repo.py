from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

BINARY_SNIFF = 8000
GITLINK = "160000"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.decode().strip()}")
    return result.stdout


def root() -> Path:
    return Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())


def files(repo: Path, *patterns: str) -> list[str]:
    listing = git(
        repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", *patterns
    )
    return sorted(p for p in set(listing.split("\0")) if p and (repo / p).is_file())


def read_text(path: Path) -> str | None:
    return decoded(path.read_bytes())


def decoded(data: bytes) -> str | None:
    if b"\0" in data[:BINARY_SNIFF]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def merge_base(repo: Path, base: str) -> str:
    result = subprocess.run(
        ["git", "merge-base", "HEAD", base], cwd=repo, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise SystemExit(
            f"cannot find the merge base of HEAD and {base}: {result.stderr.strip()}. "
            "Pass --base <branch the work merges into>, or run git remote set-head origin --auto"
        )
    return result.stdout.strip()


def changed(repo: Path, base_commit: str) -> dict[str, str | None]:
    found: dict[str, str | None] = {}
    fields = git(repo, "diff", "--raw", "--no-renames", "-z", base_commit).split("\0")
    for header, path in zip(fields[0::2], fields[1::2], strict=False):
        old_mode, new_mode, *_, status = header.lstrip(":").split()
        if GITLINK in (old_mode, new_mode):
            continue
        found[path] = None if status == "A" else f"{base_commit}:{path}"
    for path in filter(
        None, git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    ):
        found.setdefault(path, None)
    return found


@contextmanager
def worktree_index(repo: Path) -> Iterator[dict[str, str]]:
    index = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "index").strip())
    with tempfile.TemporaryDirectory() as scratch:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch, "index"))}
        if index.is_file():
            shutil.copyfile(index, env["GIT_INDEX_FILE"])
        subprocess.run(["git", "add", "-A"], cwd=repo, env=env, check=True, capture_output=True)
        yield env


def run(
    name: str,
    description: str,
    check: Callable[..., list[str]],
    *,
    takes_base: bool = False,
    after: str = "",
) -> None:
    parser = argparse.ArgumentParser(prog=name, description=description)
    if takes_base:
        parser.add_argument("--base", default="origin/HEAD", help="ref to take the merge base with")
    args = parser.parse_args()
    repo = root()
    failures = check(repo, args.base) if takes_base else check(repo)
    for failure in failures:
        print(f"{name}: {failure}", file=sys.stderr)
    if failures and after:
        print(f"{name}: {after}", file=sys.stderr)
    sys.exit(1 if failures else 0)
