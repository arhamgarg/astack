---
name: engineering
description: Use before changing, debugging, testing, or verifying code, tests, or a repository's docs and config, including as a subagent.
---

# Engineering

## Working principles

Build complex things as simply as possible. In every problem, look for complexity to remove before adding any.

1. **Start with the goal.** On a long or multi-step task, restate the goal, the problem behind it, and your assumptions before the first tool call, and again after an interruption or a new instruction. Say so if a simpler approach exists. Before a non-trivial plan, make the strongest evidence-based case against it and push back if it holds. Weigh the cost to the user, the next developer, and the next agent.
2. **Debug from a counterexample.** State the violated property and reproduce the bug with a failing behaviour check or a model trace tied to the code. Test falsifiable hypotheses, most likely first. After a restart, suspect stale persisted state first. A fix needs an unbroken causal chain from trigger to symptom, each link cited as `path:line`. When an approach fails twice, find the root cause before trying a third. If two diagnoses leave the cause unknown, give the [reviewer model](../review/SKILL.md) a read-only diagnosis job at high effort, with no forked context: the symptom, both attempts and their evidence, and the code paths, asking for a root-cause hypothesis and the check that confirms it. You keep the fix. If that fails too, stop and report.
3. **Keep it simple.** Write the least code that solves the problem clearly. No unrequested features and no abstraction for single-use code: duplicate a few lines until the pattern is proven. Every new option has a current caller and a documented default. A recurring workaround, growing special cases, type escape hatches, or callers that must know internal rules mean the design is wrong, so rework it. Validate a value once, at the boundary that owns it, and trust its type after that. Don't write a check or fallback that costs more than the case it guards, and guard an unlikely edge case only after reporting its failure mode, likelihood, and cost as a decision.
4. **Change only what the request needs.** Every changed line traces to the request or to a standing rule. Match the existing style and leave nearby code alone. Remove only what your change orphaned. When unsure, keep it and ask. Mention dead code you find, and delete it only when asked.
5. **Fail loudly.** No fallback that hides invalid state. Fail explicitly and keep the original error and its context. Catch an exception only to recover, add context, or translate it at a system boundary. Exit codes, statuses, and return values say what actually happened.
6. **Replace, don't shadow.** Migrate every caller and remove the old path in the same change. Keep backward compatibility only for a consumer that needs it.
7. **Define done first.** Turn each task into a goal you can verify and name the check that proves it. State the invariants, preconditions, and postconditions before implementation. Name the evidence that establishes each property and its limits. For a refactor, confirm the tests pass before and after. Loop until the check passes. For a repetitive edit or analysis, write a script you can rerun, do one unit by hand first, and run the script everywhere only once it reproduces that unit exactly. When the user corrects a mistake, add a check (a type, lint, test, or script) that catches it, and its error names the supported path. Add instruction text only when no check can express the rule. Time costs something, so take the shortest path to a verified result and run independent checks in parallel.

## Standing rules

- No comments. Source files have no comments or docstrings in any language. The only `#` or `//` lines are shebangs and tool pragmas (`noqa`, `type: ignore`, `isort`, `pragma`, `fmt`). Put what a comment would say in a name, a type, a test, or the commit message, and put user-facing help in the framework's help argument. Remove every comment in a file you edit.
- No session history in the work. Code, names, tests, and docs describe the code as it is, never how it used to be: no "now uses", "previously", "used to be X", "changed from X to Y". Commit messages and PR and issue text may state what the change does and why.
- For Python, use Astral's tools only: `uv`, `ruff`, and `ty`. Report `ty` gaps rather than switching type checkers.
- Reach for the standard library and existing dependencies first. Add a maintained library only when it meets the requirements, security included, and reduces the total work once integration and maintenance count. Prefer its extension points to a fork. When API behaviour is unclear, read the official docs for the pinned version, and never upgrade to match a newer example.
- For performance, first measure where the workload spends its time and change the part that costs most. Look for an algorithmic change (a closed form, an incremental update, a lower complexity class) before tuning code. A performance claim needs before and after numbers with the run count, the spread, the limiting resource, and proof the measured work actually ran.
- Keep source files at or under 500 lines unless the project sets its own limit. Tests, docs, and config are exempt. Never leave a file over the limit or grow one that already is. Split it first, in its own commit.
- Start every task that edits a code repository in a new linked worktree from the remote's base branch (`git worktree add <path> -b <branch> <remote>/<base>`), unless the environment already made one for the task. Never edit files in the main checkout or reuse another task's worktree.

## Writing about code

These rules add to `unslop` for text about code.

- Write the real symbol, file, flag, or command, not a synonym or a description, and put it in code font.
- Code and strings have no em or en dashes either.
- A PR description or commit message is a briefing a reviewer reads in under a minute. Link logs, SHA lists, and metric tables the reader can open instead of pasting them. A local or temporary path is not a link: give the command and its result.
- A count or tree is true at the commit that adds it and comes with the command that regenerates it.
- A final response leaves out what the reader can see in the diff or a passing check, and names every failing, skipped, or pending check.

## Testing

- State the contract first, then choose evidence using the escalation ladder in `verify` when it applies. A failing example test is not required before every implementation. For a bug fix, capture a counterexample before changing behaviour and confirm the fix removes it. Build one behaviour end to end before starting the next.
- Keep behaviour tests for regressions, integration, and model-to-code agreement. Prefer property-based tests over example lists when a general rule defines the behaviour. Use them when proof costs more than it resolves, and report the property as tested, not proved. For end-to-end tests, choose a realistic (medium-to-hard) scenario that exercises the risk, never the simplest one. When testing a unit alone, list every way it can fail before writing the code.
- When a change has a UI, open it and try to break it: empty input, double submit, refresh mid-action.
- Test behaviour, not implementation: assert what a caller observes through the public interface, so a refactor that keeps behaviour keeps every test passing. Write or keep a test only when it pins behaviour no other test pins, either a realistic regression or an acceptance criterion. No tautological or change-detector tests. Add a regression test for a bug fix only when the behaviour tests have a real gap. Skip new examples that only repeat a machine-checked property when current evidence also establishes model-to-code agreement. Delete an existing test only with evidence that its protection is gone, duplicated, or ineffective. A proof of a separate model alone does not establish duplication.
- Never edit an expected output to make a test pass. Inspect the stored artifacts when you change the state they capture.
- End every end-to-end run with a repeatable artifact, the command and its output, that proves each acceptance criterion.

## Verification

The project `AGENTS.md` names the setup command, the fast gate, the full gate, the QA gate, and which changes need QA. Without a project `AGENTS.md`, take them, and any risk rules and domain checklists, from configuration and CI. If CI runs the full gate, the full gate means that CI check passing on the pushed head.

| Change | Verification |
|---|---|
| Documentation only | `git diff --check`, and every command, link, and claim checked. Add the fast gate if instructions, examples, config, CI, or executable docs changed. |
| Standard code | The narrowest relevant property check, proof, or behaviour test while editing, then the fast gate and the full gate. |
| High or Critical risk, as the [review skill](../review/SKILL.md) defines it | An end-to-end test of the risk, the fast gate, and the full gate. For Critical logic, also apply `verify` and retain one independent review. |
| Changes the project sends to QA | All of the above plus the QA gate. Open and inspect the generated artifacts. |
| External-service behaviour | Every local check. Connected checks only when the user asks. |

An interrupted, skipped, stale, or partial run is not a pass. Fix the failures your change caused and run again. Show evidence before you blame infrastructure. A remote result doesn't replace inspecting artifacts, and a local pass doesn't excuse a failing required remote check, except under the approval-evidence bootstrap in [ship](../ship/SKILL.md) step 9. Repeat or widen tests only when new changes, failures, or open questions call for it.
