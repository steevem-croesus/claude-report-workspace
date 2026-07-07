# How to get a plan past the gate

The plan gate has a hard entry condition called the **build bar**: a workflow may build **only** from
a `plan.md` that is **`ready`** *and* graded **A** or **S**. This guide is what to do when your plan
comes back below that bar.

For *why* the bar exists, see
[Explanation: gates & the build bar](../explanation/gates-and-the-build-bar.md).

## Read the header first

Every `plan.md` opens with:

```
**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
```

Grade scale (low → high): **F < D < C < B < A < S**.

- **`ready` + A or S** → the gate offers the normal **approve / request changes / cancel**. Approval
  is still required; a qualifying grade *unlocks* the gate, it doesn't auto-pass it.
- **`draft`, or graded below A** → the gate does **not** offer approve. It surfaces the grade and the
  blockers (open questions, `needs-user` decision points) and routes you to changes or cancel.

## If the plan is below bar

You have three moves:

1. **Request changes (usual).** Claude writes your feedback to
   `.work/<slug>/_signals/revision-request.md`, re-dispatches the `planner`, and returns to the gate
   with a revised plan. Repeat until it reaches `ready` + A/S.

2. **Resolve the decision points it's waiting on.** A plan often stays `draft` because of a
   `needs-user` **Decision point** — a fork only you should pick. Answer it (Claude will prompt), and
   the planner can then reach `ready`.

3. **Override (deliberately).** For a change you've judged genuinely trivial, you may explicitly
   approve a sub-bar plan. The override is recorded in `revision-request.md` so it's auditable. Absent
   an explicit override, the bar holds.

## Why a plan is often `draft` at first

- an unresolved `needs-user` decision point (a real fork with material trade-offs);
- a blocking open question;
- a step underspecified enough that the implementer would have to guess;
- for parallel-flow features, the plan hasn't yet weighed shared-base extraction / interface
  reshaping (it's expected to consider that as a decision point, not default to a minimal inline diff).

These aren't the planner being difficult — an honest `draft` is considered *better* than an inflated
`ready`. The [`reviewer`](../reference/agents.md#reviewer), in plan mode, will call out an over-graded
or wrongly-`ready` plan as a must-fix.

## Don't

- **Don't ask the planner to "just mark it ready."** It's instructed never to inflate the grade to
  clear the gate. Fix the underlying gap instead.

## Reference

- Build-bar spec: [`.claude/conventions/protocol.md` → Plan gate](../../.claude/conventions/protocol.md)
- Grading rubric: [`.claude/agents/planner.md` → Grading & status](../../.claude/agents/planner.md)
