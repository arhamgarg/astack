# astack

The agent instructions and skills I use every day. They work in both Claude Code and Codex.

## Skills

| Skill | Say | What it does |
|---|---|---|
| [`ship`](skills/ship/SKILL.md) | "ship the next issue" | Takes a GitHub issue to a merged PR: branch, fix, checks, independent review, merge, and cleanup. |
| [`review`](skills/review/SKILL.md) | "review this PR" | Reviews a PR, branch, commit, or diff for bugs and merge safety, ranked by risk. |
| [`audit`](skills/audit/SKILL.md) | "audit this" | Finds tech debt and architecture problems with `path:line` evidence, and files issues when asked. |
| [`verify`](skills/verify/SKILL.md) | "prove this invariant" | Checks a property with contracts, property tests, model checking, or a Lean proof. |
| [`design`](skills/design/SKILL.md) | "design a page" | Ranks the user, the host and the project's design system above its reference, builds small changes itself or hands a new page to a builder, and checks the result against hard rules for contrast, keyboard use and motion. |
| [`engineering`](skills/engineering/SKILL.md) | (automatic) | Working rules for code: the simplest fix, no comments, behaviour tests, and the checks each change needs. |
| [`unslop`](skills/unslop/SKILL.md) | (automatic) | Rules for plain prose: no AI vocabulary, no dashes, and one idea per sentence. |
| [`instructions`](skills/instructions/SKILL.md) | (automatic) | Rules for writing and pruning `AGENTS.md` and `SKILL.md` files. |

[`AGENTS.md`](AGENTS.md) holds the rules for every session: communication, safety, and when to load `unslop`, `engineering`, `instructions`, and `design`.

Some skills call others. Install the ones they need too:

- `ship` uses `review`, `audit`, and `engineering`.
- `audit` uses `review`.
- `review` uses `verify`.
- `engineering` uses `review`, `verify`, `ship`, and `unslop`.

## Install

```bash
git clone https://github.com/arhamgarg/astack
cp -R astack/skills/* ~/.claude/skills/
cp astack/AGENTS.md ~/.claude/CLAUDE.md
cp -R astack/skills/* ~/.codex/skills/
cp astack/AGENTS.md ~/.codex/AGENTS.md
```

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`) for `ship`, and for `audit` when it files issues.
- Subagents for `design`, and for the reviewer that `ship` starts.
- `uv`, `ruff`, and `ty` for Python work under `engineering`.
- Lean 4 or Dafny for proofs in `verify`, when a property needs one.

## Make them yours

These are starting points. Edit them. Put personal settings in your project's `AGENTS.md`, which overrides the global one, so you can update the skills without losing them.

Run `python3 check.py` before committing. [`check.py`](check.py) flags dashes, broken relative links, and `SKILL.md` frontmatter whose name differs from its directory.

## License

[AGPL-3.0](LICENSE)
