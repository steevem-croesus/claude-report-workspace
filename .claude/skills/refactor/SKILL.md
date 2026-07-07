---
name: refactor
description: Restructure code in the Croesus report workspace without changing behaviour, end to end, following the gated refactor workflow — context → explore → characterize → plan → [gate] → build (small steps) → review → [gate] → ship? → retrospective. Pulls context from Jira and GitHub. Use when the user asks to refactor, clean up, restructure, extract, rename, de-duplicate, or improve the shape of existing code while keeping what it does the same. Enforces characterization-tests-before-edit and behaviour-preservation. Not for new capabilities (use feature) or fixing defects (use bug).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **refactor** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the agents in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§3 *refactor*) and `.claude/conventions/protocol.md` (task dir,
gate protocol, the plan-gate **build bar**, HALT protocol, per-repo commands, and guardrails). Cite
and follow them — do not restate their rules. Dispatch each subagent with the **Agent** tool, passing
its `subagent_type` (the agent's name) and a prompt of the form:

```
Task directory: .work/<slug>/
Task: <the task text>
```

The distinguishing rule of this workflow: **behaviour must not change**. Characterization tests come
*before* any edit; every downstream consumer of a touched `ReportFoundations` surface must be named.
Re-render a short one-line progress note at each phase transition (which phase, what artifact landed).

## 1. Setup
- Derive the **slug** (Jira key if present, else kebab-case of the first ~4 words); confirm if guessed.
- `mkdir -p .work/<slug>/_signals/` and write the raw task text to `.work/<slug>/task.md`.

## 2. Context  →  `context.md`
Dispatch **context-gatherer** with the Jira key and/or GitHub ref — capture *why* the refactor is
wanted and any constraints (deadlines, frozen APIs, callers that must not break). HALT loop per
protocol.md if needed.

## 3. Explore  →  `exploration.md`
Dispatch **explorer** to map the **blast radius**: the code to be changed and every consumer of it
across the repos. For `ReportFoundations` this is critical — it is consumed by `ReportManagerApi` and
the Spooler; the map must list downstream call sites.

## 4. Characterize  →  safety-net tests (note in `build-summary.md`)
*Before touching anything*, dispatch **implementer** to add a **safety-net of characterization tests**
that pin the current observable behaviour of the code in scope, and to build + run them green. Note
any behaviour that cannot be pinned (external deps, non-determinism) as a gap. This net is what proves
the refactor is behaviour-preserving.

## 5. Plan  →  `plan.md`
Dispatch **planner**. The plan must be a sequence of **ordered, individually-safe, behaviour-preserving
steps**, and must explicitly call out any breaking-change surface (public API, contract, wire format).
It writes a graded, status-stamped `plan.md`. HALT/decision-point loop per protocol.md.

## 6. Plan gate — enforce the build bar
Present `plan.md` (lead with its **Status** + **Grade** header). Apply the protocol.md **build bar**:
approvable **only** when `ready` **and** graded **A or S**. Below bar → do not offer *approve*; surface
the grade + blockers, then **changes** (write feedback to `_signals/revision-request.md`, re-dispatch
planner, return here) or **cancel**. An explicit user override is recorded in `_signals/revision-request.md`.
At/above bar → ask *approve / changes / cancel* via `AskUserQuestion`. **cancel** → stop.

## 7. Build  →  `build-summary.md`
For each repo/slice named in the plan's `#### <repo>` sub-sections, dispatch **implementer** and apply
the refactor in the plan's **small steps** — the characterization + existing tests must stay green
**after every step**. If a step goes red, that step's change is not behaviour-preserving: stop and
report rather than adjusting the tests to match. Builders `git add`-stage, no commit. HALT loop as needed.

## 8. Review  →  `review-code.md`
Dispatch **reviewer** in code mode over the working diff. The review must verify **no behaviour change
and no contract drift** — especially at the consumer surfaces the explorer mapped.

## 9. Code gate
Present the verdict + `build-summary.md` outcome. Ask *approve / changes / cancel*. **changes** or
`must-fix` present → write findings to `_signals/revision-request.md`, loop to §7 (**cap 3**
build↔review iterations), then report remaining issues. **approve** → continue.

## 10. Ship (optional, gated)
If the user wants to ship: **per touched repo** (no shared root repo), branch (`--no-track` from a
protected ref), commit, `git push -u`, open a PR — per the org git rules in protocol.md. Skip if declined.

## 11. Retrospective  →  `retro.md`
Dispatch **retrospective**. It proposes durable memory entries + doc/CLAUDE.md updates as a checklist.
Surface the checklist to the user for approval — **do not** auto-write memory or edit docs.

Finish with a short summary: what was restructured, the plan grade, whether the safety net held green
throughout, review outcome, PRs (if any), and the proposed learnings awaiting approval.
