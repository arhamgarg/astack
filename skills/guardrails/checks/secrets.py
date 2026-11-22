from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from repo import git, merge_base, run, worktree_index

FLAGS = (
    "--redact",
    "--no-banner",
    "--no-color",
    "--log-level",
    "info",
    "--report-format",
    "json",
    "--report-path",
    "-",
)
LOG = re.compile(r"^\S+ (?P<level>INF|WRN) (?P<message>.*)$")
SCANNED = re.compile(r"^(\d+) commits scanned\.$")
NO_RENAMES = {
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "diff.renames",
    "GIT_CONFIG_VALUE_0": "false",
}
MINIMUM_VERSION = "8.30.1"
INCOMPLETE = (
    "gitleaks did not finish the scan, so the branch is unverified; repair what its output "
    "names (for a corrupt object, run git fsck and restore the object) and rerun"
)


def gitleaks_binary() -> str:
    found = shutil.which("gitleaks")
    if found is None:
        raise SystemExit(
            f"secrets: gitleaks is not on PATH; install gitleaks {MINIMUM_VERSION} or later"
        )
    reported = subprocess.run([found, "version"], check=True, capture_output=True, text=True).stdout
    version = tuple(int(part) for part in re.findall(r"\d+", reported)[:3])
    if version < tuple(int(part) for part in MINIMUM_VERSION.split(".")):
        raise SystemExit(
            f"secrets: gitleaks {reported.strip()} is older than {MINIMUM_VERSION}; upgrade it"
        )
    return found


def _scan(repo: Path, *args: str, env: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    result = subprocess.run(
        [gitleaks_binary(), "git", *FLAGS, *args, "."],
        cwd=repo,
        env={**(env or os.environ), **NO_RENAMES},
        capture_output=True,
        text=True,
        check=False,
    )
    messages = []
    errors = []
    for line in result.stderr.splitlines():
        match = LOG.match(line)
        if match and (match["level"] == "INF" or match["message"].startswith("leaks found")):
            messages.append(match["message"])
        elif line.strip():
            errors.append(line)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = None
    if errors or not isinstance(report, list) or result.returncode != (1 if report else 0):
        raise SystemExit(
            "\n".join(
                [
                    *(f"secrets: {error}" for error in errors),
                    f"secrets: gitleaks exited with status {result.returncode}",
                    f"secrets: {INCOMPLETE}",
                ]
            )
        )
    findings = [
        f"{finding['File']}:{finding['StartLine']}: {finding['RuleID']} in "
        + (f"commit {finding['Commit']}" if finding["Commit"] else "uncommitted changes")
        for finding in report
    ]
    return findings, messages


def _commits_with_text_changes(repo: Path, span: str) -> int:
    log = git(
        repo,
        "log",
        "--diff-merges=first-parent",
        "--no-renames",
        "--diff-filter=d",
        "--format=%x00",
        "--numstat",
        span,
    )
    return sum(
        any(
            added != "-" and int(added) + int(deleted) > 0
            for added, deleted, _ in (line.split("\t", 2) for line in commit.splitlines() if line)
        )
        for commit in log.split("\0")[1:]
    )


def check(repo: Path, base: str) -> list[str]:
    span = f"{merge_base(repo, base)}..HEAD"
    committed, messages = _scan(repo, f"--log-opts=--diff-merges=first-parent {span}")
    scanned = [int(match[1]) for message in messages if (match := SCANNED.match(message))]
    expected = _commits_with_text_changes(repo, span)
    if len(scanned) != 1 or scanned[0] < expected:
        raise SystemExit(
            f"secrets: gitleaks reported {scanned or 'no count of'} commits scanned in "
            f"{span}, but {expected} commits there change text; {INCOMPLETE}"
        )
    with worktree_index(repo) as env:
        uncommitted, _ = _scan(repo, "--pre-commit", "--staged", env=env)
    return committed + uncommitted


if __name__ == "__main__":
    run(
        "secrets",
        "Fail when gitleaks, with the repository's .gitleaks.toml when it has one, finds a "
        "secret in the branch's commits or in the working tree, untracked files included.",
        check,
        takes_base=True,
        after="remove the secret from every commit on the branch and rotate it with its "
        "issuer, because a committed secret counts as exposed",
    )
