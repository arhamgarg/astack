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
{ lines 300; printf 'w = 1\f\nx = 2\f\n'; lines 300; } > src/app/feeds.py
printf 'notes\n' > docs/notes.txt
printf 'caf\xe9\n' > docs/latin.txt
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
printf '# syntax=docker/dockerfile:1\n# escape=`\n# check=skip=all\nFROM scratch\n# note\n# syntax=late\n' > Dockerfile
printf '# syntax=x\nkey: 1\n' > settings.yml
mkdir -p build src/main docs/ops; printf 'class B {\n// note\n}\n' > src/main/DockerfileBuilder.java; printf 'class E {\n  #count = 0;\n}\n' > src/main/DockerfileEditor.ts; printf '# Images\n' > docs/ops/Dockerfile.md
printf 'export {}\n// note\n' > src/main/Containerfile.ts
for f in Containerfile build/app.dockerfile Dockerfile.dev; do printf '# syntax=x\nFROM scratch\n# note\n' > "$f"; done
printf '// swift-tools-version:5.9\nlet x = 1\n' > Package.swift
mkdir -p web; printf '/// <reference types="node" />\nexport {}\n' > web/env.ts
printf 'a { color: red; } /* note */\n' > web/site.css
expect comments 1 'scripts/hi.sh:2: comment'
expect comments 1 'src/app/x.go:3: comment'
expect comments 1 'Dockerfile:5: comment'
expect comments 1 'Dockerfile:6: comment'
expect comments 1 'settings.yml:1: comment'
expect comments 1 'Containerfile:3: comment'
expect comments 1 'build/app.dockerfile:3: comment'
expect comments 1 'Dockerfile.dev:3: comment'
expect comments 1 'src/main/DockerfileBuilder.java:2: comment'
expect comments 1 'src/main/Containerfile.ts:2: comment'
expect comments 1 'web/site.css:1: comment'
lacks comments 'ok.py|x.go:1|hi.sh:1|Dockerfile:[1-4]:|env.ts|Package.swift|Containerfile:1|dockerfile:1|Dockerfile.dev:1|DockerfileEditor|Dockerfile.md'
git checkout -q -- src/app/__init__.py; rm -r src/app/ok.py scripts/hi.sh src/app/x.go Dockerfile settings.yml Package.swift web build Containerfile Dockerfile.dev src/main docs/ops
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

mkdir -p src/BadDir src/app/BadPkg; printf 'x = 1\n' > src/BadDir/MyMod.py; printf '# x\n' > docs/My_Notes.md; touch src/app/BadPkg/__init__.py; printf 'x = 1\n' > src/app/0002_extra.py; mkdir -p web; printf 'export {}\n' > web/_fooBar.ts
expect naming 1 'src/BadDir/MyMod.py: name folders in lowercase kebab-case or snake_case: bad-dir'
expect naming 1 'docs/My_Notes.md: name Markdown files in kebab-case'
expect naming 1 'src/app/BadPkg/__init__.py: name Python package folders in snake_case: bad_pkg'
expect naming 1 'src/app/0002_extra.py: name Python modules in snake_case'
expect naming 1 'web/_fooBar.ts: name script code in kebab-case'
rm -r src/BadDir docs/My_Notes.md src/app/BadPkg src/app/0002_extra.py web
mkdir -p formal/Proofs web/app/[slug] .github/ISSUE_TEMPLATE skills/demo docs/_static src/app/migrations
printf 'theorem t : True := trivial\n' > formal/Proofs/Basic.lean
mkdir -p 'web/app/(shop)/@modal/[...slug]' web/pages web/routes
for d in '(.)photo' '(..)photo' '(...)photo' '(..)(..)photo'; do mkdir -p "web/app/$d"; printf 'export {}\n' > "web/app/$d/page.tsx"; done
printf 'export {}\n' > web/Button.tsx; printf 'export {}\n' > web/app/[slug]/page.tsx; printf 'export {}\n' > 'web/app/(shop)/@modal/[...slug]/page.tsx'
for f in _app.tsx '[id].tsx' '[...slug].tsx' '[[...slug]].tsx'; do printf 'export {}\n' > "web/pages/$f"; done; for f in +page.ts '$id.tsx' '$postId.tsx' '$post_id.tsx' '$.tsx' __root.tsx; do printf 'export {}\n' > "web/routes/$f"; done
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
sed -i.bak '1d' src/app/feeds.py; rm src/app/feeds.py.bak
expect file_size 0 ''
git checkout -q -- src/app/feeds.py
printf 'y = 3\n' >> src/app/feeds.py
expect file_size 1 'src/app/feeds.py: 603 lines \(was 602\); files over 500 lines may not grow'
git checkout -q -- src/app/feeds.py

printf 'from __future__ import annotations\n\nimport os  # noqa: F401\n' > src/app/sup.py
expect suppressions 1 'src/app/sup.py: `noqa: F401` count 1 \(was 0\)'
A=scripts/checks/allowed-suppressions.txt
printf 'noqa: F401\n' > $A
expect suppressions 1 'allowed-suppressions.txt: `noqa: F401` gives no reason'
printf 'noqa: F401 | the import registers a codec\n' > $A
expect suppressions 0 ''
git add -A; git commit -qm 'feat: add sup'
expect suppressions 0 ''
printf '[tool.ruff]\nline-length = 120\n' > pyproject.toml
expect suppressions 1 'config pyproject.toml \[tool.ruff\] differs'
printf 'config pyproject.toml [tool.ruff] | long URLs in fixtures\n' >> $A
expect suppressions 0 ''
printf 'noqa: E999 | nothing\n' >> $A
expect suppressions 1 'allowed-suppressions.txt: `noqa: E999` names nothing'
sed -i.bak '$d' $A; rm $A.bak
git add -A; git commit -qm 'chore: widen'; git push -q origin work:main 2>/dev/null; git fetch -q origin
printf 'from __future__ import annotations\n\nimport sys  # noqa: F401\n' > src/app/sup2.py
expect suppressions 1 'src/app/sup2.py: `noqa: F401` count 1 \(was 0\)'
printf 'noqa: F401 | the import registers a codec\n' >> $A
expect suppressions 0 ''
git checkout -q -- $A
printf 'noqa:F401|the import registers a codec\n' >> $A
expect suppressions 0 ''
git checkout -q -- $A; rm src/app/sup2.py; git push -qf origin main:main 2>/dev/null; git fetch -q origin
mkdir -p web; printf '// eslint-disable-next-line no-console\nconsole.log(1)\n' > web/log.ts
expect suppressions 1 'web/log.ts: `eslint-disable: no-console` count 1'
rm -r web
printf 'token: %s # gitleaks:allow\n' "$(token)" > config.yml
expect suppressions 1 'config.yml: `gitleaks: allow` count 1'
printf 'gitleaks: allow | a published test token\n' >> $A
expect suppressions 0 ''
git checkout -q -- $A; rm config.yml
printf 'caf\xe9 au lait\n' > docs/latin.txt; printf 'caf\xe9\n' > src/app/new.txt
expect suppressions 0 ''
git checkout -q -- docs/latin.txt; rm src/app/new.txt
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

git checkout -q main; printf '# Old\n\nFirst line.\nSecond line.\nThird line.\n' > docs/Old_Name.md; git add -A; git commit -qm 'docs: old'; git push -q origin main 2>/dev/null
git checkout -qb rename; git mv docs/Old_Name.md docs/old-name.md
expect markdown 0 ''
printf 'Fourth line.\n' >> docs/old-name.md
expect markdown 1 'kept Markdown grew'
git checkout -q -- docs/old-name.md
git mv docs/notes.txt docs/notes.md
expect markdown 1 'docs/notes.md: new Markdown files are not allowed'
git mv docs/notes.md docs/notes.txt
expect naming 0 ''
git commit -qm 'docs: rename'
expect markdown 0 ''
git checkout -q work

git init -q --bare -b main "$W/sub.git"; git clone -q "$W/sub.git" "$W/sub" 2>/dev/null
(cd "$W/sub" && git config user.name kit && git config user.email kit@example.invalid && git config commit.gpgsign false && git commit -q --allow-empty -m one && git commit -q --allow-empty -m two && git push -q origin main 2>/dev/null)
git checkout -qb vendor
git -c protocol.file.allow=always submodule -q add "$W/sub.git" vendor/sub 2>/dev/null; git -C vendor/sub checkout -q HEAD~1; git add -A; git commit -qm 'chore: vendor'
git -C vendor/sub checkout -q main; git add vendor/sub
moved() { if [ "$(git diff --cached --raw vendor -- vendor/sub | cut -c1-15)" = "$1" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL submodule fixture: $(git diff --cached --raw vendor)"; fi; }
moved ':160000 160000 '
expect suppressions 0 '' --base vendor
expect file_size 0 '' --base vendor
git rm -q -f vendor/sub
moved ':160000 000000 '
expect suppressions 0 '' --base vendor
expect file_size 0 '' --base vendor
git checkout -q -f work 2>/dev/null; rm -rf vendor

git init -q --bare -b main "$W/adopt.git"; git clone -q "$W/adopt.git" "$W/adopt" 2>/dev/null
cd "$W/adopt"; git config user.name kit; git config user.email kit@example.invalid; git config commit.gpgsign false
printf '__pycache__/\n' > .gitignore; git add -A; git commit -qm init; git push -q origin main 2>/dev/null; git remote set-head origin --auto >/dev/null
git checkout -qb adopt; mkdir -p scripts/checks; cp "$KIT"/checks/*.py scripts/checks/
expect run_all 0 ''
git add -A; git commit -qm 'build: add checks'
expect run_all 0 ''
cd "$W/repo"; git checkout -q work

expect run_all 0 ''
echo "kit-e2e: $pass passed, $fail failed"
[ "$fail" = 0 ]
