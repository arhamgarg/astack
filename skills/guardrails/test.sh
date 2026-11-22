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
lines() { python3 -c "import sys; print('\n'.join(f'v{i} = {i}' for i in range(int(sys.argv[1]))))" "$1"; }
token() { printf 'ghp_%s' "$(python3 -c 'import random,string;random.seed(7);print("".join(random.choice(string.ascii_letters+string.digits) for _ in range(36)))')"; }
printf 'from __future__ import annotations\n\n\ndef add(a: int, b: int) -> int:\n    return a + b\n' > src/app/__init__.py
printf '# Demo\n\nSee [the guide](docs/guide.md).\n' > README.md
printf '# Guide\n\nRun it.\n' > docs/guide.md
printf '[tool.ruff]\nline-length = 100\n' > pyproject.toml
printf '__pycache__/\n' > .gitignore
lines 499 > src/app/edge.py
lines 600 > src/app/legacy.py
git add -A; git commit -qm init; git push -q origin main 2>/dev/null
git remote set-head origin --auto >/dev/null
pass=0; fail=0
expect() {
  local name="$1" code="$2" pattern="$3" out rc
  shift 3
  out=$(python3 scripts/checks/$name.py "$@" 2>&1); rc=$?
  if [ "$rc" = "$code" ] && { [ -z "$pattern" ] || printf '%s' "$out" | grep -qE -- "$pattern"; } && ! printf '%s' "$out" | grep -q Traceback; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $name $* rc=$rc want=$code /$pattern/"; echo "$out" | head -5; fi
}
lacks() {
  local name="$1" pattern="$2" out
  out=$(python3 scripts/checks/$name.py 2>&1)
  if printf '%s' "$out" | grep -qE -- "$pattern"; then fail=$((fail+1)); echo "FAIL $name reported /$pattern/"; echo "$out" | head -5; else pass=$((pass+1)); fi
}
expect run_all 0 ''
git checkout -qb work

printf 'from __future__ import annotations\n\n\ndef add(a: int, b: int) -> int:\n    """Add."""\n    return a + b  # sum\n' > src/app/__init__.py
expect comments 1 'src/app/__init__.py:5: docstring'
expect comments 1 'src/app/__init__.py:6: comment'
printf 'x = 1  # noqa: E501\n' > src/app/ok.py
printf '#!/usr/bin/env bash\n# says hi\necho hi\n' > scripts/hi.sh
printf '//go:build linux\npackage x\n// note\n' > src/app/x.go
printf '# syntax=docker/dockerfile:1\nFROM scratch\n# note\n' > Dockerfile
mkdir -p web; printf '/// <reference types="node" />\nexport {}\n' > web/env.ts
printf 'a { color: red; } /* note */\n' > web/site.css
expect comments 1 'scripts/hi.sh:2: comment'
expect comments 1 'src/app/x.go:3: comment'
expect comments 1 'Dockerfile:3: comment'
expect comments 1 'web/site.css:1: comment'
lacks comments 'ok.py|x.go:1|hi.sh:1|Dockerfile:1|env.ts'
git checkout -q -- src/app/__init__.py; rm -r src/app/ok.py scripts/hi.sh src/app/x.go Dockerfile web
printf 'int x = 1; /* caf\xe9 */\n' > src/app/legacy.c
expect comments 0 ''
expect file_size 0 ''
rm src/app/legacy.c

printf '# Guide\n\nRun it \xe2\x80\x94 now.\n' > docs/guide.md
expect dashes 1 'docs/guide.md:3: replace the dash'
expect markdown 1 'kept Markdown grew'
printf '# Guide\n\nRun.\n' > docs/guide.md
expect markdown 0 ''
printf '# New\n' > docs/new-page.md
expect markdown 1 'docs/new-page.md: new Markdown files are not allowed'
rm docs/new-page.md
git rm -q README.md; printf '# Guide\n\nRun it today.\n' > docs/guide.md
expect markdown 0 ''
git checkout -q HEAD -- README.md docs/guide.md

printf '# Demo\n\nSee [gone](docs/missing.md) and [web](https://example.com).\n\n```\n[x](nope.md)\n```\n\n[ref]: absent.md\n' > README.md
expect links 1 'README.md:3: broken link docs/missing.md'
expect links 1 'README.md:9: broken link absent.md'
lacks links 'nope.md'
mkdir -p 'docs/my file'; printf 'x\n' > 'docs/my file/a.txt'
printf '# Demo\n\nCall `handlers[name](event)`, see [root](/docs/guide.md) and [space](docs/my%%20file/a.txt).\n' > README.md
expect links 0 ''
printf '# Old\n\nCaf\xe9, see [x](gone.md).\n' > docs/guide.md
expect links 0 ''
expect history 0 ''
git checkout -q -- docs/guide.md
git checkout -q -- README.md; rm -r 'docs/my file'
printf '# Guide\n\nThis PR adds a guide.\n' > docs/guide.md
expect history 1 "docs/guide.md:3: 'This PR'"
git checkout -q -- docs/guide.md

mkdir -p src/BadDir src/app/BadPkg; printf 'x = 1\n' > src/BadDir/MyMod.py; printf '# x\n' > docs/My_Notes.md; touch src/app/BadPkg/__init__.py
expect naming 1 'src/BadDir/MyMod.py: name folders in lowercase kebab-case or snake_case: bad-dir'
expect naming 1 'docs/My_Notes.md: name Markdown files in kebab-case'
expect naming 1 'src/app/BadPkg/__init__.py: name Python package folders in snake_case: bad_pkg'
rm -r src/BadDir docs/My_Notes.md src/app/BadPkg
mkdir -p formal/Proofs web/app/[slug] .github/ISSUE_TEMPLATE skills/demo docs/_static src/app/migrations
printf 'theorem t : True := trivial\n' > formal/Proofs/Basic.lean
printf 'export {}\n' > web/Button.tsx; printf 'export {}\n' > web/app/[slug]/page.tsx
printf 'name: bug\n' > .github/ISSUE_TEMPLATE/bug.yml; printf 'x\n' > .github/pull_request_template.md
printf '# Demo\n' > skills/demo/SKILL.md; printf '# Conduct\n' > CODE_OF_CONDUCT.md
printf 'a {}\n' > docs/_static/site.css; printf 'x = 1\n' > src/app/migrations/0001_initial.py
expect naming 0 ''
rm -r formal web .github skills docs/_static src/app/migrations CODE_OF_CONDUCT.md

printf 'x = 1   \n' > src/app/trail.py
expect whitespace 1 'src/app/trail.py:1: trailing whitespace'
git add -A; git commit -qm 'feat: trail'
git -c core.whitespace=-trailing-space status >/dev/null
expect whitespace 1 'src/app/trail.py:1: trailing whitespace'
git reset -q --hard HEAD~1

lines 501 > src/app/big.py
expect file_size 1 'src/app/big.py: new file has 501 lines'
mkdir -p tests; mv src/app/big.py tests/test_big.py
expect file_size 0 ''
rm -r tests
lines 501 > src/app/edge.py
expect file_size 1 'src/app/edge.py: 501 lines \(was 499\); the change takes it past'
git checkout -q -- src/app/edge.py
lines 601 > src/app/legacy.py
expect file_size 1 'src/app/legacy.py: 601 lines \(was 600\); files over 500 lines may not grow'
lines 599 > src/app/legacy.py
expect file_size 0 ''
git checkout -q -- src/app/legacy.py

printf 'from __future__ import annotations\n\nimport os  # noqa: F401\n' > src/app/sup.py
expect suppressions 1 'src/app/sup.py: `noqa: F401` count 1 \(was 0\)'
git add -A; git commit -qm 'feat: add sup' -m 'Allow-Suppression: noqa: F401' -m 'The import registers a codec.'
expect suppressions 1 'does not read an `Allow-Suppression:` line'
git commit -q --amend -m 'feat: add sup' -m 'The import registers a codec.' -m 'Allow-Suppression: noqa: F401'
expect suppressions 0 ''
printf '[tool.ruff]\nline-length = 120\n' > pyproject.toml
expect suppressions 1 'config pyproject.toml \[tool.ruff\] differs'
git add -A; git commit -qm 'chore: widen' -m 'Allow-Suppression: config pyproject.toml [tool.ruff]'
expect suppressions 0 ''
git commit -q --allow-empty -m 'chore: noop' -m 'Allow-Suppression: noqa: E999'
expect suppressions 1 'Allow-Suppression: noqa: E999: names nothing'
git reset -q --hard HEAD~1
mkdir -p web; printf '// eslint-disable-next-line no-console\nconsole.log(1)\n' > web/log.ts
expect suppressions 1 'web/log.ts: `eslint-disable: no-console` count 1'
rm -r web
printf 'token: %s # gitleaks:allow\n' "$(token)" > config.yml
expect suppressions 1 'config.yml: `gitleaks:allow` count 1'
rm config.yml
printf 'abc:src/app/leak.py:github-pat:1\n' > .gitleaksignore
expect suppressions 1 'config .gitleaksignore differs'
rm .gitleaksignore

printf 'token = "%s"\n' "$(token)" > src/app/leak.py
expect secret_scan 1 'src/app/leak.py:1: github-pat in uncommitted changes'
printf '# Guide\n\nRun it \xe2\x80\x94 now.\n' > docs/guide.md
expect run_all 1 'run_all: failed: dashes, markdown, secret_scan'
git checkout -q -- docs/guide.md
git add -A; git commit -qm 'feat: leak'
expect secret_scan 1 'src/app/leak.py:1: github-pat in commit'
git reset -q --hard HEAD~1
expect secret_scan 0 ''

git remote set-head origin -d
expect markdown 1 'Pass --base .*git remote set-head origin --auto'
expect markdown 0 '' --base main
git remote set-head origin --auto >/dev/null

git checkout -q main; printf '# Old\n' > docs/Old_Name.md; git add -A; git commit -qm 'docs: old'; git push -q origin main 2>/dev/null
git checkout -qb rename; git mv docs/Old_Name.md docs/old-name.md
expect markdown 0 ''
expect naming 0 ''
git commit -qm 'docs: rename'
expect markdown 0 ''
git checkout -q work

expect run_all 0 ''
echo "kit-e2e: $pass passed, $fail failed"
[ "$fail" = 0 ]
