---
name: guardrails
description: Use when starting or adopting a code repository, or when asked to add mechanical checks, banned APIs, or import layer contracts to one.
---

# Guardrails

Each rule a check enforces stops costing review time. The [`checks`](checks) folder holds stdlib-only Python 3.11 scripts. Each prints one line per finding, starting with the check's name and the path, and exits 1 when it finds any. `--help` on any of them states its rule. After editing a check, run [`test.sh`](test.sh), which seeds each finding in a scratch repository.

1. **Copy the checks.** Copy `checks/*.py` into the repository's `scripts/checks/`. The copy belongs to the repository, so later edits happen there. `secret_scan.py` needs gitleaks 8.30.1 or later and reads `.gitleaks.toml` when the repository has one. The branch checks diff against `origin/HEAD`, so pass `--base <branch>` in a repository without it. Done when `python3 scripts/checks/run_all.py` runs every check.
2. **Clear the existing findings.** The tree checks (`comments`, `dashes`, `links`, `history`, `naming`) read the whole tree, so an adopted repository starts with findings. When one check reports more than about 20, report the count and ask whether to fix them or drop that check. Fix the rest in commits apart from the checks. Done when `run_all.py` exits 0.
3. **Ban APIs (Python).** Select `TID251` in ruff and add one `[tool.ruff.lint.flake8-tidy-imports.banned-api]` entry per API the project has a better path for. Each `msg` names that path, so the error is the fix. Start with these two, which return naive datetimes, and add a ban each time review corrects the same call twice:
   ```toml
   "datetime.datetime.utcnow".msg = "returns a naive datetime; use datetime.now(UTC)"
   "datetime.datetime.utcfromtimestamp".msg = "returns a naive datetime; use datetime.fromtimestamp(value, UTC)"
   ```
   Done when `uv run ruff check` passes.
4. **Layer the imports (Python, two or more subpackages).** Add `import-linter` as a dev dependency and write two contracts under `[tool.importlinter]`. The first is a `layers` contract over the root package with `exhaustive = true`, top layer first. The second is a `forbidden` contract from the root to `"<root>.**"`, with `as_packages = false` and `allow_indirect_imports = true`, which keeps the root `__init__.py` from importing its subpackages. Give each a `broken_contract_guidance` that says where the code should move. Order the layers by running `uv run lint-imports` and moving packages until it passes. List an upward import that a cycle forces in `ignore_imports`, one line per import, and report it. Done when `uv run lint-imports` passes.
5. **Wire the gate.** Run `run_all.py` in the fast gate and in CI. CI installs gitleaks, checks out with `fetch-depth: 0`, and passes `--base origin/<target branch>`. Name both commands in the project's `AGENTS.md`. Done when CI runs the checks on a pushed branch.
6. **Commit.** `suppressions` treats any tool config change as a reviewed exception. The commit that adds the ruff bans and contracts therefore ends with one trailer per changed table, for example `Allow-Suppression: config pyproject.toml [tool.ruff]`. Done when `run_all.py`, `ruff check`, and `lint-imports` all pass on the committed branch.
