---
name: bug
description: Fix a defect in the Croesus report workspace, end to end, following the gated bug workflow — context → reproduce → diagnose → plan-fix → [gate] → build → verify+review → [gate] → ship? → retrospective. Pulls context from Jira and GitHub. Use when the user reports something broken/wrong (bad report output, error, crash, incorrect value, regression) or hands over a Jira bug ticket. Enforces no-fix-without-a-reproduction-and-a-regression-test. Not for new capabilities (use feature) or pure restructuring (use refactor).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **bug** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the agents in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§2 *bug*) and `.claude/conventions/protocol.md` (task dir, gate
protocol, the plan-gate **build bar**, HALT protocol, per-repo commands, and guardrails). Cite and
follow them — do not restate their rules. Dispatch each subagent with the **Agent** tool, passing its
`subagent_type` (the agent's name) and a prompt of the form:

```
Task directory: .work/<slug>/
Task: <the task text>
```

The distinguishing rule of this workflow: **no fix ships without a reproduction and a regression
test** that fails before the fix and passes after. Diagnosis is mandatory and separate from the fix —
do not patch symptoms.

## 1. Setup
- Derive the **slug** (Jira key if present, else kebab-case of the first ~4 words); confirm if guessed.
- `mkdir -p .work/<slug>/_signals/` and write the report to `.work/<slug>/task.md`.

## 2. Context  →  `context.md`
Dispatch **context-gatherer** with the Jira key and/or GitHub ref — it captures the bug report, repro
steps, and any linked PRs/commits. HALT loop per protocol.md if needed.

## 3. Reproduce  →  `bug-diagnosis.md`
Establish a reproduction before diagnosing. Dispatch **explorer** if you first need to locate the
failing path. Then reproduce: prefer writing a **failing test** that captures the defect; otherwise
document exact repro steps. Record repro status (reliable / intermittent / not-yet-reproduced) in
`bug-diagnosis.md`. If it cannot be reproduced, surface that to the user via `AskUserQuestion` (get
more detail, or proceed on best evidence) before continuing — do not blindly patch.

## 4. Diagnose  →  `bug-diagnosis.md`
Dispatch **investigator** to find the root cause (evidence → hypotheses with verdicts → root cause →
confidence). It appends to `bug-diagnosis.md`. Distinguish the trigger from the underlying cause.

## 5. Plan the fix  →  `plan.md`
Dispatch **planner** (fix-scoped, minimal — the plan must include the regression test in its Tests
section). It writes a graded, status-stamped `plan.md`. HALT/decision-point loop as in protocol.md.

## 6. Plan gate — enforce the build bar
Present `plan.md` (lead with **Status** + **Grade**). Apply the protocol.md **build bar**: approvable
only when `ready` + graded **A or S**. Below bar → surface + **changes** (re-dispatch planner) or
**cancel**; explicit user override recorded in `_signals/revision-request.md`. At/above bar → ask
*approve / changes / cancel*. Small fixes may grade quickly, but the bar still holds unless overridden.

## 7. Build the fix  →  `build-summary.md`
Dispatch **implementer** (or **cpp-to-csharp-porter** if the fix is in a C++→C# value-provider port).
The build **must** include the regression test proving the bug is fixed. The builder builds + runs
tests before returning. HALT loop as needed. `git add`-stage, no commit.

## 8. Verify + review  →  `review-code.md`
Confirm the original reproduction is gone (re-run the failing test / repro). Dispatch **reviewer** in
code mode; it writes `review-code.md`. The review must confirm the regression test actually covers
the root cause, not just the symptom.

## 9. Code gate
Ask *approve / changes / cancel*. **changes** or `must-fix` present → write findings to
`_signals/revision-request.md`, loop to §7 (**cap 3** build↔review iterations), then report remaining
issues. **approve** → continue.

## 10. Ship (optional, gated)
If the user wants to ship: **per touched repo**, branch (`--no-track` from a protected ref), commit,
`git push -u`, open a PR — per the org git rules in protocol.md. Skip if declined.

## 11. Retrospective  →  `retro.md`
Dispatch **retrospective**. Its `retro.md` **must** include the root-cause *class* (so similar bugs
are caught earlier) and propose memory/doc updates as a checklist for user approval — do not
auto-write them.

Finish with a short summary: the root cause, the fix + regression test, verify/review outcome, PRs
(if any), and the proposed learnings awaiting approval.
