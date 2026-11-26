from __future__ import annotations

import configparser
import io
import json
import re
import tokenize
import tomllib
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from repo import changed, decoded, git_bytes, merge_base, read_text, run

PYTHON_PRAGMA = re.compile(
    r"#\s*(?:noqa(?::\s*(?P<noqa>[A-Z]+[0-9]*(?:\s*,\s*[A-Z]+[0-9]*)*))?"
    r"|(?P<checker>type|ty):\s*ignore(?:\[(?P<rules>[^\]]*)\])?"
    r"|(?P<cover>pragma: no cover)"
    r"|(?P<formatter>isort|fmt):\s*(?P<action>\w+))"
)
SCRIPT_DIRECTIVE = re.compile(
    r"(?://|/\*)\s*(?P<directive>(?P<linter>eslint|oxlint)-disable(?:-next-line|-line)?"
    r"|@ts-ignore|@ts-expect-error|@ts-nocheck|biome-ignore)(?P<rest>[^\n]*)"
)
SCRIPT_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
PYPROJECT_TABLES = ("ruff", "ty", "coverage", "importlinter")
TOML_CONFIGS = ("ruff.toml", ".ruff.toml", "ty.toml", ".gitleaks.toml")
INI_CONFIGS = (".coveragerc", ".importlinter")
JSON_CONFIGS = (".oxlintrc.json", ".eslintrc.json", "biome.json", "tsconfig.json")
TEXT_CONFIGS = (
    ".pre-commit-config.yaml",
    "eslint.config.js",
    "eslint.config.mjs",
    ".gitleaksignore",
)
SECRET_ALLOW = "gitleaks" + ":allow"
SECRET_ALLOW_KIND = "gitleaks: allow"
CONFIG_NAMES = ("pyproject.toml", *TOML_CONFIGS, *INI_CONFIGS, *JSON_CONFIGS, *TEXT_CONFIGS)
ALLOW_FILE = "scripts/checks/allowed-suppressions.txt"
SCRIPT_KINDS = ("eslint-disable", "oxlint-disable", "biome-ignore", "@ts-")
REMEDY = (
    "Fix the code the rule flags. If the rule is wrong for this file, add "
    f"the line `<kind> | <reason>` to {ALLOW_FILE}; the PR then needs an independent review."
)
SCRIPT_REMEDY = (
    "The comments check refuses script comments, so remove the directive and fix the code "
    "the rule flags. If the rule is wrong for this file, turn it off for the file in the "
    "linter config's overrides and allow the config change in "
    f"{ALLOW_FILE}."
)


def _codes(text: str) -> list[str]:
    return [code.strip() for code in text.split(",") if code.strip()]


def _python(path: str, text: str) -> Iterator[str]:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError) as exc:
        raise SystemExit(
            f"suppressions: {path}: cannot tokenize ({exc}); fix the syntax first"
        ) from exc
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        for match in PYTHON_PRAGMA.finditer(token.string):
            if match["checker"]:
                rules = _codes(match["rules"] or "")
                yield from (f"{match['checker']}: ignore[{rule}]" for rule in rules)
                if not rules:
                    yield f"{match['checker']}: ignore"
            elif match["cover"]:
                yield match["cover"]
            elif match["formatter"]:
                yield f"{match['formatter']}: {match['action']}"
            elif match["noqa"]:
                yield from (f"noqa: {code}" for code in _codes(match["noqa"]))
            else:
                yield "noqa"


def _script(text: str) -> Iterator[str]:
    for match in SCRIPT_DIRECTIVE.finditer(text):
        if not match["linter"]:
            yield match["directive"]
            continue
        kind = f"{match['linter']}-disable"
        rules = _codes(match["rest"].split("*/")[0].split("--")[0])
        yield from (f"{kind}: {rule}" for rule in rules)
        if not rules:
            yield kind


def _scan(path: str, text: str) -> Iterator[str]:
    yield from (SECRET_ALLOW_KIND for _ in range(text.count(SECRET_ALLOW)))
    if path.endswith(".py"):
        yield from _python(path, text)
    elif path.endswith(SCRIPT_SUFFIXES):
        yield from _script(text)


def _toml(path: str, text: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"suppressions: {path}: not valid TOML ({exc})") from exc


def _config_units(path: str, text: str) -> dict[str, object]:
    name = path.rsplit("/", 1)[-1]
    if name == "pyproject.toml":
        tool = _toml(path, text).get("tool", {})
        return {
            f"{path} [tool.{table}]": tool[table] for table in PYPROJECT_TABLES if table in tool
        }
    if name in TOML_CONFIGS:
        return {path: _toml(path, text)}
    if name in INI_CONFIGS:
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(text, path)
        except configparser.Error as exc:
            raise SystemExit(f"suppressions: {path}: not valid INI ({exc})") from exc
        return {path: {section: dict(parser.items(section)) for section in parser.sections()}}
    if name in JSON_CONFIGS:
        try:
            return {path: json.loads(text)}
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"suppressions: {path}: not plain JSON ({exc}); remove comments and fix it"
            ) from exc
    if name in TEXT_CONFIGS:
        return {path: text}
    return {}


def _totals(counts: Counter[tuple[str, str]]) -> Counter[str]:
    totals: Counter[str] = Counter()
    for (_, kind), count in counts.items():
        totals[kind] += count
    return totals


def _kind(text: str) -> str:
    return re.sub(r"\s*:\s*", ": ", text.strip().strip("`").strip(), count=1)


def _lines(text: str | None) -> Counter[str]:
    return Counter(line.strip() for line in (text or "").splitlines() if line.strip())


def _allowances(repo: Path, changes: dict[str, str | None]) -> tuple[set[str], list[str]]:
    if ALLOW_FILE not in changes:
        return set(), []
    blob, path = changes[ALLOW_FILE], repo / ALLOW_FILE
    old = _lines(decoded(git_bytes(repo, "show", blob)) if blob else None)
    new = _lines(read_text(path) if path.is_file() else None)
    allowed: set[str] = set()
    failures = []
    for line in sorted((new - old).keys()):
        kind, _, reason = line.partition("|")
        if reason.strip():
            allowed.add(_kind(kind))
        else:
            failures.append(f"{ALLOW_FILE}: `{line}` gives no reason; write `<kind> | <reason>`")
    return allowed, failures


def _failure(path: str, kind: str, was: int, now: int) -> str:
    remedy = SCRIPT_REMEDY if kind.startswith(SCRIPT_KINDS) else REMEDY
    return f"{path}: `{kind}` count {now} (was {was}); suppressions may not grow. {remedy}"


def _config_failure(unit: str) -> str:
    return (
        f"config {unit} differs from the merge base; tool configuration lists the exceptions "
        f"to the rules, so any change to it is a reviewed architecture change. Add the line "
        f"`config {unit} | <reason>` to {ALLOW_FILE}; the PR then needs an independent review."
    )


def check(repo: Path, base: str) -> list[str]:
    base_commit = merge_base(repo, base)
    before: Counter[tuple[str, str]] = Counter()
    after: Counter[tuple[str, str]] = Counter()
    units_before: dict[str, object] = {}
    units_after: dict[str, object] = {}
    changes = changed(repo, base_commit)
    for path, base_blob in changes.items():
        if base_blob is not None:
            old = decoded(git_bytes(repo, "show", base_blob))
            if old is not None:
                before.update((path, kind) for kind in _scan(path, old))
                units_before.update(_config_units(path, old))
        new = read_text(repo / path) if (repo / path).is_file() else None
        if new is not None:
            after.update((path, kind) for kind in _scan(path, new))
            units_after.update(_config_units(path, new))
    total_before, total_after = _totals(before), _totals(after)
    grown = {kind for kind, count in total_after.items() if count > total_before[kind]}
    changed_units = {
        f"config {unit}"
        for unit in units_before.keys() | units_after.keys()
        if units_before.get(unit) != units_after.get(unit)
    }
    allowed, failures = _allowances(repo, changes)
    failures += [
        f"{ALLOW_FILE}: `{kind}` names nothing this branch adds or changes; "
        "correct the kind or remove the line"
        for kind in sorted(allowed - grown - changed_units)
    ]
    failures += [
        _config_failure(kind.removeprefix("config ")) for kind in sorted(changed_units - allowed)
    ]
    for path, kind in sorted(after.keys()):
        was, now = before[path, kind], after[path, kind]
        if kind in grown - allowed and now > was:
            failures.append(_failure(path, kind, was, now))
    return failures


if __name__ == "__main__":
    run(
        "suppressions",
        "Fail when a change adds an inline lint, type, coverage, or formatter suppression, "
        f"or changes tool configuration, without a line in {ALLOW_FILE} that allows it.",
        check,
        takes_base=True,
    )
