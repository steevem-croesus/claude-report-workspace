---
name: explore
description: Map where something lives or how it flows across the Croesus report repos — read-only, fast, no gates — following the explore workflow (scope → map → answer). Use when the user asks "where is X", "what calls Y", "how does the report pipeline flow through these repos", "map this subsystem", or wants to orient before a feature/refactor. Produces a repo/path:line map, changes no code. Not for "why did this happen" (use investigate) or "teach me this area" (use learn).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **explore** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the **explorer** agent in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§5 *explore*) and `.claude/conventions/protocol.md` (task dir,
canonical filenames, guardrails). Cite and follow them — do not restate their rules. Dispatch the
subagent with the **Agent** tool, passing its `subagent_type` and a prompt of the form:

```
Task directory: .work/<slug>/
Task: <the question>
```

This is a **read-only, no-gate, fast** workflow. There is no plan, no build, no ship, no
retrospective. The deliverable is a code map that answers the question. It is deliberately cheap —
don't over-scaffold it.

## 1. Scope
Restate the question in one line and name the **candidate repos** (which of CroesusServer,
ReportServer, ReportFoundations, ReportManagerApi, pf-web are likely in play). If the question is
genuinely ambiguous (multiple distinct things it could mean), ask once via `AskUserQuestion`;
otherwise proceed. For a quick one-off with no ticket you may skip the task dir — for anything
worth keeping, derive the **slug** and `mkdir -p .work/<slug>/`.

## 2. Map  →  `exploration.md` (or inline)
Dispatch **explorer** to produce a `repo/path:line` map plus the cross-repo flow. For a small, quick
question let it answer inline; for a substantive map, have it write `exploration.md`.

## 3. Answer
Summarize the finding for the user: the map, the flow, and the clickable `repo/path:line` entry
points — plus a one-line "next workflow" pointer if the exploration naturally leads into a `feature`,
`refactor`, or `investigate`.
