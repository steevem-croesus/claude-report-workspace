# Your first workflow

This tutorial walks you through two runs, smallest first, so you can *see* how the workflows behave
before you rely on one for real work:

1. a **read-only `/explore`** — no gates, no risk, produces a code map;
2. a **`/feature`** run — the full gated sequence, so you meet the plan gate, the build, the code
   gate, and the retrospective.

By the end you'll recognise the phase-by-phase rhythm and know where every artifact lands. Nothing
here mutates a product repo without your approval.

> This is a *lesson*, not a reference. Follow it in order. Once it clicks, the
> [How-to guides](../how-to/) are the faster path for real tasks.

---

## Part 1 — Map some code with `/explore`

`explore` is the safest workflow: read-only, no gates, fast. Perfect for a first run.

### Step 1 — Invoke it

In the Claude Code prompt, type:

```
/explore where does the report generation request enter ReportManagerApi and what does it call?
```

You can also just *ask* in plain language ("where does…?") and Claude will pick the `explore`
workflow — but typing `/explore` makes the choice explicit while you're learning.

### Step 2 — Watch the phases

The `explore` skill runs a short sequence (see
[Reference: workflows §5](../reference/workflows.md#5-explore)):

1. **Scope** — Claude restates your question in one line and names the *candidate repos* it thinks
   are in play (here: `ReportManagerApi`, maybe `ReportFoundations`).
2. **Map** — it dispatches the [`explorer`](../reference/agents.md#explorer) agent, which searches
   across the repos and returns a `repo/path:line` map plus a short prose flow.

### Step 3 — Read the result

You get a map of clickable `repo/path:line` entries and a plain-English description of the flow. That
is the entire deliverable — there is **no plan, no build, no gate**. Notice how cheap that was.

✅ **You've learned:** a read-only workflow just answers and stops. Now let's meet a gated one.

---

## Part 2 — Build something with `/feature`

`feature` is the full gated playbook. Even for a trivial change it runs the same phases, so it's the
best one to learn on. (See [Reference: workflows §1](../reference/workflows.md#1-feature).)

### Step 1 — Invoke it

```
/feature add a `reportFormat` query parameter to GET /api/v1/reports/{generationId} so callers can request PDF or XLSX
```

(You don't have to *ship* this — you'll cancel before the change is committed. The point is to see
the machinery.)

### Step 2 — Setup & Context

Claude derives a **slug** for the task (a Jira key if your text contains one like `RPT-12345`,
otherwise a kebab-case name) and creates a task directory: `.work/<slug>/`. This is where every
artifact for this task lives — see [Reference: the task directory](../reference/task-directory.md).

Then it dispatches [`context-gatherer`](../reference/agents.md#context-gatherer), which pulls any
Jira/GitHub context and writes `context.md`. With no ticket, it says so and works from local
evidence — it never invents ticket contents.

### Step 3 — Explore

Next it dispatches [`explorer`](../reference/agents.md#explorer) (the same agent from Part 1) to map
the affected code, writing `exploration.md`.

### Step 4 — Plan, and meet the **plan gate**

[`planner`](../reference/agents.md#planner) writes `plan.md` — with a requirements-coverage table,
ordered steps, tests, risks, and an estimate. Crucially, the plan carries a header like:

```
**Status:** ready · **Grade:** A
```

This is the **build bar**. Claude will *only* let you approve-to-build a plan that is `ready` **and**
graded **A** or **S**. If the plan comes back `draft` or a lower grade, the gate won't even offer
"approve" — it'll show you why (open questions, decisions only you can make) and route you to request
changes. That's by design; see
[Explanation: gates & the build bar](../explanation/gates-and-the-build-bar.md).

At the gate you'll be asked (via a multiple-choice prompt): **approve / request changes / cancel**.

- Try **request changes** once — type something like "also mention how the format maps to the S3
  content-type". Watch Claude re-dispatch the planner and return to the gate with a revised plan.
- This time, if it's `ready` + A/S, choose **approve**.

### Step 5 — Build

[`implementer`](../reference/agents.md#implementer) picks up the plan's steps, writes the code and
tests, **builds and runs the tests**, and writes `build-summary.md` with the real command output. It
stages new files with `git add` but does **not** commit.

### Step 6 — Review, and the **code gate**

[`reviewer`](../reference/agents.md#reviewer) reviews the diff and writes `review-code.md` — one
terse line per finding, severity-tagged (🔴 must-fix / 🟡 should-fix / 🟢 consider). You reach the
**code gate**: **approve / request changes / cancel**. If there are must-fix findings, requesting
changes loops back to build (capped at 3 iterations).

### Step 7 — Ship? (decline it)

Claude asks whether to ship. **Decline** — this was a practice run. Nothing gets committed or pushed.
(When you *do* ship, it branches per-repo with `--no-track`, commits, and opens a PR following the
[org git rules](../reference/gates-and-protocol.md#branch-commit--ship-rules).)

### Step 8 — Retrospective

Finally [`retrospective`](../reference/agents.md#retrospective) writes `retro.md` and *proposes* a
checklist of durable learnings and doc updates. It never writes to memory or edits docs on its own —
it hands you the checklist to approve.

### Step 9 — Look at what you produced

Open the task directory and see the trail:

```
.work/<slug>/
├── task.md
├── context.md
├── exploration.md
├── plan.md
├── build-summary.md
├── review-code.md
├── retro.md
└── _signals/
    └── revision-request.md   ← your "request changes" feedback, recorded
```

✅ **You've learned the core loop:** *context → explore → plan → [GATE] → build → review → [GATE] →
ship? → retrospective*, each phase owned by a named agent, each artifact a file, and the two gates
where **you** decide.

---

## Where to go next

- Understand *why* it's shaped this way → [Explanation: design philosophy](../explanation/design-philosophy.md)
- Get real work done → [How-to: choose a workflow](../how-to/choose-a-workflow.md)
- Look up an agent's exact job → [Reference: agents](../reference/agents.md)
