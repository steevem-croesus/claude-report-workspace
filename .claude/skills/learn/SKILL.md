---
name: learn
description: Build a mental model of an area of the Croesus report workspace — read-only, teaching — following the learn workflow (pick target + level → guided walkthrough → glossary → exercises). Use when the user wants to understand or be onboarded onto a subsystem or concept ("help me understand X", "walk me through the Spooler batch flow", "teach me the C++→C# port mechanism", "explain pf-web's DDD layering"). Produces a walkthrough with a glossary and safe exercises, changes no code. Not for locating code (use explore) or diagnosing why something happened (use investigate).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **learn** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the **learning-guide** agent in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§7 *learn*) and `.claude/conventions/protocol.md` (task dir,
canonical filenames, guardrails). Cite and follow them — do not restate their rules. Dispatch the
subagent with the **Agent** tool, passing its `subagent_type` and a prompt of the form:

```
Task directory: .work/<slug>/
Task: teach <the subsystem/concept> at <the learner's level>
```

This is a **read-only, no-gate, teaching** workflow. There is no plan, no build, no ship, no
retrospective — the deliverable is a walkthrough that leaves the user with a working mental model. It
teaches; it does **not** change code.

## 1. Target + level
Pin down two things — the **subsystem/concept** to teach (e.g. value-provider params, the Spooler
batch flow, pf-web DDD layering, the C++→C# port mechanism, the report generation pipeline end to
end) and the **learner's current level** (new to the codebase / knows one repo / experienced elsewhere).
If either is unclear, ask once via `AskUserQuestion`. Derive the **slug** (kebab-case of the target;
a Jira key only if the learning is tied to one) and `mkdir -p .work/<slug>/`.

## 2. Teach  →  `learning-notes.md`
Dispatch **learning-guide** to produce the walkthrough, pitched to the stated level: **big picture →
happy-path trace** through the real `repo/path:line` entry points → **key abstractions** → a
**glossary** of the domain terms → a few **safe, hands-on exercises** (read-only or sandboxed — never
anything that mutates the real repos). It writes `learning-notes.md`.

## 3. Wrap up
Surface the walkthrough's shape (the trace path, the key files, the exercises) and invite follow-up
questions or a deeper pass on any one part. Point at the natural next workflow if the user now wants
to *do* something — `explore` to map further, `feature`/`refactor` to build, `investigate` to dig into
a behaviour.
