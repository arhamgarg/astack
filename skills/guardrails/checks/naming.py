from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from repo import files, run

KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PYTHON = re.compile(r"[a-z_][a-z0-9_]*")
PASCAL = re.compile(r"[A-Z][A-Za-z0-9]*")
FOLDER = re.compile(r"\.?[a-z0-9]+(?:[-_][a-z0-9]+)*|__[a-z0-9]+__")
SCRIPT_CODE = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css")
COMPONENTS = (".tsx", ".jsx")
UPPERCASE_DOCUMENTS = {
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "README.md",
    "SECURITY.md",
}


def words(stem: str) -> list[str]:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    return [word.lower() for word in re.split(r"[-_\s.]+", spaced) if word]


def kebab(stem: str) -> str:
    return "-".join(words(stem))


def pascal(stem: str) -> str:
    return "".join(word.title() for word in words(stem))


def python_name(stem: str) -> str:
    name = "_".join(words(stem))
    return name if PYTHON.fullmatch(name) else f"m_{name}"


def _folder_problem(parts: tuple[str, ...], packages: set[str], lean: set[str]) -> str | None:
    for depth, folder in enumerate(parts[:-1]):
        prefix = "/".join(parts[: depth + 1])
        if prefix in packages:
            if not PYTHON.fullmatch(folder):
                return f"name Python package folders in snake_case: {python_name(folder)}"
        elif prefix in lean and PASCAL.fullmatch(folder):
            continue
        elif not FOLDER.fullmatch(folder):
            return f"name folders in lowercase kebab-case or snake_case: {kebab(folder)}"
    return None


def _file_problem(name: str) -> str | None:
    stem, dot, rest = name.partition(".")
    suffix = f"{dot}{rest}"
    if name.endswith(".py"):
        if not PYTHON.fullmatch(stem):
            return f"name Python modules in snake_case: {python_name(stem)}{suffix}"
    elif name.endswith(".lean"):
        if not PASCAL.fullmatch(stem):
            return f"name Lean modules in PascalCase: {pascal(stem)}.lean"
    elif name.endswith(".md"):
        if name not in UPPERCASE_DOCUMENTS and not KEBAB.fullmatch(stem):
            return f"name Markdown files in kebab-case: {kebab(stem)}{suffix}"
    elif name.endswith(SCRIPT_CODE) and stem:
        component = name.endswith(COMPONENTS) and PASCAL.fullmatch(stem)
        if not KEBAB.fullmatch(stem) and not component:
            return (
                f"name script code in kebab-case, or a .tsx or .jsx component in PascalCase: "
                f"{kebab(stem)}{suffix}"
            )
    return None


def _ancestors(path: str) -> set[str]:
    parts = PurePosixPath(path).parts
    return {"/".join(parts[:depth]) for depth in range(1, len(parts))}


def check(repo: Path) -> list[str]:
    paths = files(repo)
    packages = {str(PurePosixPath(p).parent) for p in paths if p.endswith("/__init__.py")}
    lean = set().union(*(_ancestors(p) for p in paths if p.endswith(".lean")))
    failures = []
    for path in paths:
        parts = PurePosixPath(path).parts
        message = _folder_problem(parts, packages, lean) or _file_problem(parts[-1])
        if message:
            failures.append(f"{path}: {message}")
    return failures


if __name__ == "__main__":
    run(
        "naming",
        "Fail when a file or folder name breaks its language's case: snake_case Python, "
        "PascalCase Lean, kebab-case Markdown and script code (a .tsx or .jsx component may "
        "be PascalCase), snake_case Python package folders, and lowercase other folders.",
        check,
    )
