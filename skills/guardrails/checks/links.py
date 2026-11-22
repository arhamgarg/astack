from __future__ import annotations

import re
from pathlib import Path

from repo import files, run

LINK = re.compile(r"\]\(\s*(?:<([^>]*)>|([^)\s]+))")
REFERENCE = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?:<([^>]*)>|(\S+))")
FENCE = re.compile(r"^ *(```|~~~).*?^ *\1", re.MULTILINE | re.DOTALL)
EXTERNAL = re.compile(r"[a-z][a-z0-9+.-]*:|#")


def check(repo: Path) -> list[str]:
    failures = []
    for path in files(repo, "*.md"):
        content = FENCE.sub(lambda m: "\n" * m.group().count("\n"), (repo / path).read_text())
        for number, line in enumerate(content.splitlines(), 1):
            failures += [
                f"{path}:{number}: broken link {target}"
                for target in (a or b for a, b in LINK.findall(line) + REFERENCE.findall(line))
                if not EXTERNAL.match(target)
                and not ((repo / path).parent / target.split("#")[0]).exists()
            ]
    return failures


if __name__ == "__main__":
    run("links", "Fail on a relative Markdown link whose target does not exist.", check)
