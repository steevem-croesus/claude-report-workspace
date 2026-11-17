# Reference — Gates & protocol

The shared foundation every workflow builds on. **Authoritative source:**
[`.claude/conventions/protocol.md`](../../.claude/conventions/protocol.md).

## Gate protocol (interactive)

This workspace runs **gated**. At each gate the orchestrator stops and asks you (via a multiple-choice
prompt): *approve / request changes / cancel*.

- **approve** → proceed to the next phase.
- **request changes** → your feedback is written verbatim to
  `.work/<slug>/_signals/revision-request.md`; the phase's agent is re-dispatched (it reads its prior
  artifact + the revision request); then you return to the same gate with the revised artifact.
- **cancel** → stop the workflow.

The orchestrator **never auto-proceeds past a gate.** The two universal gates are the **plan gate**
(after `plan.md`) and the **code gate** (after `build-summary.md` + `review-code.md`). Some workflows
add their own (the spike's *decision* gate).

## The plan gate — the build bar

The plan gate has an extra, non-negotiable entry condition. `plan.md` carries a header:

```
**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
```

Scale: **F < D < C < B < A < S**. The workflow may build **only** from a plan that is **`ready`** *and*
graded **A or S**.

- **`draft` or below A** → the gate does **not** offer *approve*. It surfaces the grade + blockers
  (open questions, `needs-user` decision points) and routes to **request changes** (re-dispatch the
  planner) or **cancel**.
- **`ready` + A/S** → normal *approve / changes / cancel*. A qualifying grade *unlocks* the gate; it
  does not auto-pass it — approval is still required.
- **Override** → you may explicitly approve a sub-bar plan (e.g. a deliberately tiny change). The
  override is recorded in `revision-request.md` so it's auditable. Absent an explicit override, the
  bar holds.

The rubric is owned by [`planner.md`](../../.claude/agents/planner.md); how-to:
[get a plan past the gate](../how-to/pass-the-plan-gate.md); rationale:
[gates & the build bar](../explanation/gates-and-the-build-bar.md).

## The code gate

After build + review, present the reviewer's verdict + the `build-summary.md` outcome. *approve /
changes / cancel*. **changes** (or any `must-fix` finding) loops back to build against the review —
capped at **3 build↔review iterations**, after which the workflow stops and reports remaining issues.

## HALT protocol (agent → orchestrator)

Any producing agent (planner, implementer, porter, context-gatherer, investigator) may stop mid-run
and return a HALT block on a genuine user decision:

```
HALT: need user decision
Reason: <why it can't proceed>
Question: <the specific question>
Proposed default: <recommendation>
State: <progress so far, to resume>
```

The orchestrator surfaces the question, writes the answer to `_signals/resume.<agent>.md`, and
re-dispatches. **Cap: 3 HALT round-trips per agent**; after that, proceed with the stated default or
stop with a clear message.

## Per-repo build / test / lint

| Repo | Build | Test (single) | Lint |
|---|---|---|---|
| ReportManagerApi | `dotnet build /c/Repos/monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.sln` | `dotnet test <proj> --filter "FullyQualifiedName~<Name>"` | — |
| ReportFoundations | `dotnet build <lib .sln/.csproj>` | `dotnet test <proj.SmallTests>` | — |
| pf-web | `nx build <project>` | `nx test <project> --testFile=<path>` | `nx lint <project>` |
| CroesusServer | CMake / Visual Studio | (usually read-only reference) | — |
| ReportServer | CMake / Visual Studio | (usually read-only reference) | — |

Test tiers: C# `*.SmallTests` (unit, no external deps) / `*.MediumTests` (integration), xUnit + Moq;
Angular: Vitest. The runnable API web project is `ReportManager.API/ReportManagerAPI.csproj`.

## Branch, commit & ship rules

Product commits/PRs happen **in the real repo behind the symlink**, never in the workspace-root repo. There are
only two product repos: the `monolith` monorepo (every symlink except pf-web — one branch/PR covers C# + C++) and `pf-web`. Agents `git add`-stage new files but **do not commit** unless the task explicitly
asks; committing is the workflow's final, gated *ship* step.

- Branch from a protected ref (`main`, `master`, `develop`, `release/*`, `support/*`) with
  **`--no-track`**: `git switch -c <name> --no-track origin/develop`.
- First push of a new branch: **`git push -u origin <branch>`** — never a bare `git push`.
- `pf-web` enforces **Conventional Commits** via commitlint; the .NET repos follow standard team
  conventions.

> These mirror the org-level git guardrails: never let a new branch silently track a protected ref;
> always make the destination explicit on first push.

## Guardrails (every agent, every phase)

- **Never** run org-denied CLIs: `aws`, `terraform`/`tofu`, or wrappers around them (`assume`,
  `granted`). ReportManagerApi uses AWS via the SDK/config only — never the CLI.
- Read-only agents (explorer, investigator, learning-guide, reviewer, retrospective) never edit code.
- Respect each repo's own `CLAUDE.md` / `copilot-instructions.md` — they override generic advice.

## Context gathering

Always dispatch [`context-gatherer`](agents.md#context-gatherer) first in
`feature`/`bug`/`refactor`/`spike`/`investigate`. It resolves the Jira ticket via the Atlassian MCP,
resolves GitHub context via `gh` inside the relevant repo, and writes `context.md`. If Jira/GitHub is
unreachable (headless/auth), the workflow proceeds on local evidence and says so — it never fabricates
ticket content.
