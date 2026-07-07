# The orchestrator & agent model

This page explains *why* the work is split across a skill that orchestrates and many narrow agents,
instead of one capable assistant doing everything. For what each agent actually is, see
[Reference: agents](../reference/agents.md).

## The two layers

- **The orchestrator** is the workflow skill (`/feature`, `/bug`, …). It owns the *sequence*: which
  phase runs next, when to stop at a gate, when to loop, how to derive the slug. It talks to *you*.
- **The agents** are specialists dispatched by the orchestrator via the Agent tool. Each owns one
  *phase* and one artifact. They talk to the *code and the ticket*, not to you — their output is a
  file plus a short summary the orchestrator relays.

The division is deliberate: control flow (deterministic, gated, human-facing) is kept separate from
the work itself (specialised, tool-heavy). The orchestrator never writes the plan; the planner never
decides whether to ship.

## Why narrow agents instead of one generalist?

Three reasons, all about quality:

1. **A focused role produces focused output.** The [`reviewer`](../reference/agents.md#reviewer) is
   told to be adversarial and terse — no praise, no summaries, no scope creep. That posture produces
   better reviews than a generalist who also wrote the code and is inclined to defend it. Likewise the
   [`investigator`](../reference/agents.md#investigator) is told to *try to refute* its own leading
   hypothesis before accepting it. These stances only make sense as dedicated roles.

2. **Separation prevents self-marking.** The planner grades its own plan, but the reviewer
   independently verifies that grade, and the gate depends on the verified result. If the same agent
   planned, built, reviewed, *and* graded, there'd be no independent check anywhere. Splitting the
   roles creates the adversarial checks the [build bar](gates-and-the-build-bar.md) relies on.

3. **Least privilege.** Most agents are strictly **read-only** — they physically can't edit code
   (their tool list omits Edit/Write-to-code). Only the [`implementer`](../reference/agents.md#implementer)
   and [`cpp-to-csharp-porter`](../reference/agents.md#cpp-to-csharp-porter) can change source. That's
   why a `explore`/`investigate`/`learn` run is safe to fire off without a second thought.

## Read-only vs editing — the split

| | Agents | Why |
|---|---|---|
| **Read-only** | context-gatherer, explorer, investigator, learning-guide, reviewer, retrospective | understanding and judging the work; must not be able to change it |
| **Editing** | planner (writes only `plan.md`), implementer, cpp-to-csharp-porter | producing the plan and the code |

Note the planner is a middle case: it *writes*, but only the plan artifact — never production code.
Design happens before, and separately from, implementation.

## Why the fixed prompt shape and the task directory?

Every agent is dispatched with the same tiny contract:

```
Task directory: .work/<slug>/
Task: <the task text>
```

The agent reads the artifacts already in that directory (its predecessors' output) and writes its own.
This is what lets phases compose without the orchestrator having to thread state through prompts: the
`planner` reads `context.md` + `exploration.md`; the `reviewer` reads `plan.md`; the `retrospective`
reads everything. The [task directory](../reference/task-directory.md) *is* the shared memory between
agents.

## Why HALT instead of guessing?

A producing agent that hits a genuine fork — ambiguous requirement, a decision only the user should
make — doesn't guess. It returns a **HALT** block (reason, question, proposed default, state), and the
orchestrator surfaces the question to you, records the answer, and re-dispatches. Guessing past a real
fork is exactly the failure mode the whole system is built to avoid; HALT is the agent-level version of
a gate. It's capped (3 round-trips per agent) for the same reason the build↔review loop is capped:
bounded automation that escalates rather than thrashes.

## How this connects to code-fleet

Because the layers are cleanly separated, the *build + review* phases of `feature`/`refactor` can be
swapped out for the org's `code-fleet` plugin (`/code-fleet:work` and its language-pack agents)
without disturbing the orchestration or the read-only roles. The workspace agents remain the ones that
know the multi-repo report topology and the C++→C# port recipe. See
[Reference: workflows → code-fleet](../reference/workflows.md#relationship-to-code-fleet).
