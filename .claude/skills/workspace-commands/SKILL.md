---
name: workspace-commands
description: Build, test, coverage, Docker and serve commands for the repos in this workspace (ReportManagerApi, ReportFoundations, CroesusServer, ReportServer, pf-web), plus the per-repo gotchas that make them work. Use when you need to build, test, run coverage on, containerize, or serve any repo under repos/, or when a build/test invocation fails and you need the correct path or flags.
---

# Commands by repo

## ReportManagerApi & ReportFoundations (.NET 8, C#)

Build and test with the standard `dotnet build` / `dotnet test` invocations against
`ReportManagerAPI.sln`.

> **Build from the real monolith path, not the `repos/` symlink** — solution references don't
> resolve through the symlink. Use `/c/Repos/monolith/CFF/Products/ReportManagerApi/`.

```bash
# Code coverage (from the repo dir, needs dotnet-reportgenerator-globaltool)
cd /c/Repos/monolith/CFF/Products/ReportManagerApi && ./show-code-coverage.cmd

# Docker
docker build -t reportmanagerapi repos/ReportManagerApi --no-cache --progress=plain
docker run -d -p 5000:80 --name reportmanagerapi reportmanagerapi
```

- The runnable web project is **`ReportManager.API/ReportManagerAPI.csproj`** (contains `Program.cs`, controllers). The bare `ReportManagerAPI/` folder is a build-output stub — ignore it.
- Test-project naming: `*.SmallTests` (unit, no external deps), `*.MediumTests` (integration). Stack is **xUnit + Moq** (some MSTest present).
- `ReportFoundations` projects each have their own `.sln`/`.csproj` and are also referenced by the API solution; build them the same way.
- Local AWS/auth config lives in `appsettings.Development.json` (queue URL, bucket, `AWSOptions`) and `launchSettings.json` (`AWS_PROFILE`). Requires a reachable Frameworkserver on port 8999.

## CroesusServer & ReportServer (C++, CMake)

Both are built with CMake / Visual Studio (`CroesusServer.sln` / `ReportServer.sln`, each with a
`CMakeLists.txt`). They are generally **read-only sources of truth** for the porting workflow — you
locate and analyze C++ functions here, you don't typically modify them for report tasks. A report
function to port may live in either one, so search both.

- **CroesusServer** — Frameworkserver monolith; report logic under `Src/Report`, `Src/ReportApi`.
  Its `POST_BUILD` step generates `versions.ini` and signs the binary.
- **ReportServer** — the legacy report-generation engine; generation logic under `Src/RGSession`
  (`rgs_report_generation.c`, `gen_engine_info.c`), plus `Src/CmdManager`, `Src/Server`, `Src/gRPC`,
  `Src/XMLRPC`.

## pf-web (Angular 21 + NX)

See `repos/pf-web/CLAUDE.md` for the full command set. Drive everything through `nx` — project names
are not folder paths. The non-obvious one:

```bash
cd repos/pf-web
nx hybrid xpert --backend=http://localhost   # serve against a backend
nx test report                                # test the report domain libs
```
