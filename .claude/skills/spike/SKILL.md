---
name: spike
description: Run a timeboxed investigation in the Croesus report workspace to reduce uncertainty and reach a decision, following the spike workflow — frame + timebox → context → investigate (throwaway) → findings → [gate (decide)]. Use when the approach itself is genuinely unknown and the user wants to evaluate options before committing ("should we…?", "is X feasible?", "which approach?", "spike this"). Produces a recommendation, not shipped code — prototypes are throwaway. Not for building the chosen approach (use feature/refactor) or explaining existing behaviour (use investigate).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **spike** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the agents in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§4 *spike*) and `.claude/conventions/protocol.md` (task dir,
gate protocol, HALT protocol, guardrails). Cite and follow them — do not restate their rules.
Dispatch each subagent with the **Agent** tool, passing its `subagent_type` (the agent's name) and a
prompt of the form:

```
Task directory: .work/<slug>/
Task: <the task text>
```

The distinguishing rules of this workflow: **no production code** — any prototype is throwaway,
kept isolated, and must not be shipped; the work is **timeboxed**; and the deliverable is a
**decision**, not a merge. There is no build/review/ship phase and no retrospective phase — but you
still capture durable learnings to memory at the end. Re-render a one-line progress note at each
phase transition.

## 1. Frame + timebox
Before dispatching anything, pin down with the user (via `AskUserQuestion` only if unclear):
- the **precise question** the spike must answer,
- a **timebox** (how much effort is worth spending),
- what **"done"** looks like — the decision this feeds and the options on the table.
Derive the **slug** (Jira key if present, else kebab-case of the first ~4 words; confirm if guessed),
`mkdir -p .work/<slug>/_signals/`, and write the framing (question, timebox, done-definition) to
`.work/<slug>/task.md`.

## 2. Context (light)  →  `context.md`
Only if a ticket or GitHub ref exists: dispatch **context-gatherer** for a light brief. Skip if the
spike is a pure "is this feasible" question with no ticket — say so and move on.

## 3. Investigate  →  evidence (notes toward `spike.md`)
Dispatch **explorer** (to map what exists / where the seams are) and/or **investigator** (to answer
*why/whether* something holds) as the question needs. If a throwaway prototype is warranted, build it
in **isolation** — a scratch location, never edited into the real repos' source — and treat it as
disposable evidence, not a deliverable. Keep within the timebox; if it blows, stop and report what's
known so far.

## 4. Findings  →  `spike.md`
Synthesize into `spike.md`: the question, what was tried, the **options** with their trade-offs and
the cost/risk of each, and a clear **recommendation**. Be explicit about what remains uncertain and
what a follow-up feature/refactor would need to nail down.

## 5. Decision gate
Present `spike.md` (lead with the recommendation). Ask the user to **decide** via `AskUserQuestion` —
typically: pick an option (which usually feeds a `feature` or `refactor` workflow), ask for more
investigation (loop to §3, respecting a fresh timebox), or drop it. Record the decision in `spike.md`.

## 6. Capture learnings
Even without a retrospective phase, surface a short checklist of durable learnings worth saving to
memory (feasibility verdicts, dead ends to avoid, constraints discovered). **Do not** auto-write
memory — offer the checklist for the user's approval.

Finish with a short summary: the question, the recommendation, the user's decision, the follow-up
workflow it feeds (if any), and the proposed learnings awaiting approval.
