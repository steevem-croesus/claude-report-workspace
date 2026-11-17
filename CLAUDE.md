# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

`claude-report-workspace` is a curated set of symlinks assembling the codebases that make up the
**Croesus Xpert report-generation pipeline**, so that cross-repo report work can be done from a
single root. The symlinks live under **`repos/`** and each points at a checkout elsewhere on disk:

> **The workspace root is its own small *local* git repo** (on `main`, no remote) that tracks only
> the workspace tooling — `.claude/`, `docs/`, `CLAUDE.md`, this file's helpers. It does **not**
> track the product code: `repos/`, `.work/`, and `.benchmark/` are gitignored. **All product
> commits/PRs happen inside the separate symlinked repos below, never at this root.** See
> [`docs/`](docs/README.md) for the full documentation of the workflows/agents that live here.

| Symlink (under `repos/`)   | Real path                                      | Language / stack        | Role in the pipeline |
| -------------------------- | ---------------------------------------------- | ----------------------- | -------------------- |
| `repos/CroesusServer`      | `/c/Repos/monolith/PM/Products/CroesusServer`  | **C++** (CMake)         | The "Frameworkserver" monolith. Holds *legacy* report logic (`Src/Report`, `Src/ReportApi`) being ported to C#. |
| `repos/ReportServer`       | `/c/Repos/monolith/PM/Products/ReportServer`   | **C++** (CMake)         | The legacy C++ report-generation **engine/server** (`Src/RGSession`, `Src/Server`, gRPC/XMLRPC). Also a source of report logic being ported to C#. |
| `repos/ReportFoundations`  | `/c/Repos/monolith/CFF/ReportFoundations`      | **C#** (class libs)     | Shared reporting libraries: business logic, entities, design, implementations, and the **Spooler** (batch generation). Consumed by `ReportManagerApi`. |
| `repos/ReportManagerApi`   | `/c/Repos/monolith/CFF/Products/ReportManagerApi` | **C# / .NET 8** (Web API) | Async report-generation API. Clean/DDD layering; in-process batch generation, S3 storage; talks to the Frameworkserver. |
| `repos/pf-web`             | `/c/Repos/pf-web`                              | **TypeScript / Angular 21 + NX** | Frontend (Croesus Xpert). The `report` domain lives under `libs/report/`. |
| `repos/CroesusClient`      | `/c/Repos/monolith/CFF/Products/CroesusClient` | **C# / WPF**            | The legacy **WPF desktop client** — the interfaces `pf-web` is being rebuilt from. A *reference source* of report UI/logic being ported to `ReportManagerApi` + `pf-web`. Report-porting surface is staged under `TempReport/`. |
| `repos/Foundations`        | `/c/Repos/monolith/CFF/Foundations`            | **C#** (class libs)     | Shared CFF foundation libraries (non-report-specific) consumed by the C# products. |

**Only two git repos sit behind these symlinks.** Every symlink except `repos/pf-web` points into the
**same monorepo** (`/c/Repos/monolith`, remote `croesusfin/monolith`): one branch and one PR cover
ReportManagerApi + ReportFoundations + the C++ sources together. `repos/pf-web` is the second repo
(`/c/Repos/pf-web`). So a cross-stack change is **at most two branches/PRs** — one in the monolith,
one in pf-web. Check `git status`/`git branch` inside a symlink before committing — product changes
never go to the workspace-root repo, which only versions the tooling. All workspace-relative paths
below are written from the workspace root, hence the `repos/` prefix.

## How the pieces fit (report generation flow)

1. A user requests a report from the frontend (`pf-web`, or the legacy ReportWebClient).
2. `POST /api/v1/reports` on **ReportManagerApi** (`BaseReportGenerationController` →
   `ReportGenerationService`) creates a generation request and writes a status row to
   `B_RPT_BATCH_GEN_REQUEST`.
3. Generation runs **in-process**: `BaseReportGenerationService.SubmitGenerationRequest` enqueues the
   batches in memory and runs them through `BaseBatchServiceAsynchronous`, using **ReportFoundations**
   logic and the **ReportSpooler**, which reach the **CroesusServer** Frameworkserver over
   **port 8999** for portfolio/financial data. **There is no SQS hop on this path** — an SQS client
   (`IQueueMessaging`) is registered in DI but nothing consumes it.
4. The finished file is stored through `IStorageManager` (**S3** via `CloudStorageManager`, or local
   disk); the frontend downloads it via `GET /api/v1/reports/{generationId}`.

Naming convention on a vserver: queue `{vserver}-reports-sqs`, bucket `{vserver}-reports-bucket`.

## Per-repo authority (read these first)

Each repo carries its own, more detailed guidance. Prefer it over anything here for repo-local work:

- **pf-web** → `repos/pf-web/CLAUDE.md` (Angular/NX conventions, DDD layer rules, testing, commits) and `repos/pf-web/ARCHITECTURE.md`. Do not restate its rules; defer to it.
- **ReportManagerApi** → `repos/ReportManagerApi/README.md` (Docker, AWS setup, coverage) and `repos/ReportManagerApi/copilot-instructions.md` (the `IValueProviderParameter` recipe and the C++→C# port workflow — see below).
- **ReportManagerApi** routes → `repos/ReportManagerApi/ReportManager.API/API_Routes_Documentation.md`.
- **ReportServer** → no CLAUDE/README, but `repos/ReportServer/Doc/` holds report-parameter references
  useful when porting (e.g. `Bible des parametres de rapport.docx`, `params_source.xls`,
  `sources.xls`, `SrvRap-API.doc`). Mostly `.doc`/`.xls`/`.pdf`, not plain text.
- **Monolith conventions & architecture** → `C:\Repos\monolith\doc\references\` (outside `repos/`) — the
  authoritative C#/ORM **coding conventions** (StyleCop restrictive ruleset, `Result<T>`, NuGet CPM) and
  **architecture references** (ReportServer, RTM, FrameworkServer, AgentServer, CoreApi). Catalogued, with the
  precedence chain, in [`.claude/conventions/monolith-references.md`](.claude/conventions/monolith-references.md);
  the workflows/agents consult it when generating, reviewing, or explaining monolith code.

## Cross-repo workflow: porting C++ report logic to C#

The recurring reason these repos sit together: **converting a C++ report function from
`CroesusServer` *or* `ReportServer` into a C# `IValueProviderParameter`** in `ReportManagerApi`
(the function may live in either C++ source — search both). The full recipe
(folder placement, executer registration, which repository interface to inject) is in
`repos/ReportManagerApi/copilot-instructions.md`. Key mapping cues when reading the C++ source:

- C++ references a `PREF_` / preference / config  → inject `IPreferencesRepository`.
- C++ references a `PARAM_` / parameter            → inject `IReportCommandAndQueryContextRepository`.
- Date logic                                        → inject `IParameterDateValueService` / `IDateTimeService`.

New parameter classes go under
`ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/` (date ones in
`.../Parameters/Date/`) and must be registered — in alphabetical order — in the matching
`Pre`/`PostParamEntryValueProviderFunctionsExecuter.cs`.

- For a **declarative radio/combo**, the already-migrated **sibling report sharing the same `TPL_`
  template** is the first oracle for the `PossibleValues`/`PossibleDisplayValues` keys — copy them 1:1
  before resolving legacy C++ `.resx` keys (which are often the wrong/old namespace). New keys use the
  `RPT_mgr_*` prefix, never `CRESUS_rpt_*`; never invent a translation.

## Commands by repo

Per-repo build/test/coverage/serve commands and their gotchas live in the
`workspace-commands` skill (`.claude/skills/workspace-commands/SKILL.md`) — invoke it before
building or testing anything under `repos/`. Two things worth knowing up front:
**ReportManagerApi must be built from the real monolith path, not the `repos/` symlink**, and the
C++ repos (`CroesusServer`, `ReportServer`) are **read-only sources of truth** for the porting
workflow — a function to port may live in either, so search both.

## Conventions

- Commit inside the real repo behind the symlink (monolith or pf-web), on that repo's branch — never at the workspace root.
- Respect each repo's own commit rules: `pf-web` enforces **Conventional Commits** via commitlint (see its CLAUDE.md); the .NET repos follow standard team conventions.
- When a task spans repos (e.g. a new report field: C++ analysis → C# parameter → API route → Angular UI), follow the pipeline order above: the C++/C# parts share one monolith branch/PR, the Angular part gets its own pf-web branch/PR.

## Working with Claude in this workspace

This workspace ships a set of **agents** and **workflow conventions** (under `.claude/`) that
encode how to build features, fix bugs, refactor, spike, explore, investigate, and learn here —
each with its own phase sequence, gated for approval, and wired to pull context from **Jira**
(Atlassian MCP) and **GitHub** (`gh`). They are inspired by and interoperate with the org's
`code-fleet` plugin.

> 📚 **Full documentation for everything in this section lives under [`docs/`](docs/README.md)**,
> organised by the [Diátaxis](https://diataxis.fr/) method (tutorials · how-to · reference ·
> explanation). Start at [`docs/README.md`](docs/README.md). The `.claude/` files remain the source
> of truth; the docs explain and index them.

Where things live — the files are the source of truth; consult them rather than this list:

- **Workflows** — `.claude/conventions/workflows.md` (seven playbooks: `feature`, `bug`, `refactor`,
  `spike`, `explore`, `investigate`, `learn` — each a live skill, with phases and gates).
- **Shared protocol** — `.claude/conventions/protocol.md` (task directory, artifact filenames, the
  gate + HALT protocols, org git/branch guardrails).
- **Monolith conventions & references** — `.claude/conventions/monolith-references.md`, the catalogued
  index of `C:\Repos\monolith\doc\references\` with the precedence chain.
- **Team memory** — `.claude/conventions/known-pitfalls.md` (lessons already paid for: porting,
  Xpert-vs-Conseiller validation, tests, review, git) and `.claude/conventions/rma-architecture-notes.md`
  (verified facts about ReportManagerApi internals). **Durable learnings about the code or project go
  there, not into Claude memory** — subagents and teammates only see the repo.
- **Agents** — `.claude/agents/` (dispatch by `subagent_type`); **templates** —
  `.claude/conventions/templates/`; **migration conventions** —
  `.claude/conventions/{migration-protocol,backend-conventions,frontend-conventions}.md`.

Rules that aren't discoverable from those files:

- The **monolith skills** (`croesus-orm`, `create-{small,medium,large}-tests`, `create-internal-route`,
  `implement-full-story`, `croesus-process-conventions`) are *symlinks* into
  `/c/Repos/monolith/.claude/skills/` — machine-specific and gitignored. (Re)create them with
  `link-monolith-skills.ps1` run elevated, then restart Claude Code. **They are owned by the monolith
  repo — edit them there, never here.**
- **All deliverables for a report migration go under `.work/{slug}/`** (analysis, logs, review, PDF);
  `{slug}` = the Jira key if a ticket is given, else the report internal name. `.work/` is not versioned.
  `docs/reports/{REPORT_NAME}/` is a **versioned archive**: copy final deliverables worth keeping in git
  (`analysis.md`, `migration-log-*.md`) there only when the user asks — never work in it directly. Shared global inputs (not deliverables) stay under `docs/`:
  `fields.csv` (master parameter list) + `template_ids.csv`.
- Migration work is reachable directly (dispatch a migration agent) or through the gated `/feature`
  **migration mode** (`.claude/skills/feature/SKILL.md` §1a).

Starting a piece of work? Pick the matching workflow in `workflows.md` and follow its phases;
begin every non-trivial task by dispatching `context-gatherer` with the Jira key and/or GitHub ref.
