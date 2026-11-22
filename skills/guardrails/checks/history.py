from __future__ import annotations

import re
from pathlib import Path

from repo import files, run

HISTORY = re.compile(
    r"\bthis (?:pr|pull request|commit|change|conversation|machine)\b"
    r"|\bmoved (?:from|out of)\b|\bsection by section\b|^\s*historical:",
    re.IGNORECASE,
)


def check(repo: Path) -> list[str]:
    return [
        f"{path}:{number}: '{match.group()}': describe the code as it is, not how it changed"
        for path in files(repo, "*.md")
        for number, line in enumerate((repo / path).read_text().splitlines(), 1)
        for match in HISTORY.finditer(line)
    ]


if __name__ == "__main__":
    run(
        "history",
        "Fail on Markdown that narrates change history instead of current behaviour.",
        check,
    )
