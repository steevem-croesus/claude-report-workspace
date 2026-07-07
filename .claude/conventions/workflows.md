# Workflows

Seven workflows, each a distinct phase sequence tuned to the *kind* of work. All share the
foundation in `protocol.md` (task dir, context gathering, gates, HALT, per-repo rules). Gates are
**interactive** — the orchestrator stops and waits for approval. `→` is a phase; **[GATE]** is a
stop-for-approval point; agents are named in `code font`.

Each `/<workflow>` command drives the sequence below. **All seven are live skills** under
`.claude/skills/` — model-invocable, or run with `/feature`, `/bug`, `/refactor`, `/spike`,
`/explore`, `/investigate`, `/learn`. Each skill orchestrates the agents in `../agents/` via the
Agent tool and defers to this file (its `§N`) and `protocol.md` for the authoritative rules.

---

## 1. `feature` — build something new

> **spike?* → context → explore → plan → [GATE] → build → review → [GATE] → ship? → retrospective**

| Phase | Agent | Output |
|---|---|---|
| 0. Spike (optional) | run the `spike` workflow first *only if* the approach is genuinely unknown | `spike.md` |
| 1. Context | `context-gatherer` | `context.md` |
| 2. Explore | `explorer` | `exploration.md` |
| 3. Plan | `planner` | `plan.md` (with requirements-coverage table) |
| **Plan GATE** | — | build bar: plan must be `ready` + grade **A/S** to be approvable (see protocol.md); else approve / changes / cancel |
| 4. Build | `implementer` (or `cpp-to-csharp-porter` for value-provider ports; one per repo/slice) | code + tests, `build-summary.md` |
| 5. Review | `reviewer` (code mode) | `review-code.md` |
| **Code GATE** | — | approve / changes (loop to build, cap 3) / cancel |
| 6. Ship (optional, gated) | orchestrator | branch + commit + PR **per repo** (org git rules) |
| 7. Retrospective | `retrospective` | `retro.md` + proposed learnings |

Notes: cross-repo features run phase 4 in pipeline order (C++ analysis → C#/API → Angular UI), each
repo on its own branch/PR. The plan's `#### <repo>` sub-sections tell each `implementer` its slice.

---

## 2. `bug` — fix a defect

> **context → reproduce → diagnose → plan-fix → [GATE] → build → verify+review → [GATE] → ship? → retrospective**

| Phase | Agent | Output |
|---|---|---|
| 1. Context | `context-gatherer` | `context.md` (bug report, repro steps, linked PRs) |
| 2. Reproduce | orchestrator (+ `explorer` to locate) | a failing test or documented repro in `bug-diagnosis.md` |
| 3. Diagnose | `investigator` | root cause + evidence in `bug-diagnosis.md` |
| 4. Plan fix | `planner` (fix-scoped, minimal) | `plan.md` |
| **Plan GATE** | — | build bar: plan must be `ready` + grade **A/S** (see protocol.md); lightweight for small fixes, but the bar still holds unless explicitly overridden |
| 5. Build | `implementer` / `cpp-to-csharp-porter` | fix + **regression test that fails before, passes after**, `build-summary.md` |
| 6. Verify + review | `reviewer` (code mode) | confirms the repro is gone; `review-code.md` |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optional) | orchestrator | branch + commit + PR |
| 8. Retrospective | `retrospective` | `retro.md` — **must** include the root-cause class so similar bugs are caught earlier |

The distinguishing rule: **no fix without a reproduction and a regression test**. Diagnosis
(phase 3) is mandatory and separate from the fix — don't patch symptoms.

---

## 3. `refactor` — change structure, not behaviour

> **context → explore → characterize → plan → [GATE] → build (small steps) → review → [GATE] → ship? → retrospective**

| Phase | Agent | Output |
|---|---|---|
| 1. Context | `context-gatherer` | `context.md` (why refactor, constraints) |
| 2. Explore | `explorer` | `exploration.md` — map the blast radius / consumers |
| 3. Characterize | orchestrator + `implementer` | a **safety-net of tests** capturing current behaviour *before* touching it; note gaps |
| 4. Plan | `planner` | `plan.md` — ordered, **behaviour-preserving** steps; explicit breaking-change surfaces |
| **Plan GATE** | — | build bar: plan must be `ready` + grade **A/S** to be approvable (see protocol.md); else approve / changes / cancel |
| 5. Build | `implementer` | small, individually-verified steps; **build+tests green after each** |
| 6. Review | `reviewer` | `review-code.md` — verify no behaviour change + no contract drift |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optional) | orchestrator | branch + commit + PR |
| 8. Retrospective | `retrospective` | `retro.md` |

Distinguishing rule: **behaviour must not change**. Characterization tests (phase 3) come *before*
any edit; ReportFoundations refactors must call out every downstream consumer.

---

## 4. `spike` — timeboxed investigation to reduce uncertainty

> **frame + timebox → investigate (throwaway) → findings → [GATE: decide]**

| Phase | Agent | Output |
|---|---|---|
| 1. Frame | orchestrator | the question to answer + a timebox + what "done" means |
| 2. Context | `context-gatherer` (light) | `context.md` if a ticket exists |
| 3. Investigate | `explorer` + `investigator` (+ throwaway prototypes, isolated) | evidence, prototype notes |
| 4. Findings | orchestrator | `spike.md` — options, trade-offs, a **recommendation**, and cost/risk of each |
| **Decision GATE** | — | pick an option → usually feeds a `feature` or `refactor` workflow |

Distinguishing rules: **no production code** (prototypes are throwaway and must not be shipped);
timeboxed; the deliverable is a decision, not a merge. Capture durable learnings to memory even
though there's no retrospective phase.

---

## 5. `explore` — understand where/what (read-only)

> **scope → map → answer**

| Phase | Agent | Output |
|---|---|---|
| 1. Scope | orchestrator | restate the question + candidate repos |
| 2. Map | `explorer` | `exploration.md` (or inline) — `repo/path:line` map + flow |

No gates, no build, no ship. Use to orient before a feature/refactor, or to answer "where does X
live / how does Y flow across the repos". Fast and cheap.

---

## 6. `investigate` — understand why (read-only, deeper)

> **frame → gather evidence → hypothesize → verify → conclude**

| Phase | Agent | Output |
|---|---|---|
| 1. Frame | orchestrator | the precise question / incident |
| 2. Context | `context-gatherer` | `context.md` (tickets, related PRs, history) |
| 3. Analyze | `investigator` | `investigation.md` — evidence → hypotheses (with verdicts) → root cause → confidence |

No gates, no build. Deeper than `explore`: it answers *why/how*, ruling out alternatives with
git history, logs, and code. Often the front half of a `bug` workflow when the cause is unknown.

---

## 7. `learn` — build a mental model (read-only, teaching)

> **pick target + level → guided walkthrough → glossary → exercises**

| Phase | Agent | Output |
|---|---|---|
| 1. Target | orchestrator | subsystem/concept + learner's current level |
| 2. Teach | `learning-guide` | `learning-notes.md` — big picture → happy-path trace → key abstractions → glossary → safe exercises |

No gates, no build. For onboarding onto the report pipeline or a specific area (value-provider
params, the Spooler batch flow, pf-web DDD layering, the C++→C# port mechanism).

---

## Choosing a workflow

| If the task is… | Use |
|---|---|
| add/change user-facing or API behaviour | `feature` |
| something is broken / wrong output | `bug` |
| improve structure, keep behaviour | `refactor` |
| "should we…?" / unknown approach / evaluate an option | `spike` |
| "where is / how does X flow?" | `explore` |
| "why did / how did this happen?" | `investigate` |
| "help me understand this area" | `learn` |

When in doubt between `bug` and `investigate`: if you already know it's broken and want it fixed →
`bug` (which runs `investigate`'s diagnosis as phase 3). If you only want to understand a
behaviour → `investigate`.

## Relationship to `code-fleet`

This set is inspired by and interoperates with the org's `code-fleet` plugin. Where you'd rather
lean on the fleet's mature language packs, the `feature`/`refactor` **build + review** phases can be
delegated to `/code-fleet:work` (its `compass`→`lookout`→`dot-coder`/`ts-coder`→reviewers pipeline)
instead of the workspace `planner`/`implementer`/`reviewer`. The workspace agents add what the fleet
doesn't: the report multi-repo topology awareness, the `cpp-to-csharp-porter`, and the read-only
`explore`/`investigate`/`learn` and `retrospective` roles. Note code-fleet writes to
`.claude/work/<slug>/` while this set uses `.work/<slug>/`.
