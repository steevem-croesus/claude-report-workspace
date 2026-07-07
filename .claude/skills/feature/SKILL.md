---
name: feature
description: Build a new feature (or user-facing / API change) in the Croesus report workspace, end to end, following the gated feature workflow — context → explore → plan → [gate] → build → review → [gate] → ship? → retrospective. Pulls context from Jira and GitHub. Use when the user asks to add/implement/build a feature, capability, report field, endpoint, or UI, or hands over a Jira story/ticket to implement. Not for fixing defects (use the bug workflow) or pure restructuring (use refactor).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **feature** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the agents in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§1 *feature*) and `.claude/conventions/protocol.md` (task dir,
gate protocol, the plan-gate **build bar**, HALT protocol, per-repo commands, and guardrails). Cite
and follow them — do not restate their rules. Dispatch each subagent with the **Agent** tool, passing
its `subagent_type` (the agent's name) and a prompt of the form:

```
Task directory: .work/<slug>/
Task: <the task text>
```

Re-render a short one-line progress note at each phase transition (which phase, what artifact landed).

## 1. Setup
- Derive the **slug**: the Jira key if the task text contains one (e.g. `FOG-9412`, `CFF-1234`),
  else kebab-case of the first ~4 words. Confirm the slug with the user if it was guessed.
- `mkdir -p .work/<slug>/_signals/` and write the raw task text to `.work/<slug>/task.md`.

## 2. Context  →  `context.md`
Dispatch **context-gatherer** with the Jira key and/or any GitHub ref in the task. It writes
`context.md`. If it returns a HALT block, follow the protocol.md HALT loop (surface via
`AskUserQuestion`, write `_signals/resume.context-gatherer.md`, re-dispatch; cap 3).

## 3. Explore  →  `exploration.md`
Dispatch **explorer** to map the affected code across the repos. It writes `exploration.md`.

## 3a. Clarify (only if needed)
Read `context.md` + `exploration.md`. If there is *genuine* ambiguity that would make the planner
guess wrong (unclear location with multiple candidates, an unmade behavioural choice, open-ended
scope), ask via `AskUserQuestion` and write Q→A to `clarifications.md`. Skip silently if the task is
clear. Do not ask defensive "are you sure?" questions.

> **Spike first?** If the *approach itself* is genuinely unknown (not just details), tell the user
> this warrants a spike and offer to pause here — the spike workflow isn't a skill yet, so run its
> phases by hand per workflows.md §4, then resume this feature with the decision as input.

## 4. Plan  →  `plan.md`
Dispatch **planner**. It writes a graded, status-stamped `plan.md` (requirements-coverage table,
steps, tests, risks, decision points, estimate). Run the HALT loop if it returns one. Resolve any
`needs-user` decision points it surfaces via `AskUserQuestion` before re-dispatching.

## 5. Plan gate — enforce the build bar
Present `plan.md` (lead with its **Status** + **Grade** header). Apply the **build bar** from
protocol.md: a plan is approvable **only** when `ready` **and** graded **A or S**.
- If `draft` or below A → do **not** offer *approve*. Surface the grade + blockers, then **changes**
  (write feedback to `_signals/revision-request.md`, re-dispatch planner, return to this gate) or
  **cancel**. The user may explicitly override to approve a sub-bar plan — record the override in
  `_signals/revision-request.md`.
- If `ready` + A/S → ask *approve / changes / cancel* via `AskUserQuestion`. Approval is still
  required. **cancel** → stop ("cancelled at the plan gate").

## 6. Build  →  `build-summary.md`
For each repo/slice named in the plan's `#### <repo>` sub-sections, dispatch a builder in plan/
pipeline order (C++ analysis → C#/API → Angular UI):
- **cpp-to-csharp-porter** when the step is a C++→C# value-provider port,
- **implementer** otherwise.
Each writes `build-summary.md` and builds + runs its tests before returning (outcome `ok` /
`tests-failed` / `build-failed`). Run the HALT loop on any halt. Builders `git add`-stage but do not
commit.

## 7. Review  →  `review-code.md`
Dispatch **reviewer** in code mode over the working diff. It writes `review-code.md` with
severity-tagged findings and a verdict.

## 8. Code gate
Present the verdict + `build-summary.md` outcome. Ask *approve / changes / cancel*.
- **changes** or `must-fix` present → write the findings to `_signals/revision-request.md`,
  loop back to §6 (re-build against the review). **Cap: 3 build↔review iterations**; then stop and
  report the remaining issues.
- **approve** → continue.

## 9. Ship (optional, gated)
Ask whether to ship. If yes, **per touched repo** (there is no shared root repo): create a feature
branch (`--no-track` from a protected ref), commit, `git push -u`, open a PR. Follow the org git
rules in protocol.md exactly. Skip entirely if the user declines.

## 10. Retrospective  →  `retro.md`
Dispatch **retrospective**. It writes `retro.md` and proposes durable memory entries + doc/CLAUDE.md
updates as a checklist. Surface that checklist to the user for approval — **do not** auto-write
memory or edit docs.

Finish with a short summary: what shipped/was built, the plan grade, build/review outcome, PRs (if
any), and the proposed learnings awaiting approval.
