# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

`claude-report-workspace` is **not a repository** — it is a curated set of symlinks assembling
the codebases that make up the **Croesus Xpert report-generation pipeline**, so that cross-repo
report work can be done from a single root. The symlinks live under **`repos/`** and each points
at a checkout elsewhere on disk:

| Symlink (under `repos/`)   | Real path                                      | Language / stack        | Role in the pipeline |
| -------------------------- | ---------------------------------------------- | ----------------------- | -------------------- |
| `repos/CroesusServer`      | `/c/Repos/monolith/PM/Products/CroesusServer`  | **C++** (CMake)         | The "Frameworkserver" monolith. Holds *legacy* report logic (`Src/Report`, `Src/ReportApi`) being ported to C#. |
| `repos/ReportServer`       | `/c/Repos/monolith/PM/Products/ReportServer`   | **C++** (CMake)         | The legacy C++ report-generation **engine/server** (`Src/RGSession`, `Src/Server`, gRPC/XMLRPC). Also a source of report logic being ported to C#. |
| `repos/ReportFoundations`  | `/c/Repos/monolith/CFF/ReportFoundations`      | **C#** (class libs)     | Shared reporting libraries: business logic, entities, design, implementations, and the **Spooler** (batch generation). Consumed by `ReportManagerApi`. |
| `repos/ReportManagerApi`   | `/c/Repos/monolith/CFF/Products/ReportManagerApi` | **C# / .NET 8** (Web API) | Async report-generation API. Clean/DDD layering; uses AWS SQS + S3; talks to the Frameworkserver. |
| `repos/pf-web`             | `/c/Repos/pf-web`                              | **TypeScript / Angular 21 + NX** | Frontend (Croesus Xpert). The `report` domain lives under `libs/report/`. |

Because these are symlinks, git operations run against the *real* repos, each on its own
branch and remote. Check `git status`/`git branch` inside a given symlink (e.g. `cd repos/pf-web`)
before committing — there is no single top-level repo to commit to. All workspace-relative paths
below are written from the workspace root, hence the `repos/` prefix.

## How the pieces fit (report generation flow)

1. A user requests a report from the frontend (`pf-web`, or the legacy ReportWebClient).
2. `POST /api/v1/reports` on **ReportManagerApi** creates a generation request: the payload is
   pushed to an **AWS SQS queue** and a status row is written to `B_RPT_BATCH_GEN_REQUEST`.
3. A batch worker (ReportBatchService) dequeues the request and generates the report using
   **ReportFoundations** logic, which in turn reaches the **CroesusServer** Frameworkserver
   over **port 8999** for portfolio/financial data.
4. The finished file lands in an **S3 bucket**; the frontend downloads it via
   `GET /api/v1/reports/{generationId}`.

Naming convention on a vserver: queue `{vserver}-reports-sqs`, bucket `{vserver}-reports-bucket`.

## Per-repo authority (read these first)

Each repo carries its own, more detailed guidance. Prefer it over anything here for repo-local work:

- **pf-web** → `repos/pf-web/CLAUDE.md` (Angular/NX conventions, DDD layer rules, testing, commits) and `repos/pf-web/ARCHITECTURE.md`. Do not restate its rules; defer to it.
- **ReportManagerApi** → `repos/ReportManagerApi/README.md` (Docker, AWS setup, coverage) and `repos/ReportManagerApi/copilot-instructions.md` (the `IValueProviderParameter` recipe and the C++→C# port workflow — see below).
- **ReportManagerApi** routes → `repos/ReportManagerApi/ReportManager.API/API_Routes_Documentation.md`.
- **ReportServer** → no CLAUDE/README, but `repos/ReportServer/Doc/` holds report-parameter references
  useful when porting (e.g. `Bible des parametres de rapport.docx`, `params_source.xls`,
  `sources.xls`, `SrvRap-API.doc`). Mostly `.doc`/`.xls`/`.pdf`, not plain text.

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

## Commands by repo

### ReportManagerApi & ReportFoundations (.NET 8, C#)

```bash
# Build / test the API solution
dotnet build repos/ReportManagerApi/ReportManagerAPI.sln
dotnet test  repos/ReportManagerApi/ReportManagerAPI.sln

# Run a single test project or a single test
dotnet test repos/ReportManagerApi/ReportManagerAPI.Domain.SmallTests
dotnet test repos/ReportManagerApi/ReportManagerAPI.Domain.SmallTests --filter "FullyQualifiedName~DateTimeServiceTests"

# Code coverage (from the repo dir, needs dotnet-reportgenerator-globaltool)
cd repos/ReportManagerApi && ./show-code-coverage.cmd

# Docker
docker build -t reportmanagerapi repos/ReportManagerApi --no-cache --progress=plain
docker run -d -p 5000:80 --name reportmanagerapi reportmanagerapi
```

- The runnable web project is **`ReportManager.API/ReportManagerAPI.csproj`** (contains `Program.cs`, controllers). The bare `ReportManagerAPI/` folder is a build-output stub — ignore it.
- Test-project naming: `*.SmallTests` (unit, no external deps), `*.MediumTests` (integration). Stack is **xUnit + Moq** (some MSTest present).
- `ReportFoundations` projects each have their own `.sln`/`.csproj` and are also referenced by the API solution; build them the same way.
- Local AWS/auth config lives in `appsettings.Development.json` (queue URL, bucket, `AWSOptions`) and `launchSettings.json` (`AWS_PROFILE`). Requires a reachable Frameworkserver on port 8999.

### CroesusServer & ReportServer (C++, CMake)

Both are built with CMake / Visual Studio (`CroesusServer.sln` / `ReportServer.sln`, each with a
`CMakeLists.txt`). They are generally **read-only sources of truth** for the porting workflow — you
locate and analyze C++ functions here, you don't typically modify them for report tasks. A report
function to port may live in either one, so search both.

- **CroesusServer** — Frameworkserver monolith; report logic under `Src/Report`, `Src/ReportApi`.
  Its `POST_BUILD` step generates `versions.ini` and signs the binary.
- **ReportServer** — the legacy report-generation engine; generation logic under `Src/RGSession`
  (`rgs_report_generation.c`, `gen_engine_info.c`), plus `Src/CmdManager`, `Src/Server`, `Src/gRPC`,
  `Src/XMLRPC`.

### pf-web (Angular 21 + NX)

See `repos/pf-web/CLAUDE.md` for the full command set. Most-used:

```bash
cd repos/pf-web
npm install
nx hybrid xpert --backend=http://localhost   # serve against a backend
nx test report                                # test the report domain libs
nx lint <project>
```

## Conventions

- Commit inside the specific symlinked repo, on that repo's branch — never assume a shared root.
- Respect each repo's own commit rules: `pf-web` enforces **Conventional Commits** via commitlint (see its CLAUDE.md); the .NET repos follow standard team conventions.
- When a task spans repos (e.g. a new report field: C++ analysis → C# parameter → API route → Angular UI), follow the pipeline order above and keep each repo's change on its own branch/PR.

## Working with Claude in this workspace

This workspace ships a set of **agents** and **workflow conventions** (under `.claude/`) that
encode how to build features, fix bugs, refactor, spike, explore, investigate, and learn here —
each with its own phase sequence, gated for approval, and wired to pull context from **Jira**
(Atlassian MCP) and **GitHub** (`gh`). They are inspired by and interoperate with the org's
`code-fleet` plugin.

- **Workflows** — `.claude/conventions/workflows.md` defines seven playbooks and when to use each:
  `feature`, `bug`, `refactor`, `spike`, `explore`, `investigate`, `learn`. Each names the phases,
  the interactive gates, and which agent produces which artifact.
- **Skills** — `.claude/skills/` holds the orchestrating skills that auto-drive a workflow.
  All seven workflows are live skills (model-invocable, or run `/feature`, `/bug`, `/refactor`,
  `/spike`, `/explore`, `/investigate`, `/learn`). Each defers to `workflows.md` + `protocol.md`.
  Alongside them, seven **monolith skills** are *symlinked in* from `/c/Repos/monolith/.claude/skills/`
  (`croesus-orm`, `create-{small,medium,large}-tests`, `create-internal-route`, `implement-full-story`,
  `croesus-process-conventions`) — CFF-monolith authoring/testing helpers reused here. They are
  machine-specific links (gitignored, not tracked); (re)create them by running
  `link-monolith-skills.ps1` elevated, then restart Claude Code. The real skills are owned by the
  monolith repo — edit them there, not here.
- **Shared protocol** — `.claude/conventions/protocol.md`: the task directory (`.work/<TICKET-ID>/`),
  canonical artifact filenames, context-gathering, the gate + HALT protocols, per-repo build/test
  commands, and the org git/branch guardrails.
- **Agents** — `.claude/agents/` (dispatch via the Agent tool):
  - read-only: `context-gatherer` (Jira+GitHub intel), `explorer` (code map), `investigator`
    (root cause), `learning-guide` (walkthrough), `reviewer` (plan/code review), `retrospective`.
  - editing: `planner` (→ `plan.md`), `implementer` (build+test, any stack), `cpp-to-csharp-porter`
    (the C++→C# value-provider recipe).
- **Templates** — `.claude/conventions/templates/` (context, plan, review, spike, bug-diagnosis, retro).

Starting a piece of work? Pick the matching workflow in `workflows.md` and follow its phases;
begin every non-trivial task by dispatching `context-gatherer` with the Jira key and/or GitHub ref.
