# Reference — Workflows

Seven workflows, each a phase sequence tuned to a *kind* of work. All share the foundation in
[gates & protocol](gates-and-protocol.md). Notation: `→` is a phase; **[GATE]** is a stop-for-approval
point; agents are named in `code`.

**Authoritative source:** [`.claude/conventions/workflows.md`](../../.claude/conventions/workflows.md).
Each workflow is also a live skill under `.claude/skills/` (see [skills](skills.md)), invokable as
`/feature`, `/bug`, `/refactor`, `/spike`, `/explore`, `/investigate`, `/learn`.

| # | Workflow | Gated | Writes code | One-liner |
|---|---|---|---|---|
| 1 | [feature](#1-feature) | ✅ | ✅ | build something new |
| 2 | [bug](#2-bug) | ✅ | ✅ | fix a defect (repro + regression test required) |
| 3 | [refactor](#3-refactor) | ✅ | ✅ | change structure, not behaviour |
| 4 | [spike](#4-spike) | ✅ (decision) | ✗ (throwaway) | timeboxed investigation → decision |
| 5 | [explore](#5-explore) | ✗ | ✗ | map where/what (read-only) |
| 6 | [investigate](#6-investigate) | ✗ | ✗ | root-cause why/how (read-only) |
| 7 | [learn](#7-learn) | ✗ | ✗ | build a mental model (read-only) |

---

## 1. feature

> *(spike?) → context → explore → plan → **[GATE]** → build → review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Output |
|---|---|---|
| 0. Spike (optional) | run `spike` first *only if* the approach is genuinely unknown | `spike.md` |
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Explore | [`explorer`](agents.md#explorer) | `exploration.md` |
| 3. Plan | [`planner`](agents.md#planner) | `plan.md` (+ requirements-coverage table) |
| **Plan GATE** | — | build bar: `ready` + **A/S** to be approvable; else changes / cancel |
| 4. Build | [`implementer`](agents.md#implementer) or [`cpp-to-csharp-porter`](agents.md#cpp-to-csharp-porter); one per repo slice | code + tests, `build-summary.md` |
| 5. Review | [`reviewer`](agents.md#reviewer) (code mode) | `review-code.md` |
| **Code GATE** | — | approve / changes (loop to build, cap 3) / cancel |
| 6. Ship (optional, gated) | orchestrator | branch + commit + PR **per repo** |
| 7. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` + proposed learnings |

Cross-repo features run phase 4 in pipeline order (C++ analysis → C#/API → Angular UI), each repo on
its own branch/PR. How-to: [run the feature workflow](../how-to/run-the-feature-workflow.md).

---

## 2. bug

> *context → reproduce → diagnose → plan-fix → **[GATE]** → build → verify+review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Output |
|---|---|---|
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Reproduce | orchestrator (+ [`explorer`](agents.md#explorer) to locate) | failing test / repro in `bug-diagnosis.md` |
| 3. Diagnose | [`investigator`](agents.md#investigator) | root cause + evidence in `bug-diagnosis.md` |
| 4. Plan fix | [`planner`](agents.md#planner) (minimal) | `plan.md` |
| **Plan GATE** | — | build bar applies |
| 5. Build | [`implementer`](agents.md#implementer) / [`cpp-to-csharp-porter`](agents.md#cpp-to-csharp-porter) | fix + **regression test (fails before, passes after)**, `build-summary.md` |
| 6. Verify + review | [`reviewer`](agents.md#reviewer) | confirms repro gone; `review-code.md` |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optional) | orchestrator | branch + commit + PR |
| 8. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` — **must** include root-cause class |

Distinguishing rule: **no fix without a reproduction and a regression test.** Diagnosis (phase 3) is
mandatory and separate from the fix. How-to: [fix a bug](../how-to/fix-a-bug.md).

---

## 3. refactor

> *context → explore → characterize → plan → **[GATE]** → build (small steps) → review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Output |
|---|---|---|
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Explore | [`explorer`](agents.md#explorer) | `exploration.md` — the blast radius / consumers |
| 3. Characterize | orchestrator + [`implementer`](agents.md#implementer) | safety-net tests pinning current behaviour *before* any edit |
| 4. Plan | [`planner`](agents.md#planner) | `plan.md` — ordered, behaviour-preserving steps; explicit breaking surfaces |
| **Plan GATE** | — | build bar applies |
| 5. Build | [`implementer`](agents.md#implementer) | small steps; **build+tests green after each** |
| 6. Review | [`reviewer`](agents.md#reviewer) | `review-code.md` — verify no behaviour change / no contract drift |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optional) | orchestrator | branch + commit + PR |
| 8. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` |

Distinguishing rule: **behaviour must not change.** Characterization tests come *before* any edit; a
`ReportFoundations` refactor must name every downstream consumer.

---

## 4. spike

> *frame + timebox → context (light) → investigate (throwaway) → findings → **[GATE: decide]***

| Phase | Agent | Output |
|---|---|---|
| 1. Frame | orchestrator | the question + a timebox + what "done" means |
| 2. Context (light) | [`context-gatherer`](agents.md#context-gatherer) | `context.md` if a ticket exists |
| 3. Investigate | [`explorer`](agents.md#explorer) + [`investigator`](agents.md#investigator) (+ isolated throwaway prototypes) | evidence, prototype notes |
| 4. Findings | orchestrator | `spike.md` — options, trade-offs, a **recommendation** |
| **Decision GATE** | — | pick an option → usually feeds a `feature` or `refactor` |

Distinguishing rules: **no production code** (prototypes are throwaway and isolated); **timeboxed**;
deliverable is a **decision**, not a merge. No retrospective phase, but durable learnings are still
captured to memory (with approval).

---

## 5. explore

> *scope → map → answer*

| Phase | Agent | Output |
|---|---|---|
| 1. Scope | orchestrator | restated question + candidate repos |
| 2. Map | [`explorer`](agents.md#explorer) | `exploration.md` (or inline) — `repo/path:line` map + flow |

No gates, no build, no ship. Answers *where does X live / how does Y flow across the repos*. Cheap; a
quick one-off may skip the task directory. How-to: [choose a workflow](../how-to/choose-a-workflow.md).

---

## 6. investigate

> *frame → context → analyze → conclude*

| Phase | Agent | Output |
|---|---|---|
| 1. Frame | orchestrator | the precise question / incident |
| 2. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 3. Analyze | [`investigator`](agents.md#investigator) | `investigation.md` — evidence → hypotheses (with verdicts) → root cause → confidence |

No gates, no build. Deeper than `explore`: answers *why/how*, ruling out alternatives with git
history, logs, and code. Often the front half of a `bug`.

---

## 7. learn

> *pick target + level → guided walkthrough → glossary → exercises*

| Phase | Agent | Output |
|---|---|---|
| 1. Target | orchestrator | subsystem/concept + learner's current level |
| 2. Teach | [`learning-guide`](agents.md#learning-guide) | `learning-notes.md` — big picture → happy-path trace → key abstractions → glossary → safe exercises |

No gates, no build. For onboarding onto the pipeline or a specific area.

---

## Relationship to code-fleet

This set is inspired by and interoperates with the org's `code-fleet` plugin. The `feature`/`refactor`
**build + review** phases can be delegated to `/code-fleet:work` (its
`compass`→`lookout`→`dot-coder`/`ts-coder`→reviewers pipeline). The workspace agents add what the
fleet doesn't: multi-repo report topology awareness, the `cpp-to-csharp-porter`, and the read-only
`explore`/`investigate`/`learn` + `retrospective` roles. Note: code-fleet writes to
`.claude/work/<slug>/`; this set uses `.work/<slug>/`.
