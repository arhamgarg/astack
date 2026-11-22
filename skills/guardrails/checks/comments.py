from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

from repo import files, read_text, run

PRAGMA = re.compile(
    r"#\s*(noqa: [A-Z]+[0-9]+(, ?[A-Z]+[0-9]+)*"
    r"|isort: (off|on|skip_file)"
    r"|pragma: no cover"
    r"|type: ?ignore\[[\w, -]+\]"
    r"|ty: ?ignore\[[\w, -]+\]"
    r"|fmt: (on|off|skip))"
)
HASH_FILES = re.compile(r"(^|/)(Makefile|\.gitignore)$|\.(sh|bash|zsh|toml|ya?ml)$")
SLASH_FILES = re.compile(r"\.(js|mjs|cjs|jsx|ts|tsx|go|rs|swift|kt|java|c|h|cc|cpp|hpp)$")
DIRECTIVE = re.compile(r"//go:\w|/// <reference |// swift-tools-version:")
HEADER_DIRECTIVE = re.compile(r"#\s*(syntax|escape|check)=")
DOCKERFILE = re.compile(
    r"(^|/)(Dockerfile|Containerfile)(\.(?!(md|markdown|mdx|rst|txt)$)[A-Za-z0-9_-]+)?$"
    r"|\.dockerfile$"
)
BLOCK = re.compile(r"""'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|/\*.*?\*/""", re.DOTALL)
FIX = (
    "encode the constraint in a name, a type, a test, or a lint rule, "
    "and explain the reason in the commit message"
)


def _python(path: str, src: str) -> list[str]:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
        tree = ast.parse(src, path)
    except tokenize.TokenError as exc:
        return [f"{path}:{exc.args[1][0]}: cannot parse; fix the syntax first"]
    except SyntaxError as exc:
        return [f"{path}:{exc.lineno}: cannot parse; fix the syntax first"]
    failures = [
        f"{path}:{token.start[0]}: comment; {FIX}"
        for token in tokens
        if token.type == tokenize.COMMENT
        and not PRAGMA.fullmatch(token.string.strip())
        and not (token.start[0] == 1 and token.string.startswith("#!"))
    ]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        first = node.body[0] if node.body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            failures.append(
                f"{path}:{first.lineno}: docstring; move help to the help argument; {FIX}"
            )
    return failures


def _css(path: str, src: str) -> list[str]:
    return [
        f"{path}:{src.count(chr(10), 0, token.start()) + 1}: comment; {FIX}"
        for token in BLOCK.finditer(src)
        if token.group().startswith("/*")
    ]


def _lines(path: str, src: str, markers: tuple[str, ...], docker: bool) -> list[str]:
    failures = []
    header = True
    for number, line in enumerate(src.splitlines(), 1):
        stripped = line.lstrip()
        header = header and docker and bool(HEADER_DIRECTIVE.match(stripped))
        if (number == 1 and stripped.startswith("#!")) or header:
            continue
        if stripped.startswith(markers) and not DIRECTIVE.match(stripped):
            failures.append(f"{path}:{number}: comment; {FIX}")
    return failures


def check(repo: Path) -> list[str]:
    failures: list[str] = []
    for path in files(repo):
        src = read_text(repo / path)
        if src is None:
            continue
        if path.endswith(".py"):
            failures += _python(path, src)
        elif path.endswith(".css"):
            failures += _css(path, src)
        elif SLASH_FILES.search(path):
            failures += _lines(path, src, ("//", "/*"), docker=False)
        elif HASH_FILES.search(path) or DOCKERFILE.search(path):
            failures += _lines(path, src, ("#",), docker=bool(DOCKERFILE.search(path)))
    return failures


if __name__ == "__main__":
    run(
        "comments",
        "Fail on any comment or docstring. Shebangs, bare tool pragmas, and compiler or "
        "parser directives pass.",
        check,
    )
