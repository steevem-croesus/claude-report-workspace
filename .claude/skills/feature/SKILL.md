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

## 1a. Report-migration mode — delegate to the report-migration workspace

**When to switch on.** If this feature is *migrating a report from Conseiller (C++) to Xpert* —
signals: the task says "migrate"/"migration" together with a report internal name
(e.g. `FOREIGN_PROPERTY`, `ASSETS_UNDER_MGT`, `PERF_SEC_LEVEL`), "to Xpert", or porting a report's
C++ parameters to C#/Angular — run **migration mode**. Confirm in one line that you're in migration
mode before proceeding; otherwise ignore this section and run the standard flow below.

In migration mode the domain work is driven by the specialist agents that live in the
**report-migration workspace**, *not* this workspace's generic `explorer`/`planner`/`implementer`/
`reviewer`. The feature **gates stay** — that gated orchestration is exactly what `/feature` adds.

**The migration agents (single source of truth — do NOT copy them into this workspace):**
`C:\Repos\claude-report-migration\.claude\agents\` → `report-analyst`, `backend-migrator`,
`frontend-migrator`, `migration-validator`, `migration-reviewer`. Their rules live in
`C:\Repos\claude-report-migration\.claude\conventions\` (`migration-protocol.md` +
`backend-conventions.md` + `frontend-conventions.md`).

**How to invoke one.** These agents are **not registered as subagents here**, so you cannot pass
their name as `subagent_type`. Dispatch with the **Agent** tool using `subagent_type: general-purpose`
and a prompt of this exact shape (fill in `<agent>`/`<file>`/report/task):

```
You are the <agent> for the Croesus report-migration workspace. Répondre en français.
Working root: C:\Repos\claude-report-migration — treat it as your cwd. All of that workspace's
relative paths (ReportManagerApi/, ReportFoundations/, CroesusServer/, pf-web/, docs/) resolve from
there, and they symlink the SAME monolith/pf-web checkouts this workspace uses, so edits are shared.
Read and follow your definition EXACTLY: C:\Repos\claude-report-migration\.claude\agents\<file>.md,
plus the conventions it cites in C:\Repos\claude-report-migration\.claude\conventions\.
Write your artifacts where your definition says (docs/reports/<REPORT>/…).
Report: <internal report name>.  Task: <the task text>.
```

Note: general-purpose dispatch does not inherit the migration agent's `model:` frontmatter — that's
fine; the definition still governs behaviour.

**Phase mapping (this workspace's feature phases → migration agents):**

| Feature phase | Migration mode |
|---|---|
| 2. Context | keep `context-gatherer` only if a Jira/GitHub ref exists; else skip and say so |
| 3. Explore | dispatch **`report-analyst`** → `docs/reports/<REPORT>/analysis.md` (the spec) |
| 4. Plan | the `report-analyst` spec **is** the plan — do not run this workspace's `planner` |
| 5. Plan GATE | present `analysis.md`; approve / changes (re-dispatch `report-analyst`) / cancel |
| 6. Build | dispatch **`backend-migrator`**, then **`frontend-migrator`** (backend → frontend order) |
| 7. Review | dispatch **`migration-reviewer`** (audit vs conventions) + **`migration-validator`** (Xpert JSON vs Conseiller XML, when outputs are available) |
| 8. Code GATE | as normal |
| 9. Ship | per touched repo (monolith + pf-web), org git rules as normal |
| 10. Retrospective | keep this workspace's `retrospective` |

Everything below is the **standard (non-migration)** feature flow; in migration mode, apply the
mapping above at each numbered phase.

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
