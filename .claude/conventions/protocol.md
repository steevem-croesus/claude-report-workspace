# Working protocol (shared across all workflows)

This is the shared foundation every workflow in `workflows.md` builds on: where artifacts live,
how context is gathered, how gates and HALTs work, and the per-repo build/branch rules. It is
inspired by the conventions of the org's `code-fleet` plugin (task dir, HALT protocol, staged
gates, requirements-coverage plans, jira/gh intel) adapted to this multi-repo report workspace. See the
root `../../CLAUDE.md` for repo topology and the report pipeline.

## The task directory — `.work/<TICKET-ID>/`

Every non-trivial workflow run creates a per-task directory at the **workspace root**:
`C:\Repos\claude-report-workspace\.work\<slug>\`.

- **Slug** = the Jira key when detected (e.g. `FOG-9412`, `CFF-1234`); otherwise the kebab-case of
  the first ~4 words of the task. Re-running the same task reuses the directory.
- It lives at the workspace root on purpose — it does **not** pollute the symlinked repos, and it
  survives across sessions. Add `.work/` to your global gitignore if you don't want it tracked.

### Canonical filenames (one artifact = one file)

| File | Written by | Purpose |
|---|---|---|
| `context.md` | context-gatherer | Jira + GitHub intel brief |
| `exploration.md` | explorer | Code map for the task |
| `investigation.md` | investigator | Root-cause analysis |
| `learning-notes.md` | learning-guide | Walkthrough / mental model |
| `spike.md` | (orchestrator + explorer) | Spike findings + recommendation |
| `plan.md` | planner | Implementation plan (gates the build) |
| `bug-diagnosis.md` | investigator | Reproduction + root cause for a bug |
| `review-plan.md` | reviewer | Plan-gate findings |
| `build-summary.md` | implementer / porter | What was built + build/test results |
| `review-code.md` | reviewer | Code-gate findings |
| `retro.md` | retrospective | Retrospective + proposed learnings |
| `clarifications.md` | orchestrator | Q→A resolved before planning |

## Context gathering (start of every feature/bug/refactor/spike/investigate)

Always dispatch **context-gatherer** first. It:
1. Resolves the Jira ticket via the **Atlassian MCP** — `getAccessibleAtlassianResources`
   (for `cloudId`) → `getJiraIssue` (description, comments, acceptance criteria, links) →
   `getJiraIssueRemoteIssueLinks`. Confluence specs fetched when referenced.
2. Resolves GitHub context via the **`gh` CLI** run inside the relevant symlinked repo —
   `gh pr view/diff`, `gh issue view`, `gh search`, and `git log`.
3. Writes `context.md` and reports the target repo(s) + top open questions.

If Jira/GitHub is unreachable (headless/auth), the workflow proceeds on local evidence and says so —
it never fabricates ticket content.

## Gate protocol (INTERACTIVE — this workspace runs gated)

At each **gate**, the orchestrator stops and asks the user, via `AskUserQuestion`:

> *"Approve, request changes, or cancel?"*

- **approve** → proceed to the next phase.
- **changes** → write the user's feedback verbatim to `.work/<slug>/_signals/revision-request.md`,
  re-dispatch the phase's agent (it reads its prior artifact + the revision request), then return to
  the same gate with the revised artifact.
- **cancel** → stop the workflow.

Never auto-proceed past a gate. The two universal gates are the **plan gate** (after `plan.md`) and
the **code gate** (after `build-summary.md` + `review-code.md`); some workflows add their own
(e.g. the spike's *decision* gate).

### Plan gate — the build bar

The plan gate has an extra, non-negotiable entry condition. `plan.md` carries a header
`**Status:** <draft|ready> · **Grade:** <F|D|C|B|A|S>` (scale **F < D < C < B < A < S**; rubric
owned by `../agents/planner.md`). The workflow may build **only** from a plan that is **`ready`**
**and** graded **A or S**.

- If the plan is `draft` or graded **below A**, the gate does **not** offer *approve*. Surface the
  grade + why (blocking open questions, `needs-user` decision points), and route to **changes** —
  re-dispatch the planner (optionally resolving `needs-user` decision points via `AskUserQuestion`
  first) until it reaches `ready` + (A|S), or **cancel**.
- Only when the plan is `ready` + (A|S) does the user get the normal *approve / changes / cancel*
  choice. Approval is still required — a qualifying grade unlocks the gate, it does not auto-pass it.
- The user may **override** and approve a sub-bar plan explicitly (e.g. a deliberately small change
  they've judged fine); record the override in `revision-request.md` so it's auditable. Absent an
  explicit override, the bar holds.

## HALT protocol (agent → orchestrator)

Any producing agent (planner, implementer, porter, context-gatherer, investigator) may stop mid-run
and return a HALT block when it hits a genuine user decision:

```
HALT: need user decision
Reason: <why it can't proceed>
Question: <the specific question>
Proposed default: <recommendation>
State: <progress so far, to resume>
```

The orchestrator surfaces the question (via `AskUserQuestion`), writes the answer to
`.work/<slug>/_signals/resume.<agent>.md`, and re-dispatches. Cap: **3 HALT round-trips per agent**;
after that, proceed with the stated default or stop with a clear message.

## Per-repo build / test / lint (what agents actually run)

| Repo | Build | Test (single) | Lint |
|---|---|---|---|
| ReportManagerApi | `dotnet build repos/ReportManagerApi/ReportManagerAPI.sln` | `dotnet test <proj> --filter "FullyQualifiedName~<Name>"` | — |
| ReportFoundations | `dotnet build <the lib .sln/.csproj>` | `dotnet test <proj.SmallTests>` | — |
| pf-web | `nx build <project>` | `nx test <project> --testFile=<path>` | `nx lint <project>` |
| CroesusServer | CMake / Visual Studio | (usually read-only reference) | — |
| ReportServer | CMake / Visual Studio | (usually read-only reference) | — |

Test tiers: C# `*.SmallTests` (unit, no external deps) / `*.MediumTests` (integration), xUnit + Moq.
Angular: Vitest. The runnable API web project is `ReportManager.API/ReportManagerAPI.csproj`.

## Branch, commit & ship rules (per repo, org-mandated)

Commits/PRs happen **per symlinked repo, on that repo's own branch** — there is no shared root repo.
Agents `git add`-stage new files but **do not commit** unless the task explicitly asks; committing
is the workflow's final *ship* step, gated.

- Branch from a protected ref (`main`, `master`, `develop`, `release/*`, `support/*`) with
  **`--no-track`**: `git switch -c <name> --no-track origin/develop`.
- First push of a new branch: **`git push -u origin <branch>`** — never a bare `git push`.
- `pf-web` enforces **Conventional Commits** via commitlint (see `repos/pf-web/CLAUDE.md`); the .NET repos
  follow standard team conventions.

## Guardrails (apply to every agent and phase)

- **Never** run org-denied CLIs: `aws`, `terraform`/`tofu`, or wrappers around them (e.g. `assume`,
  `granted`). ReportManagerApi uses AWS via the SDK/config only — never the CLI.
- Read-only agents (explorer, investigator, learning-guide, reviewer, retrospective) never edit code.
- Respect each repo's own `CLAUDE.md` / `copilot-instructions.md` — they override generic advice.
