#!/bin/bash
set -u
KIT=$(cd "$(dirname "$0")" && pwd)
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
git init -q --bare -b main "$W/origin.git"
git clone -q "$W/origin.git" "$W/repo" 2>/dev/null
cd "$W/repo"
git config user.name kit; git config user.email kit@example.invalid; git config commit.gpgsign false
mkdir -p scripts/checks src/app docs
cp "$KIT"/checks/*.py scripts/checks/
printf 'from __future__ import annotations\n\n\ndef add(a: int, b: int) -> int:\n    return a + b\n' > src/app/__init__.py
printf '# Demo\n\nSee [the guide](docs/guide.md).\n' > README.md
printf '# Guide\n\nRun it.\n' > docs/guide.md
printf '[tool.ruff]\nline-length = 100\n' > pyproject.toml
git add -A; git commit -qm init; git push -q origin main 2>/dev/null
git remote set-head origin --auto >/dev/null
pass=0; fail=0
expect() {
  local name="$1" code="$2" pattern="$3" out rc
  out=$(python3 scripts/checks/$name.py 2>&1); rc=$?
  if [ "$rc" = "$code" ] && { [ -z "$pattern" ] || printf '%s' "$out" | grep -qE -- "$pattern"; }; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $name rc=$rc want=$code /$pattern/"; echo "$out" | head -5; fi
}
python3 scripts/checks/run_all.py >/dev/null 2>&1 && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL clean run_all"; python3 scripts/checks/run_all.py; }
git checkout -qb work
printf 'from __future__ import annotations\n\n\ndef add(a: int, b: int) -> int:\n    """Add."""\n    return a + b  # sum\n' > src/app/__init__.py
expect comments 1 'src/app/__init__.py:5: docstring'
expect comments 1 'src/app/__init__.py:6: comment'
printf 'x = 1  # noqa: E501\n' > src/app/ok.py
printf '#!/usr/bin/env bash\n# says hi\necho hi\n' > scripts/hi.sh
printf '//go:build linux\npackage x\n// note\n' > src/app/x.go
expect comments 1 'scripts/hi.sh:2: comment'
expect comments 1 'src/app/x.go:3: comment'
out=$(python3 scripts/checks/comments.py 2>&1); echo "$out" | grep -qE 'ok.py|x.go:1|hi.sh:1' && { fail=$((fail+1)); echo "FAIL comments flagged a pragma"; echo "$out"; } || pass=$((pass+1))
git checkout -q -- src/app/__init__.py; rm src/app/ok.py scripts/hi.sh src/app/x.go
printf '# Guide\n\nRun it \xe2\x80\x94 now.\n' > docs/guide.md
expect dashes 1 'docs/guide.md:3: replace the dash'
expect markdown 1 'kept Markdown grew'
printf '# Guide\n\nRun.\n' > docs/guide.md
expect markdown 0 ''
printf '# New\n' > docs/new-page.md
expect markdown 1 'docs/new-page.md: new Markdown files are not allowed'
rm docs/new-page.md
printf '# Demo\n\nSee [gone](docs/missing.md) and [web](https://example.com).\n\n```\n[x](nope.md)\n```\n' > README.md
expect links 1 'README.md:3: broken link docs/missing.md'
out=$(python3 scripts/checks/links.py 2>&1); echo "$out" | grep -q 'nope.md' && { fail=$((fail+1)); echo "FAIL links read a fence"; } || pass=$((pass+1))
git checkout -q -- README.md
printf '# Guide\n\nThis PR adds a guide.\n' > docs/guide.md
expect history 1 "docs/guide.md:3: 'This PR'"
git checkout -q -- docs/guide.md
mkdir -p src/BadDir; printf 'x = 1\n' > src/BadDir/MyMod.py; printf '# x\n' > docs/My_Notes.md
expect naming 1 'src/BadDir/MyMod.py: name folders in lowercase kebab-case or snake_case: bad-dir'
expect naming 1 'docs/My_Notes.md: name Markdown files in kebab-case: my-notes.md'
rm -rf src/BadDir docs/My_Notes.md
mkdir -p formal/Proofs; printf 'theorem t : True := trivial\n' > formal/Proofs/Basic.lean
mkdir -p web; printf 'export {}\n' > web/Button.tsx
expect naming 0 ''
rm -rf formal web
printf 'x = 1   \n' > src/app/trail.py
expect whitespace 1 'src/app/trail.py:1: trailing whitespace'
rm src/app/trail.py
python3 -c "print('\n'.join(f'v{i} = {i}' for i in range(501)))" > src/app/big.py
expect file_size 1 'src/app/big.py: new file has 501 lines'
mkdir -p tests; mv src/app/big.py tests/test_big.py
expect file_size 0 ''
rm -rf tests
printf 'from __future__ import annotations\n\nimport os  # noqa: F401\n' > src/app/sup.py
expect suppressions 1 'src/app/sup.py: `noqa: F401` count 1 \(was 0\)'
git add -A; git commit -qm 'feat: add sup' -m 'Allow-Suppression: noqa: F401'
expect suppressions 0 ''
printf '[tool.ruff]\nline-length = 120\n' > pyproject.toml
expect suppressions 1 'config pyproject.toml \[tool.ruff\] differs'
git add -A; git commit -qm 'chore: widen' -m 'Allow-Suppression: config pyproject.toml [tool.ruff]'
expect suppressions 0 ''
git commit -q --allow-empty -m 'chore: noop' -m 'Allow-Suppression: noqa: E999'
expect suppressions 1 'Allow-Suppression: noqa: E999: names nothing'
git reset -q --hard HEAD~1
printf 'token = "ghp_%s"\n' "$(python3 -c 'import random,string;random.seed(7);print("".join(random.choice(string.ascii_letters+string.digits) for _ in range(36)))')" > src/app/leak.py
expect secrets 1 'src/app/leak.py:1: github-pat in uncommitted changes'
git add -A; git commit -qm 'feat: leak'
expect secrets 1 'src/app/leak.py:1: github-pat in commit'
git reset -q --hard HEAD~1
expect secrets 0 ''
python3 scripts/checks/run_all.py >/dev/null 2>&1 && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL final run_all"; python3 scripts/checks/run_all.py; }
echo "kit-e2e: $pass passed, $fail failed"
[ "$fail" = 0 ]
