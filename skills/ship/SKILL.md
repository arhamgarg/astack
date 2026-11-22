---
name: ship
description: Use when asked to fix, ship, or merge the next open GitHub issue, a named issue, or all open issues, or to finish an open loop PR.
---

# Issue-to-merge loop

Resolve `<base>` and `<remote>` from, in order, the request, an existing PR, the project instructions, and the remote's default branch. Resolve the absolute path of the sibling [`review`](../review/SKILL.md) skill for the reviewer.

## Invocation

The arguments set the scope:

- no argument or a request for the next issue: use the step 2 ranking
- a count `N` or a request for all issues: repeat until that many issues are merged or none is eligible
- `#N`, an issue URL, or a title: select that issue
- a PR number, URL, or reference to the current PR: resume that open loop PR

The request authorizes cleanup, branches, pushes, opening and editing the PR, independent review, PR comments, filing issues for valid findings outside the issue, merging, issue closure, and deletion of task branches and worktrees. Delete only what the loop created. Never discard, overwrite, reformat, or commit unrelated user changes. Run issues sequentially, with at most one loop PR open. Pause only for the stop conditions below.

Done when every issue in scope is merged and closed, cleanup is verified, and the report is sent, or a stop condition is reported.

## 1. Clean up and gather state

The loop owns branches matching step 3 and worktrees under its path. Delete them only when no uncommitted work or commits unreachable from `<base>` or an open PR would be lost. Keep the current worktree and each open loop PR's branch and worktree. Report anything unsafe to delete.

Fetch with `--prune`, fast-forward `<base>` in the main checkout, and confirm `gh auth status`. Gather open issues with labels and dependencies, open PRs, and worktree status. Resume an open loop PR before selecting an issue.

## 2. Pick the issue

Unless the request names one, rank open issues by, in order:

1. smallest implementation and verification surface
2. lowest operational and financial risk
3. clearest acceptance criteria, with goal, boundary, constraints, and acceptance stated or derivable from the repository
4. highest value
5. lowest number

An issue is eligible when it has no unresolved dependency or conflicting open PR, is not the audit skill's `audit: ledger` issue, and was not filed by this run for a review finding. The ledger issue stays open. Take the first eligible issue. Fetch and rerank before each issue.

## 3. Branch and worktree

Name the branch `<type>/<subject>`. The type is `fix`, `feat`, `docs`, `test`, `refactor`, or `chore`. The subject is specific lowercase kebab case without an issue number or filler. Use `<parent of main checkout>/.worktrees/<repo>/<type>-<subject>` from `<remote>/<base>`, unless the environment created the task worktree. Confirm that worktree with `git rev-parse --absolute-git-dir` differing from `--git-common-dir`. Run every edit, commit, and gate there.

Use one branch and PR per issue, never stacked.

Before editing, map each acceptance criterion to a test, command, or inspection. For a bug, reproduce it end to end first unless that is impossible locally.

When the issue names a defect class, fix the whole class. Run its class search, or write one as the sibling audit skill's § File issues defines it. Every true instance in the issue's `## Scope` is in scope. When the criteria name a guard, it must fail on each unfixed true instance.

When the project sets a PR size limit and the fix would exceed it, split the issue before editing. File each vertical slice as an issue in the audit format, with `Blocked by #N` naming the slice before it. Close the original issue with a comment listing the slices. The slices replace it in this run's scope, and the first slice continues the loop here.

## 4. Implement and commit

Search for and reuse existing rules, constants, parsers, and factories before writing them. Commit prerequisite refactors separately first.

An issue requiring an irreversible change needs two PRs, each through the full loop. Merge the reversible work first, then the irreversible work.

Keep a mechanical move free of behaviour changes.

Commit each independently explainable change. Stage by path (`git commit -- <paths>`), never `-a` or `git add -A`. Keep review fixes as separate commits until merge. Use Conventional Commits (`<type>[scope][!]: <description>`) for commit subjects and PR titles. Fix a deliberately failing test commit in the same session. Report skipped hooks.

## 5. Verify

Run the required gates, then `git diff --check`. Rerun the class search. Under `## Verification`, record its command and zero remaining true instances in scope, and name each other hit with the reason it is not one. Apply the review skill's CRAP, duplication, and mutation checklist item to changed code, recording equivalent survivors with reasons and inherited survivors as counts under `## Verification`. Read the final diff and commit list against the merge base.

If `<remote>/<base>` moved, rebase and rerun the gates before pushing. After each rebase, run `git range-diff <old-base>..<old-head> <new-base>..<new-head>`. Confirm every commit survived with only conflict resolution changed.

## 6. Push and open the PR

After local gates pass, push and open a ready PR against `<base>` with these sections in order:

1. `Closes #N`
2. `## Summary`: what changed and why
3. `## Acceptance criteria`: each criterion with before and after evidence
4. `## Key files`: where a reviewer should start
5. `## Risks and limitations`: blast radius and reversibility
6. `## Verification`: exact commands and results
7. `## External checks`: checks not performed
8. `## Independent review`: a placeholder until step 9

If the environment supports thread links to PRs, link it now.

## 7. Independent review

Standard-risk documentation-only changes skip review unless a repository check requires the step 9 block. Set `## Independent review` to `- Not required: Standard risk, documentation only` and continue at step 9.

Start one read-only reviewer on the review skill's reviewer model when the PR opens. Run required checks concurrently, including a local gate that posts a status. Use fresh context and high effort where supported. Give the reviewer:

- the PR URL, repository path, and base and head revisions
- the issue and acceptance criteria
- absolute paths to instruction files and the review skill, to read before the diff and follow, including its output format
- completed and pending verification
- instructions to judge code and evidence and read required head statuses without waiting.

Record approval over a pending check only after it passes on the same head. Handle failures under step 9 and re-review the fixed head.

Keep the PR worktree's files and branch unchanged while the reviewer works.

## 8. Triage and re-review

Trace each finding before acting. Before implementing a capability identified as missing, search for callers. Decline unused capabilities as unrequested scope. File each valid finding beyond the issue's goal as a new issue in the sibling [`audit`](../audit/SKILL.md) skill's format, after checking the tracker for a duplicate, and list its number under `## Risks and limitations`.

- Fix valid BLOCKER or HIGH findings, failed criteria, and failures caused by the change.
- Fix valid MEDIUM or LOW findings when in scope and improving correctness or necessary maintainability. Otherwise record why not.
- Dismiss invalid or duplicate findings with code, test, or artifact evidence.

Rerun affected gates, push, and handle checks as in step 7. Start a new round with the original brief, earlier findings and dispositions, open objections, new head, and new results. Use the same reviewer model until it returns `APPROVE` on the current head or a stop condition applies.

## 9. Record the review and wait for green

After `APPROVE` and after any pending check passes, confirm the head matches the reviewed head. Post the reviewer's section 6 report from the final round as a PR comment, with `## Independent review report` as its first line followed by the same four lines below, then the report. In the comment, cite evidence by command and result, use repository-relative paths, and leave out machine-local paths and personal identifiers. Then replace `## Independent review` with exactly:

```text
## Independent review
- Model: `<reviewer model id>`
- Reasoning effort: `<effort, or unsupported>`
- Reviewed head: `<full 40-character SHA>`
- Verdict: `APPROVE`
```

Any later push invalidates this evidence and returns to step 7.

Approval-evidence bootstrap: if a repository check requires this block on the current head, approval may precede that check passing. Its only failure must be the missing block, and every other required check must pass. The check must pass once the block is recorded.

Wait for every required check, including when `<base>` has no branch protection:

- description policy failure: fix the description and wait
- test failure caused by the change: fix, push, return to step 7
- proven unrelated failure: rerun once, then stop if it fails again
- `<base>` moved and the PR is behind or conflicts: rebase, rerun gates, push with `--force-with-lease`, return to step 7

## 10. Merge

Fetch. If the head lacks `<remote>/<base>`, follow step 9 for a base move. Require current-head approval evidence, or the step 7 not-required line, and all required checks passing. Merge with `gh pr merge <number> <method> --delete-branch`, using a repository-approved method. Confirm the PR is `MERGED` and the issue `CLOSED`. If `Closes #N` failed to close it, close it with a comment naming the PR.

## 11. Clean up

In order:

1. Fetch with `--prune` and delete any remote branch the loop created.
2. Fast-forward `<base>` in the main checkout.
3. Remove the task worktree when it has no uncommitted or unpushed work. If running inside it, detach onto `<remote>/<base>` for the next turn's step 1 to remove.
4. Delete the local task branch.
5. Remove other loop-created worktrees after the same check, and prune worktree metadata.
6. Use `git branch -a` and `git worktree list` to confirm only the current worktree and step 1 exceptions remain. Confirm no loop PR is open.

## 12. Report and continue

Report each issue and PR, reviewer model, verdict, finding dispositions, merge commit, and cleanup.

For remaining issues, return to step 2. After every third merge, inspect combined changes for duplicated logic, changed assumptions, obsolete issues, and new coupling. Include fixes in the next issue only if they belong to it. Otherwise report them.

## Stop conditions

Stop and report without further changes when:

- no remote exists or the base is ambiguous
- the selected issue's prerequisite PR is still open
- delegation is unavailable when review starts
- cleanup cannot establish whether a branch or worktree holds unrecoverable work
- no eligible issue remains
- the issue retains two materially different readings after investigation
- a user change overlaps the required edit and cannot be preserved
- the reviewer returns `BLOCKED` for evidence outside authorized scope
- review reaches 4 rounds without `APPROVE`, or open BLOCKER and HIGH findings remain above zero without decreasing between two rounds
- a required check fails for an unrelated reason twice
- escalated diagnosis finds no root cause
- `gh` authentication or merge fails twice

Report the issue, PR, branch, worktree, head, last completed step, and stop evidence so the next run can resume.
