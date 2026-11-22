---
name: audit
description: Use when asked to audit code, find tech debt, or review architecture, or to file issues from those findings.
---

# Codebase audit

Change only the issue tracker, and only when asked. Never edit code or write tracking files.

## Scope

- no argument: every first-party source and test path the ledger does not cover, report only
- `full`: every first-party source and test directory, ignoring the ledger
- a path or package: that scope
- a request to file issues: audit and file verified finding classes

Audit first-party code only, in every scope.

Done when every verified class is reported or filed, every review escape is named, and the ledger entry is written. Report severity counts, issue numbers, dismissed candidates with reasons, read and unread scope, and verified findings per thousand lines read.

## Prepare

Read linter, formatter, and type-checker configuration and ignores, dependencies, recent history, uncommitted changes, and existing tracker issues. Without tracker access, report unchecked deduplication and do not file.

Read the ledger: the open tracker issue titled `audit: ledger`, with one entry per comment in the § Record the ledger entry format. A path is covered when an entry read it in full, it has no uncommitted changes, and `git diff --quiet <entry SHA> HEAD -- <path>` succeeds. An entry whose SHA is unknown covers nothing. Without tracker access, or with more than one open ledger issue, treat every path as uncovered and report why.

## Look for

Start with hot spots by churn × size from `git log --numstat`. Prioritize:

- Boundaries: persistence, external services, or CLI status outside their layer, diagnostics changing authoritative state, secrets crossing boundaries, and decision logic mixed with I/O.
- Security: input-built destructive paths or shell commands, dependency install scripts, and secrets in code, logs, or artifacts.
- Change preventers: concepts requiring scattered edits, modules changing for unrelated reasons, migration duplicates, and distant files changing together.
- Reader load: multi-hop data origins or mutations, pass-through wrappers, and modules adding only indirection.
- Documentation: verify every documented path, command, and config key against code.
- Hidden failures, bloat, and weak tests: apply user instructions and the sibling [`review`](../review/SKILL.md) skill test checklist.

## Verify findings

Require current `path:line` evidence and a concrete behavioural, safety, or measurable maintenance consequence. Exclude tracker duplicates and deliberate choices recorded in configuration, `AGENTS.md`, or history.

Verify every delegated finding yourself.

Group each class across files into one finding listing every instance. For classes with open or closed issues, report only recurrences merged after that issue. Name the `review` checklist item that should have caught each recurrence as a review escape.

Severity follows `review`, section 5.

## File issues

File one issue per class. Apply severity labels when available. Under Problem, give the class search: a command (`grep`, `ast-grep`, or a script) that lists every instance, with its hit count at the verified commit and any hits that are not instances. Criteria must name a lint, test, or type that prevents recurrence and fails on every true instance.

Split a large class into vertical slices. Each slice's Scope names the instances it owns, and only the last slice's criteria name the guard.

Check validation, failure modes, idempotency and retry, authorization, concurrency and ordering, data lifecycle, external-dependency failure, state transitions, and observability. Classify each as a criterion, existing behaviour, not applicable, or an open question under Problem.

Use this format:

```text
## Problem
<what is wrong, with path:line citations and the concrete consequence>
<class search command and its hit count>

## Acceptance criteria
- <observable outcome the fix must achieve>
- <end-to-end test or inspection that proves it>

## Scope
<files involved, what is out of scope, and "Blocked by #N" for each issue that must merge first>
```

Use a Conventional Commits subject without the type for the title.

## Record the ledger entry

When filing, add a comment to the ledger issue. If it is missing, create it and pin it with `gh issue pin`. Use this format:

```text
SHA: <full commit SHA>
Scope: <argument, or "uncovered paths">
Lines read: <count of lines in fully read text files>
Verified findings: <count> (<count per thousand lines read>)
Issues: <numbers filed or extended>
Paths read in full:
<one path per line, or a directory when every file in it was read in full>
```

List only paths without uncommitted changes. When an entry exceeds one comment, continue it in further comments that each start with the SHA line.

In a report-only audit, put the same entry in the report instead.
