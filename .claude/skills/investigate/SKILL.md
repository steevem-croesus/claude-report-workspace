---
name: investigate
description: Find out why or how something happened in the Croesus report workspace — read-only, evidence-driven — following the investigate workflow (frame → context → analyze → conclude). Pulls context from Jira and GitHub. Use when the user asks "why did X happen", "how did this reach production", "why is Y behaving this way", or wants a root-cause understanding without a fix. Rules out alternatives with code, git history, and logs. Not for fixing a known defect (use bug, which runs this as its diagnosis) or locating code (use explore).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Drive the **investigate** workflow for this task:

**$ARGUMENTS**

This skill orchestrates the agents in `.claude/agents/`. The authoritative specs are
`.claude/conventions/workflows.md` (§6 *investigate*) and `.claude/conventions/protocol.md` (task dir,
canonical filenames, HALT protocol, guardrails). Cite and follow them — do not restate their rules.
Dispatch each subagent with the **Agent** tool, passing its `subagent_type` (the agent's name) and a
prompt of the form:

```
Task directory: .work/<slug>/
Task: <the question / incident>
```

This is a **read-only, no-gate** workflow. There is no plan, no build, no ship, no retrospective — the
deliverable is a root-cause conclusion with its supporting evidence. It is **deeper than `explore`**:
it answers *why/how*, ruling out alternatives rather than just mapping where code lives. When the cause
is unknown at the start of a bug, this is the front half of the `bug` workflow.

## 1. Frame
State the **precise question or incident** in one line — what behaviour/outcome needs explaining, and
(if known) when it started. Derive the **slug** (Jira key if present, else kebab-case of the first ~4
words; confirm if guessed) and `mkdir -p .work/<slug>/_signals/`; write the framing to
`.work/<slug>/task.md`. If the question is too vague to investigate, sharpen it once via
`AskUserQuestion`.

## 2. Context  →  `context.md`
Dispatch **context-gatherer** with the Jira key and/or GitHub ref — it pulls the ticket, related PRs,
commits, and history that bear on the incident. HALT loop per protocol.md if needed. Skip only if
there is genuinely no ticket/GitHub context and say so.

## 3. Analyze  →  `investigation.md`
Dispatch **investigator** to work the evidence: gather from code, git history, Jira, GitHub, and logs;
form **hypotheses**; verify or refute each with a verdict; and conclude with the **most-supported root
cause** and a **confidence** level. It writes `investigation.md`. If it returns a HALT (needs a
decision or missing access), run the protocol.md HALT loop.

## 4. Conclude
Present the conclusion: the root cause, the key evidence that pins it, the alternatives ruled out, and
the confidence. If the natural next step is a fix, point the user at the `bug` workflow (which will
reuse this diagnosis) or `feature`/`refactor` as appropriate — but **do not** start fixing here.
