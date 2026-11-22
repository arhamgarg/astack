from __future__ import annotations

from pathlib import Path, PurePosixPath

from repo import files, git, git_bytes, merge_base, run

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


def check(repo: Path, base: str) -> list[str]:
    base_commit = merge_base(repo, base)
    listing = git(repo, "ls-tree", "-r", "-z", "--name-only", base_commit)
    before = _markdown(set(filter(None, listing.split("\0"))))
    after = _markdown(set(files(repo)))
    failures = [
        f"{path}: new Markdown files are not allowed; {SUPPORTED}."
        for path in sorted(after - before)
    ]
    was = {path: len(git_bytes(repo, "show", f"{base_commit}:{path}")) for path in before}
    now = {path: len((repo / path).read_bytes()) for path in after & before}
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
        "Fail when a change adds a Markdown file or grows the Markdown it keeps.",
        check,
        takes_base=True,
    )
