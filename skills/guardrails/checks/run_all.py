from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TREE = ("comments", "dashes", "links", "history", "naming")
BRANCH = ("markdown", "whitespace", "file_size", "suppressions", "secrets")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run every check in this folder and fail if any fails."
    )
    parser.add_argument("--base", default="origin/HEAD", help="ref to take the merge base with")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    failed = []
    for name in (*TREE, *BRANCH):
        extra = ("--base", args.base) if name in BRANCH else ()
        result = subprocess.run([sys.executable, str(here / f"{name}.py"), *extra], check=False)
        if result.returncode != 0:
            failed.append(name)
    if failed:
        print(f"run_all: failed: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
