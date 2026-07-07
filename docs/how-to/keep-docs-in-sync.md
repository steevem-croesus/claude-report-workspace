# How to keep these docs in sync

These `docs/` explain and index the files under [`.claude/`](../../.claude/). The `.claude/` files are
the **source of truth**; the docs must follow them, not the other way round. When you change a
workflow, agent, or the protocol, update the docs in the same change.

## The mapping

| If you edit… | Update this doc |
|---|---|
| `.claude/conventions/workflows.md` | [reference/workflows.md](../reference/workflows.md) (and any affected how-to) |
| `.claude/conventions/protocol.md` | [reference/gates-and-protocol.md](../reference/gates-and-protocol.md), [reference/task-directory.md](../reference/task-directory.md) |
| any `.claude/agents/*.md` | [reference/agents.md](../reference/agents.md) |
| any `.claude/skills/*/SKILL.md` | [reference/skills.md](../reference/skills.md) |
| the plan grading rubric in `planner.md` | [how-to/pass-the-plan-gate.md](pass-the-plan-gate.md), [explanation/gates-and-the-build-bar.md](../explanation/gates-and-the-build-bar.md) |

## Rules of thumb

- **Reference pages describe; they don't duplicate.** Keep them thin and always link back to the
  authoritative `.claude/` file. The less you copy verbatim, the less can drift.
- **Explanation pages age slowly** — they're about *why*, which changes rarely. Revisit them only when
  the design philosophy itself changes (e.g. a new gate, a dropped workflow).
- **Tutorials must stay runnable.** If you rename a slash command or change a gate's wording, re-walk
  [the tutorial](../tutorials/first-workflow.md) to confirm the steps still match reality.

## Quick check for drift

The seven workflows and nine agents are enumerable. If a doc lists a workflow/agent that no longer
exists in `.claude/`, or misses a new one, that's drift. A fast audit:

```bash
ls .claude/skills/*/SKILL.md          # the seven live workflow skills
ls .claude/agents/*.md                # the nine agents
```

Compare against [reference/skills.md](../reference/skills.md) and
[reference/agents.md](../reference/agents.md).
