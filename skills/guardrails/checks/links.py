from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from repo import files, read_text, run

LINK = re.compile(r"\]\(\s*(?:<([^>]*)>|([^)\s]+))")
REFERENCE = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?:<([^>]*)>|(\S+))")
FENCE = re.compile(r"^ *(```|~~~).*?^ *\1", re.MULTILINE | re.DOTALL)
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1")
EXTERNAL = re.compile(r"[a-z][a-z0-9+.-]*:|#")


def _exists(repo: Path, path: str, target: str) -> bool:
    relative = unquote(target.split("#")[0])
    if relative.startswith("/"):
        return (repo / relative.lstrip("/")).exists()
    return ((repo / path).parent / relative).exists()


def check(repo: Path) -> list[str]:
    failures = []
    for path in files(repo, "*.md"):
        content = read_text(repo / path)
        if content is None:
            continue
        content = FENCE.sub(lambda m: "\n" * m.group().count("\n"), content)
        for number, line in enumerate(content.splitlines(), 1):
            outside_code = CODE_SPAN.sub("", line)
            failures += [
                f"{path}:{number}: broken link {target}"
                for target in (
                    a or b for a, b in LINK.findall(outside_code) + REFERENCE.findall(outside_code)
                )
                if not EXTERNAL.match(target) and not _exists(repo, path, target)
            ]
    return failures


if __name__ == "__main__":
    run("links", "Fail on a relative Markdown link whose target does not exist.", check)
