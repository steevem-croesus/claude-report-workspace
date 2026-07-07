# How to port a C++ report function to C#

Goal: reimplement a C++ report function (from `CroesusServer` **or** `ReportServer`) as a C#
`IValueProviderParameter` in `ReportManagerApi`. This is the workspace's most recurring cross-repo
task, and it has a dedicated agent: [`cpp-to-csharp-porter`](../reference/agents.md#cpp-to-csharp-porter).

**Authoritative recipe:** [`repos/ReportManagerApi/copilot-instructions.md`](../../repos/ReportManagerApi/copilot-instructions.md).
This guide orients you; that file is the source of truth for folders and registration.

## When to use which entry point

- **Inside a feature/bug** — the `feature`/`bug` workflow automatically dispatches
  `cpp-to-csharp-porter` (instead of the generic `implementer`) when a plan step is a value-provider
  port. You don't do anything special.
- **Standalone** — dispatch the agent directly (or describe the port task) when the whole job *is* a
  port.

## What the porter does (so you can check its work)

1. **Finds & confirms the C++ source.** Searches **both** `repos/CroesusServer/Src/` and
   `repos/ReportServer/Src/` — the function may live in either — reads it fully, and states its
   semantics (inputs, outputs, edge cases, and especially date/period math) with the `repo/path:line`
   it came from.

2. **Chooses the injected dependencies from C++ signals:**

   | C++ signal | Inject |
   |---|---|
   | `PREF_` / preference / config | `IPreferencesRepository` |
   | `PARAM_` / parameter | `IReportCommandAndQueryContextRepository` |
   | date / period logic | `IParameterDateValueService` / `IDateTimeService` |
   | repartitions | `IRepartitionRepository` |
   | transactions | `ITransactionsRepository` |
   | industry codes | `IIndustryCodeRepository` |
   | indexes | `IIndexesRepository` |

3. **Creates the parameter class** `<FunctionName>Parameter` with a `ProvideValue` method, placed in:
   - general/pre: `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/`
   - date-related: `.../Parameters/Date/`

4. **Registers it — alphabetically —** in the matching executer:
   - pre: `PreParamEntryValueProviderFunctionsExecuter.cs`
   - post: `PostParamEntryValueProviderFunctionsExecuter.cs`
   as `implementationsDictionary["<FunctionName>"] = () => new <FunctionName>Parameter();`

5. **Adds date helpers** to `IDateTimeService` (Domain) + `DateTimeService.cs` if new date ops are
   needed.

6. **Writes tests (mandatory)** mirroring `GetStartYearFromSelectedYMParameter` style, covering the
   C++ edge cases — parameter tests under `ReportManagerAPI.Infrastructure.SmallTests/...` and
   date-service tests in `ReportManagerAPI.Domain.SmallTests/Services/DateTimeServiceTests.cs`.

7. **Builds and tests** before returning:
   `dotnet build repos/ReportManagerApi/ReportManagerAPI.sln` + `dotnet test <the *.SmallTests project>`.

## What to double-check as the reviewer/approver

- **Fidelity.** The C# must match the C++ semantics. Any deliberate divergence must be called out
  explicitly with the source line — the [`reviewer`](../reference/agents.md#reviewer) flags silent
  divergences as must-fix.
- **Right repository interface injected** (per the table above).
- **Alphabetical registration** in the correct pre/post executer.
- **Edge cases covered** — especially date/period boundaries (year rollover, fiscal vs calendar).

If the porter can't find the function, the semantics are ambiguous, or the correct repository
interface is unclear, it **HALTs** and asks rather than guessing financial/date logic.

## Reference

- Mapping cues also summarised in the root [`CLAUDE.md`](../../CLAUDE.md).
- Agent spec: [`.claude/agents/cpp-to-csharp-porter.md`](../../.claude/agents/cpp-to-csharp-porter.md)
