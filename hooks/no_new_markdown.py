#!/usr/bin/env python3
import json
import os
import sys
import tempfile
from pathlib import Path

ALLOWED_NAMES = {"AGENTS.md", "CLAUDE.md", "SKILL.md", "README.md"}
ALLOWED_ROOTS = [Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve()]
SUPPORTED = (
    "New Markdown files are blocked. Put the content in code instead: a name, a type, "
    "a test, a lint rule, CLI help, or the commit message or PR body. Edit an existing "
    "document if the text truly belongs there. Allowed new files: AGENTS.md, CLAUDE.md, "
    "SKILL.md, README.md, and files in temporary directories."
)


def allowed(path: Path) -> bool:
    if path.name in ALLOWED_NAMES or path.exists():
        return True
    resolved = path.resolve()
    return any(resolved == root or root in resolved.parents for root in ALLOWED_ROOTS)


def main() -> int:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Write":
        return 0
    raw = payload.get("tool_input", {}).get("file_path", "")
    if not raw.lower().endswith((".md", ".markdown", ".mdx")):
        return 0
    path = Path(os.path.expanduser(raw))
    if not path.is_absolute():
        path = Path(payload.get("cwd") or os.getcwd()) / path
    if allowed(path):
        return 0
    print(f"{path}: {SUPPORTED}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
