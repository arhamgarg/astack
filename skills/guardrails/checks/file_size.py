from __future__ import annotations

import re
from pathlib import Path

from repo import changed, git_bytes, merge_base, run

BUDGET = 500
SOURCE = re.compile(r"\.(py|js|mjs|cjs|jsx|ts|tsx|go|rs|swift|kt|java|c|h|cc|cpp|hpp|lean)$")
TEST = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|_test\.\w+$|\.(test|spec)\.\w+$")


def _counts_toward_budget(path: str) -> bool:
    return bool(SOURCE.search(path)) and not TEST.search(path)


def check(repo: Path, base: str) -> list[str]:
    base_commit = merge_base(repo, base)
    failures = []
    for path, base_blob in sorted(changed(repo, base_commit).items()):
        if not _counts_toward_budget(path) or not (repo / path).is_file():
            continue
        lines = len((repo / path).read_bytes().splitlines())
        if lines <= BUDGET:
            continue
        if base_blob is None:
            failures.append(
                f"{path}: new file has {lines} lines; the budget is {BUDGET}. "
                "Split it along the concepts it owns before committing."
            )
            continue
        was = len(git_bytes(repo, "show", base_blob).splitlines())
        if was <= BUDGET:
            failures.append(
                f"{path}: {lines} lines (was {was}); the change takes it past the {BUDGET}-line "
                "budget. Split the file in its own commit before the behaviour change."
            )
        elif lines > was:
            failures.append(
                f"{path}: {lines} lines (was {was}); files over {BUDGET} lines may not grow. "
                "Split the file in its own commit before the behaviour change."
            )
    return failures


if __name__ == "__main__":
    run(
        "file_size",
        f"Fail when a change leaves a non-test source file over {BUDGET} lines or grows "
        "one already over it.",
        check,
        takes_base=True,
    )
