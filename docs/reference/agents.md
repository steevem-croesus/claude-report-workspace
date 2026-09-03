# Reference — Agents

Nine agents live under [`.claude/agents/`](../../.claude/agents/), dispatched via the Agent tool by
the workflow skills. Each carries a distinguished/fellow-level engineering persona and a narrow role.
They split into **read-only** (never edit code) and **editing**.

| Agent | Role | Read-only? | Model | Writes |
|---|---|---|---|---|
| [`context-gatherer`](#context-gatherer) | Jira + GitHub intel | ✅ | Sonnet | `context.md` |
| [`explorer`](#explorer) | cross-repo code map | ✅ | Sonnet | `exploration.md` |
| [`investigator`](#investigator) | root-cause analysis | ✅ | Opus | `investigation.md` / `bug-diagnosis.md` |
| [`learning-guide`](#learning-guide) | teaching walkthrough | ✅ | Sonnet | `learning-notes.md` |
| [`reviewer`](#reviewer) | plan/code review | ✅ | Opus | `review-plan.md` / `review-code.md` |
| [`retrospective`](#retrospective) | capture learnings | ✅ (code) | Sonnet | `retro.md` |
| [`planner`](#planner) | implementation plan | writes `plan.md` only | Opus | `plan.md` |
| [`implementer`](#implementer) | build + test | ✏️ edits code | Opus | code, tests, `build-summary.md` |
| [`cpp-to-csharp-porter`](#cpp-to-csharp-porter) | C++→C# value-provider port | ✏️ edits code | Opus | code, tests, `build-summary.md` |

All agents obey the shared [guardrails](gates-and-protocol.md#guardrails): never run org-denied CLIs
(`aws`, `terraform`/`tofu`), respect each repo's own `CLAUDE.md`, and read-only agents never edit.

## Per-agent model

Each agent pins its own model via a `model:` field in its
[`.claude/agents/*.md`](../../.claude/agents/) frontmatter, tiered by what the role actually demands:

- **Opus** — `planner`, `implementer`, `cpp-to-csharp-porter`, `reviewer`, `investigator`: anything
  that designs the change, writes or ports code, judges quality, or does root-cause reasoning. These
  are the correctness-critical, high-stakes roles — the plan that gates the build, the financial/date
  C++→C# port, the review the build bar depends on.
- **Sonnet** — `context-gatherer`, `explorer`, `learning-guide`, `retrospective`: the read-only
  gather / map / teach / summarise roles. Plenty capable, faster, and cheaper.

To change a tier, edit that agent's `model:` value (`opus` / `sonnet` / `haiku`, or `inherit` to
follow your session model). Because the field lives in the agent frontmatter, the choice applies
everywhere the agent is dispatched, in every workflow.

---

## context-gatherer

- **Role:** assemble a faithful, cited Context brief before anyone writes code. Does *not* design,
  estimate, or write production code.
- **Invoked:** first, in every `feature`/`bug`/`refactor`/`spike`/`investigate` run.
- **Inputs:** a Jira key, a GitHub ref (`#123` / URL), or free-text task.
- **Tools:** Read, Write, Grep, Glob, Bash, WebFetch, and Atlassian MCP (`getAccessibleAtlassianResources`,
  `getJiraIssue`, `searchJiraIssuesUsingJql`, `getJiraIssueRemoteIssueLinks`, Confluence fetch).
- **Procedure:** resolve the Jira ticket (summary, description, comments, acceptance criteria, links,
  referenced Confluence specs) → resolve GitHub context via `gh` inside the relevant repo → cross-
  reference asked-vs-existing and flag contradictions.
- **Output:** `context.md` (template:
  [`templates/context.md`](../../.claude/conventions/templates/context.md)) + a summary naming the
  target repo(s) and top 3 open questions.
- **Guardrail:** read-only on Jira/GitHub too — never comments on or transitions a ticket, never opens
  a PR. If it can't reach Jira/GitHub, it says so and works from local evidence; never fabricates.

## explorer

- **Role:** locate and map code across the repos so others can orient fast. Maps; does not judge or
  propose fixes.
- **Invoked:** `explore` workflow; start of `feature`/`refactor`; anywhere a code map is needed.
- **Tools:** Read, Grep, Glob, Bash.
- **Notable heuristic:** when a feature reads config/"default"/setup data, it doesn't stop at the
  obvious helper — it also traces the **repository / Flex "scenario" discovery path**
  (`I*Repository.BuildScenarioData`, `Get*SetupConfig`), because the generation path often resolves
  data through a scenario the query-side helper hides. It also flags shared surfaces (interfaces that
  might need to become generic, base classes to extract) when a feature adds a flow **alongside** an
  existing one.
- **Output:** a `repo/path:line` table grouped by repo + prose flow + 2–3 best entry points →
  `exploration.md` (or inline for quick questions).

## investigator

- **Role:** find the *root cause* of a defect/behaviour with evidence, not plausibility. Explains;
  does not fix.
- **Invoked:** `investigate` workflow; the diagnose phase of `bug`.
- **Tools:** Read, Grep, Glob, Bash, WebFetch.
- **Procedure:** frame → gather evidence (code, `git log`/`git blame`/`git log -S`, tickets/PRs,
  logs) → hypothesize → **verify adversarially** (try to refute the leading hypothesis; distinguish
  trigger from root cause) → conclude with confidence (high/medium/low).
- **Output:** `investigation.md` (or `bug-diagnosis.md` in a bug): symptom → evidence → hypotheses
  (with verdicts) → root cause → confidence → open questions. Every claim cited.

## learning-guide

- **Role:** make a newcomer productive in a chosen area, teaching from the real code.
- **Invoked:** `learn` workflow.
- **Tools:** Read, Grep, Glob, Bash, WebFetch.
- **Output:** `learning-notes.md` — big picture → happy-path trace (`repo/path:line`) → key
  abstractions → glossary (`PREF_`, `PARAM_`, spooler, value-provider, `generationId`, …) → 2–4 safe,
  read-only/throwaway exercises → where to go next.

## reviewer

- **Role:** adversarial, terse review. No praise, no summaries, no scope creep.
- **Invoked:** the plan gate (plan mode) and code gate (code mode) of `feature`/`bug`/`refactor`.
- **Tools:** Read, Grep, Glob, Bash (may build/run tests to verify a finding — non-mutating).
- **Two modes:**
  - **Plan review** — does the plan satisfy its requirements-coverage table? Is placement/layering
    correct, are risks/tests/estimate realistic, and — critically — **is the self-assigned Grade +
    Status honest?** An over-graded or wrongly-`ready` plan is a must-fix, because the build bar
    depends on it.
  - **Code review** — correctness bugs, layering violations, weak/missing tests, cross-repo contract
    drift, C++→C# fidelity.
- **Output:** one line per finding — `repo/path:line: <emoji> <severity>: <problem>. <fix>.` —
  severities 🔴 must-fix / 🟡 should-fix / 🟢 consider; a **Don't miss** line; a verdict (`clean` /
  `should-fix only` / `must-fix present`) → `review-plan.md` or `review-code.md`.

## retrospective

- **Role:** turn finished work into durable knowledge. Does not modify production code.
- **Invoked:** last phase of `feature`/`bug`/`refactor`.
- **Tools:** Read, Glob, Grep, Bash, Write.
- **Output:** `retro.md` (template:
  [`templates/retro.md`](../../.claude/conventions/templates/retro.md)) — what shipped, plan vs
  reality, what went well/hard, root-cause *class* (bugs only), follow-ups, and 1–4 **proposed**
  durable learnings (memory entries + doc/CLAUDE.md edits) as a checklist. **Never writes memory or
  edits docs itself** — it surfaces the checklist for you to approve.

## planner

- **Role:** design the change before a line is written. Does not write production code.
- **Invoked:** the plan phase of `feature`/`bug`/`refactor` (after context + exploration).
- **Tools:** Read, Grep, Glob, Bash, Write.
- **Honours architecture rules:** pf-web DDD layering; ReportManagerApi clean architecture + the
  value-provider recipe; ReportFoundations breaking-surface call-outs (and the discovery-route
  check — verify whether the *generation* path resolves data via a Flex scenario before scoping RF
  out); parallel-flow shared-base/interface-reshape as a first-class decision point.
- **Output:** `plan.md` (template:
  [`templates/plan.md`](../../.claude/conventions/templates/plan.md)) with a **Status/Grade header**,
  Problem, Requirements coverage, Affected areas, **Contracts & interfaces**, Steps (grouped `#### <repo>`
  for multi-repo), Tests, Risks, Decision points (`resolved`/`needs-user`), Estimate (T-shirt sizes +
  confidence), Open questions.
- **Contracts & interfaces:** the concrete design the implementer writes as-is — endpoints (route, auth,
  request/response, status codes, controller), DTO/entity/model schemas as code blocks (types + nullability,
  C# and its TS mirror), exact public method signatures, columns/`spAddColumn` migrations, `PARAM_`/`PREF_`/
  `RPT_mgr_*` keys. Only what the change creates or modifies; anything not verified in code is flagged
  `⚠ à confirmer` and lowers the estimate's confidence. A contract left as prose caps the plan at **B**.
- **The build bar:** grades on **F < D < C < B < A < S**; marks `draft` unless honestly `ready` +
  (A|S). **Never inflates the grade to pass the gate** — see
  [gates & the build bar](../explanation/gates-and-the-build-bar.md).
- **HALT:** stops and asks on a genuine fork rather than guessing.

## implementer

- **Role:** turn an approved plan into working, tested code across C#/.NET, Angular/TypeScript, or
  C++. Does not re-plan or exceed the plan's scope.
- **Invoked:** the build (and refactor characterize) phase, per repo slice — *except* value-provider
  ports, which go to the porter.
- **Tools:** Read, Glob, Grep, Edit, Write, Bash, `mcp__ide__getDiagnostics`.
- **Discipline:** match the target repo's `CLAUDE.md` conventions exactly; write tests in the repo's
  tier/style; **always build then run the authored tests before returning** and report real command
  output; `git add`-stage new files but **do not commit**.
- **Output:** `build-summary.md` — files changed per repo, tests added, exact commands + outcomes,
  deviations. Outcome ∈ `ok` / `tests-failed` / `build-failed`.
- **HALT:** stops if the plan is ambiguous or contradicts the code.

## cpp-to-csharp-porter

- **Role:** the specialist for reimplementing a C++ report function as a C# `IValueProviderParameter`
  in ReportManagerApi. Follows [`copilot-instructions.md`](../../repos/ReportManagerApi/copilot-instructions.md)
  exactly.
- **Invoked:** the build phase when a step is a value-provider port (inside `feature`/`bug`), or
  standalone.
- **Tools:** Read, Glob, Grep, Edit, Write, Bash, `mcp__ide__getDiagnostics`.
- **Procedure & dependency mapping:** see the how-to,
  [port a C++ function to C#](../how-to/port-cpp-to-csharp.md).
- **Output:** `build-summary.md` — C++ source (`repo/path:line`) + semantics, the C# class + injected
  deps, the executer line added, any `IDateTimeService` addition, tests, build/test results, and any
  C++ behaviour it could **not** faithfully reproduce.
- **Guardrail:** fidelity first — the C# must match the C++ semantics; deliberate divergences are
  called out. HALTs rather than guessing financial/date logic.
