---
name: verify
description: Use when asked to prove an invariant, model-check behaviour, or work on formal verification, when changing state machines or Critical logic, or when reviewing formal evidence.
---

# Verify

When reviewing, assess the existing contract and evidence read-only. Run probes in a temporary copy and report gaps instead of implementing fixes.

## 1. State the contract

Choose one property whose failure matters to the requested change. State its preconditions, postconditions, and invariant in the code's terms. Identify the observable harm if it fails. Separate safety (something bad never happens) from liveness (something good eventually happens).

Read the implementation, existing specifications, project gates, and pinned tools. Map the property to the functions and transitions that must enforce it. Finish when the property, assumptions, code boundary, and acceptance check are explicit.

## 2. Choose the escalation ladder

Start at the lowest rung that answers the risk. Escalate when its limits leave the required property unresolved. These are choices of evidence, not four mandatory passes.

1. **Contract.** Use types, boundary validation, and preconditions and postconditions to make the obligation explicit. Runtime checks establish only what executes.
2. **Property-based testing.** Generate inputs or action sequences against the real implementation. Prefer independent invariants or an independent oracle over reimplementing the same calculation. Generate valid inputs directly, include meaningful boundary values, and retain shrunk counterexamples. Record the seed or replay data and run budget. A sampled pass is testing, not proof.
3. **Bounded model checking.** Enumerate reachable states and transitions within explicit bounds. Reuse the project's exhaustive model before introducing TLA+. State the initial states, transition rules, bounds, fairness assumptions, and actual atomic steps. Report explored states and completion. A depth cutoff, timeout, or sampled search does not establish an unbounded invariant.
4. **Deductive proof.** Use Lean 4, or an existing code verifier such as Dafny, when the property must hold beyond useful bounds. Prove initialization and preservation for a state invariant, or the function's postcondition under its preconditions. Preserve the intended statement and use the project's pinned toolchain and dependencies.

For state machines and Critical logic, start with a bounded model or a deductive proof of the relevant invariant. If proof is too costly, use property-based tests and explain the remaining gap. A failed proof is unresolved evidence, not permission to weaken the contract. Keep required gates and the independent Critical review.

Reuse the project's existing proof and model directories, its declared commands, and its pinned toolchain, and keep its dependency choices: add no library just to use a familiar tactic. If the project instructions name proof or model assets that are absent, report them and locate the intended checkout before claiming a proof run.

Finish when the tool, scope, expected cost, and unresolved risks are stated. Add a new verification tool only when existing tools cannot answer the property at reasonable cost.

## 3. Check the property and its connection to code

Run the selected check on the exact source under review. Record the tool version, command, exit status, and output. Include the target theorem or model configuration so a successful build cannot stand in for an unchecked property.

For Lean, inspect the theorem's assumptions and axiom dependencies as well as the build result. Reject `sorry`, `admit`, and added axioms that assume the obligation. For any verifier, keep specifications strong enough to express the requested behaviour. Check that preconditions are satisfiable and relevant transitions are reachable. A proof under impossible assumptions establishes nothing about the intended execution.

Check that the model matches code guards, event order, persistence, and atomic steps. Trace every abstraction to code and name omitted effects. For numeric properties, state whether the model uses integers, reals, or floating point. Exact arithmetic alone does not establish floating-point behaviour. Keep integration or conformance tests at the boundary between model and implementation. State explicitly when agreement rests on inspection rather than proof.

In a temporary copy, break the guarded property by changing a guard, update, or event order. Confirm the relevant check rejects the broken control, then confirm the unchanged version passes. If a model check still passes after a corresponding code defect, record that gap and verify the conformance check catches it. Reuse an existing broken control when it still covers the property and current code mapping.

If the check fails, translate the counterexample into code states and distinguish a code defect from an incorrect specification. Fix only within the task's scope. Finish when the check passes, the broken control is rejected, and code agreement is supported, or report the unresolved obligation and exact failure. Treat unfinished or unavailable checks as unverified.

## 4. Keep only evidence that adds coverage

Skip new example tests and additional adversarial rounds that only repeat an established property. A replacement needs current evidence for both the property and its connection to the implementation. A bounded result replaces only cases inside its bounds. Keep behaviour regressions, integration checks, and tests of effects outside the model. Delete an existing test only after identifying equivalent protection for every behaviour it covered.

Critical changes retain one independent review of the specification, assumptions, model-to-code agreement, and uncovered risks. The [review skill](../review/SKILL.md) defines that review. Recheck fixes and changed evidence without reopening unchanged proofs. Preserve project gates and required head approvals.

Finish with a compact evidence record in the task's existing verification report. Include each item below.

- Property and scope, including assumptions, bounds, numeric semantics, and any fairness requirements.
- Proof or model files, covered code symbols, and the revision or content hashes at which their agreement was checked.
- Exact command, tool version, result, output artifact, and broken-control result.
- Evidence for model-to-code agreement and any tests or review probes omitted as redundant.
- Uncovered behaviour, including liveness unless separately established, I/O, external services, and unmodeled concurrency or runtime effects.

When mapped code, dependencies, assumptions, or specifications change, refresh the affected checks and agreement evidence before reusing the result. A checked model establishes only its stated property, not correctness of the whole system.
