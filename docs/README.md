# Documentation — Croesus report workspace

This documentation covers **the `.claude/` workflows and agents** that live in this workspace: the
seven gated playbooks (`feature`, `bug`, `refactor`, `spike`, `explore`, `investigate`, `learn`),
the agents that carry them out, and the shared protocol they all obey. It is *not* documentation of
the report pipeline's code — for that, see the per-repo `CLAUDE.md` files and the root
[`../CLAUDE.md`](../CLAUDE.md).

## How this documentation is organised (Diátaxis)

These docs follow the [Diátaxis](https://diataxis.fr/) framework. Each of the four quadrants serves a
different need — pick the one that matches what you're trying to do right now:

| Quadrant | When you are… | Nature |
|---|---|---|
| 📚 **[Tutorials](tutorials/)** | learning, new here, want to be *shown* | learning-oriented, hands-on lessons |
| 🔧 **[How-to guides](how-to/)** | getting a specific job done | task-oriented recipes |
| 📖 **[Reference](reference/)** | looking something up mid-task | information-oriented, dry facts |
| 💡 **[Explanation](explanation/)** | understanding *why* it's built this way | understanding-oriented discussion |

A quick way to choose:

- **"Show me how this works from scratch."** → [Tutorials](tutorials/)
- **"How do I fix a bug / run a feature / pass a gate?"** → [How-to guides](how-to/)
- **"What does the `planner` agent output again?"** → [Reference](reference/)
- **"Why are there gates at all? Why not one big agent?"** → [Explanation](explanation/)

## Start here by role

- **New to the workspace** → [Tutorial: your first workflow](tutorials/first-workflow.md), then
  [Explanation: the design philosophy](explanation/design-philosophy.md).
- **Experienced, here to get work done** → [How-to: choose a workflow](how-to/choose-a-workflow.md)
  and the [Reference](reference/).

## Source of truth

The authoritative specs are the files under [`../.claude/`](../.claude/) — chiefly
[`.claude/conventions/workflows.md`](../.claude/conventions/workflows.md) and
[`.claude/conventions/protocol.md`](../.claude/conventions/protocol.md). **These docs explain and
index those files; they do not replace them.** Where a Reference page and a `.claude/` file disagree,
the `.claude/` file wins — and please [fix the drift](how-to/keep-docs-in-sync.md).

> **Note on location.** This `docs/` tree lives at the workspace root, which is itself a small git
> repo (`.git/` exists here), but the symlinked product repos under `repos/` are *separate* repos.
> See [Reference: the task directory & workspace layout](reference/task-directory.md).
