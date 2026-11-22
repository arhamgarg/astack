---
name: instructions
description: Use before any edit to AGENTS.md or SKILL.md.
---

# Writing for agents

## Pointers

A pointer is a line in context that names material outside it and says which cases call for it. Its wording, not the material behind it, decides whether the agent gets there. When a must-have target sits behind a weak pointer, sharpen the wording first and inline the material only if that fails.

A pointer costs context on every turn, so prune it harder than the body: put the trigger word first, keep one trigger per distinct case, and cut anything the body already says.

## Two costs

- Context: always-loaded material spends tokens and attention every turn, whether it fires or not.
- Memory: the person has to remember which documents exist and when to use them. Spend that where human judgement matters and remove it where it doesn't.

Material behind a pointer costs only the pointer's line. Material with no pointer rides entirely on the person's memory.

## Where each piece goes

Content is either steps, which the agent does in order, or reference, which it consults when needed. Each piece sits on one rung:

1. a step in the file
2. reference in the file
3. reference in a separate file behind a pointer, loaded only when the pointer fires

Inline what every path needs and move out what only some paths reach. Reference that buries the steps makes the agent skip some of them. Keep a concept's definition, rules, and caveats under one heading.

## Done conditions

End every step on a condition that tells the agent it is finished, checkable and exhaustive where possible. A vague condition lets the steps that follow pull the agent on early, so sharpen it first. Hide the later steps by splitting the sequence only when the condition can't be made sharper, you have seen the agent rush, and the split puts the later steps outside the agent's context.

## When to split

A split spends one of the two costs, so split only when it pays:

- by sequence, under the conditions in § Done conditions
- by invocation, when a trigger word you actually use should fire the new skill on its own, or another skill needs to reach it
- by path, when a document is too long with every line live, so each path carries only what it needs

## Leading words

A leading word is a single word that names an idea the agent already thinks with from pretraining. Repeat it as that one word, never a sentence, and it anchors behaviour cheaply. In a body it shapes execution. In a pointer it shapes invocation, most when the same word appears in prompts, docs, and code. A coined word brings no priors, so use an existing one. Look for restatements a leading word could replace.

A prohibition puts the forbidden behaviour into context and makes it more likely. State the behaviour you want instead. Keep a prohibition only as a hard guardrail you can't phrase positively, and pair it with the positive target.

## Pruning

- Say each thing in one place. Duplication costs tokens and maintenance and inflates a rule beyond its rank.
- Scripts, configuration, directory layout, and tool help are sources of truth. A document that restates it is a cache, worth it only when the lookup is expensive. Write down only what the agent can't find by looking.
- Delete lines that never bear on the task or have gone stale.
- Delete a no-op whole, not trimmed. A line the model already obeys by default costs load and changes nothing. A leading word too weak to beat the default is also a no-op, and the fix is a stronger word.

## Testing a change

- Write conditions, not cases.
- Before adding a rule, run the task five or more times in fresh sessions without it. If no run fails, the rule is a no-op.
- When retuning a document, set the pass bar first, change one thing per round, and run the prompt at least twice before and twice after.
- After editing a skill, check that every path and command it names exists. After editing its description, run three prompts that should fire it and two that shouldn't in fresh non-interactive sessions (`claude -p` or `codex exec`).

## Skill mechanics

- A skill the agent invokes keeps a `description`, a permanently loaded pointer that follows the pointer rules above and states only the triggers: the requests, files, or situations that should fire the skill, never what the skill does. Its body is also where reference that several skills share can live.
