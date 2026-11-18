from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DASHES = re.compile("[–—]")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
FRONTMATTER = re.compile(
    r"\A---\nname: ([a-z0-9-]+)\ndescription: \S.*?\n(?:[a-z-]+: .*\n)*---\n", re.DOTALL
)


def problems() -> list[str]:
    found = []
    for doc in [ROOT / "AGENTS.md", *sorted(ROOT.glob("skills/*/*.md"))]:
        text = doc.read_text()
        where = doc.relative_to(ROOT)
        for number, line in enumerate(text.splitlines(), 1):
            if DASHES.search(line):
                found.append(
                    f"{where}:{number}: en or em dash; use a comma or a period"
                )
        for target in LINK.findall(text):
            if "://" not in target and not (doc.parent / target).exists():
                found.append(f"{where}: link to missing file {target}")
        if doc.name == "SKILL.md":
            match = FRONTMATTER.match(text)
            if match is None:
                found.append(f"{where}: frontmatter needs name and description first")
            elif match[1] != doc.parent.name:
                found.append(f"{where}: name {match[1]} differs from its directory")
    return found


if __name__ == "__main__":
    found = problems()
    print("\n".join(found))
    sys.exit(1 if found else 0)
