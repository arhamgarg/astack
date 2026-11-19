---
name: review
description: Use when asked to review, check, or look over code, a PR, a branch, a commit, or a diff for bugs or merge safety, or when acting as a reviewer subagent.
---

# Code review

## Target

Resolve the target:

- no argument: the current branch's open PR, else the branch against the base. If the branch is the base and nothing is uncommitted, report nothing to review.
- a PR number or URL: that PR's base and head
- a branch or commit: that revision against its merge base with the base
- a range: its endpoints

Resolve the base from the request, PR, project instructions, then remote default branch. Without a remote, use the configured base or ask. Fetch when a remote exists. Report unavailable remote evidence. Read with `git diff <base>...<head>`, `git show`, and `git log`.

Done when section 6 is complete or nothing to review is reported.

## Reviewer model

The reviewer model is the newest Claude Fable model when you are an Anthropic model, and the newest GPT Astra model when you are an OpenAI model. Use the harness's floating alias where it has one, otherwise the highest version it lists, and record the exact model ID in review evidence.

## 1. Stance

Check the contract and evidence first. Focus adversarial probes on unproved behaviour, assumptions, and model-to-code agreement. Critical changes retain one independent review. Additional rounds need a changed finding, changed code, or new evidence, and focus on the affected risk. Required head approvals still apply. Unless asked for fixes, review read-only without editing, switching branches, or changing external state. Run probes, mutations, and scripts on a copy in a new temporary directory, never in a checkout. Stay in the foreground until section 6 is written.

## 2. Inputs

Read the base, head, full merge-base diff, linked issue and acceptance criteria, public APIs, and available verification results. For state machines, Critical logic, or formal evidence, read the [`verify`](../verify/SKILL.md) skill. Identify missing inputs that block a conclusion. Continue without optional context when the repository answers the question.

## 3. Procedure

1. **Scope.** List every changed file, hunk, and commit. State the requested behaviour in one sentence and make each criterion a pass or fail check. Flag unrelated changes that add risk, review burden, or behaviour outside the issue, and undeclared dependencies on unmerged PRs.
2. **Risk.** Apply the highest class, refined by the project:
   - Critical: changes to external systems or money, persistent operational state, point-in-time correctness of authoritative data, locking, backup, restore, secrets, or destructive operations
   - High: core domain logic, data retrieval and caching, validation, metrics, CLI exit status, notifications, or report artifacts
   - Standard: isolated tooling, tests, or documentation that cannot reach a Critical or High boundary

   Tests and documentation carry the risk of the behaviour they specify, regardless of diff size.
3. **Behaviour.** For each change, read the whole function or type, callers, downstream consumers, configuration and factory wiring, serialization, persisted-state boundaries, and contract tests. Trace error, retry, restart, missing-data, and partial-success paths. Require a concrete, reachable failure path for concerns. Inspect pinned library source, wire and database formats, flags, and indirect consumers. Investigate unexplained differences across sibling implementations. Name the fact safety depends on and establish it with evidence. Distinguish inspection, executed tests, exhaustive bounded checks, and machine-checked proofs. For formal evidence, apply the evidence requirements in `verify`. Inspect the specification, assumptions, and code mapping instead of re-deriving the proved result.
4. **Checklists.** Apply section 4 and relevant project checklists.
5. **Verification.** Confirm every hunk was read. Any unread hunk makes the verdict `BLOCKED`.
6. **Other reviews.** Reproduce or trace bot and human claims. Dismiss incorrect claims with evidence and avoid duplicate findings.
7. **Report.** Use sections 5 and 6.

## 4. Checklists

### Correctness and scope

- Public, error, and default behaviour are explicit.
- Retries are bounded and wrap only idempotent operations.
- Repeated execution is deterministic or deliberately idempotent.
- Logging and diagnostics never change authoritative state.
- Every effect of removed or replaced code is preserved elsewhere or dropped deliberately.
- Removed complexity has not moved into callers, configuration, or tests.
- New rules, constants, parsers, and factories do not duplicate existing ones. Search before accepting.
- Decision logic uses pure functions with I/O at the edges.
- Enforceable constraints have checks.
- Added text that breaks the [`engineering`](../engineering/SKILL.md) skill no-session-history rule is a LOW finding.

### Types and configuration

- Config models and input boundaries reject invalid, unknown, misspelled, and out-of-range values.
- Parsing validates ranges and field combinations.
- Settings survive the loader, factory, runtime, and CLI unchanged.
- Every control claimed as configurable is configurable.
- Types and validation exclude illegal states. Each type-system escape hatch has a reason.

### Tests, documentation, and artifacts

- Bug fixes have a failing behaviour check or counterexample tied to the code before the fix and confirming evidence after it. Retain end-to-end checks required by project gates. A model-only counterexample needs a trace to the implementation.
- Evidence covers failure, boundary, restart, and partial-success paths in proportion to risk. Follow `verify` when deciding whether a proof replaces duplicate examples. Keep tests of integration and model-to-code agreement.
- Assertions and coverage are not weakened to hide regressions.
- Expected-output changes record behaviour changes.
- No test would pass if every call returned `None`. Reject assertions limited to type, presence, truthiness, absence, mock calls, or lack of exceptions. Also reject expected values computed by the implementation, restated constants or defaults, and self-asserting fixtures.
- Project CRAP, duplication, and mutation tools pass on changed code, except equivalent survivors justified in the PR and inherited survivors on lines whose text exists in the base. Without these tools, invert one condition covered by new tests and confirm a test fails. If formal evidence already includes a broken control for that property, reuse it and check the remaining implementation gap.
- Documentation matches actual behaviour and claims external checks or production readiness only with evidence.

## 5. Findings and severity

Report defects introduced or exposed by the change against the issue's goal. Mention pre-existing problems separately. They affect the verdict only if the change worsens or relies on them.

- BLOCKER: unintended external change, broken safety limit, materially misstated authoritative figures, corrupted or lost authoritative data, exposed secrets, unsafe recovery, or an unbuilt acceptance criterion.
- HIGH: a realistic path to wrong core behaviour, status, or recovery, with narrower impact than BLOCKER.
- MEDIUM: a bounded correctness, compatibility, observability, or maintenance defect with a concrete failure path.
- LOW: a useful nonblocking improvement. Exclude style preferences, naming taste, and speculative flexibility.

Use one finding per root cause, citing the smallest useful `path:line`, preferably changed:

```text
[SEVERITY] Short imperative title (path:line)

Trigger: <the input, state, or sequence>
Impact: <the observable wrong behaviour>
Evidence: <code path, test result, or artifact>
Required behavior: <the minimum the fix must satisfy, without prescribing a redesign>
Verification: <the check that establishes the fix and its limits, naming the uncovered behaviour when a new test is needed>
```

On re-review, check earlier findings and the diff since the reviewed head. Recheck affected proofs and code mappings when their inputs change. Reuse unchanged evidence and skip probes that only repeat established properties. Raise a new finding on already reviewed code only when it is a BLOCKER. Distinguish verification from mocks and inference.

## 6. Output and verdict

Return every section below, with findings sorted by severity, path, then line:

```text
Findings
<findings, or "No findings.">

Acceptance criteria
- PASS | FAIL | NOT VERIFIED: <criterion and evidence>

Verification
- PASS | FAIL | NOT RUN | INTERRUPTED: <command or inspection>: <result>

Residual risks
- <risks left open by the evidence, including model-to-code gaps and unproved liveness, or "None identified.">

Verdict
<APPROVE | COMMENT | REQUEST_CHANGES | BLOCKED>: <one-sentence reason>
```

Choose the verdict:

- `REQUEST_CHANGES`: a BLOCKER or HIGH finding, failed criterion, or required check failing because of the change.
- `COMMENT`: neither `REQUEST_CHANGES` nor `BLOCKED` applies, every criterion and completed check passes, and MEDIUM or LOW findings remain open or a required check is safely unavailable.
- `APPROVE`: no open finding, every criterion and required local check and artifact inspection passes, and required remote checks are green or pending, or fail only under the sibling [`ship`](../ship/SKILL.md) skill, step 9 approval-evidence bootstrap. MEDIUM or LOW findings declined with an accepted reason count as resolved.
- `BLOCKED`: missing access, requirements, or evidence, or unrelated infrastructure failure prevents a safe verdict.

If unable to submit a GitHub approval, give a recommendation and state that remote review state did not change.
