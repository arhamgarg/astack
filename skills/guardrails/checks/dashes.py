from __future__ import annotations

from pathlib import Path

from repo import files, run, text

DASHES = (chr(0x2013), chr(0x2014))


def check(repo: Path) -> list[str]:
    failures = []
    for path in files(repo):
        content = text(repo / path)
        if content is None:
            continue
        failures += [
            f"{path}:{number}: replace the dash with a comma, a period, a colon, or 'to'"
            for number, line in enumerate(content.splitlines(), 1)
            if any(dash in line for dash in DASHES)
        ]
    return failures


if __name__ == "__main__":
    run("dashes", "Fail on any em dash or en dash in a text file.", check)
