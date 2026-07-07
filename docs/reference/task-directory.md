# Reference — The task directory & workspace layout

## `.work/<slug>/`

Every non-trivial workflow run creates a per-task directory at the **workspace root**:
`C:\Repos\claude-report-workspace\.work\<slug>\`.

- **slug** = the Jira key when detected (`FOG-9412`, `CFF-1234`); otherwise the kebab-case of the
  first ~4 words of the task. Re-running the same task **reuses** the directory.
- It lives at the workspace root on purpose: it does **not** pollute the symlinked repos and it
  survives across sessions. It is **gitignored** here (`/.work/` in [`.gitignore`](../../.gitignore)).

### Canonical artifact filenames (one artifact = one file)

| File | Written by | Purpose |
|---|---|---|
| `task.md` | orchestrator | the raw task text |
| `context.md` | [context-gatherer](agents.md#context-gatherer) | Jira + GitHub intel brief |
| `exploration.md` | [explorer](agents.md#explorer) | code map for the task |
| `investigation.md` | [investigator](agents.md#investigator) | root-cause analysis |
| `bug-diagnosis.md` | investigator | reproduction + root cause for a bug |
| `learning-notes.md` | [learning-guide](agents.md#learning-guide) | walkthrough / mental model |
| `spike.md` | orchestrator + explorer | spike findings + recommendation |
| `plan.md` | [planner](agents.md#planner) | implementation plan (gates the build) |
| `review-plan.md` | [reviewer](agents.md#reviewer) | plan-gate findings |
| `build-summary.md` | [implementer](agents.md#implementer) / [porter](agents.md#cpp-to-csharp-porter) | what was built + build/test results |
| `review-code.md` | reviewer | code-gate findings |
| `retro.md` | [retrospective](agents.md#retrospective) | retrospective + proposed learnings |
| `clarifications.md` | orchestrator | Q→A resolved before planning |

### The `_signals/` subdirectory

Control-flow breadcrumbs the orchestrator writes when looping a phase:

| File | Written when |
|---|---|
| `_signals/revision-request.md` | you choose **request changes** at a gate (feedback recorded verbatim; also records an explicit build-bar override) |
| `_signals/resume.<agent>.md` | an agent HALTs and you answer its question (the answer, so the agent can resume) |

**Templates** for the artifacts live in
[`.claude/conventions/templates/`](../../.claude/conventions/templates/): `context.md`, `plan.md`,
`review.md`, `spike.md`, `bug-diagnosis.md`, `retro.md`.

## Workspace layout

This workspace is a thin root holding symlinks to the real product checkouts. Full topology is in the
root [`CLAUDE.md`](../../CLAUDE.md); in brief:

```
C:\Repos\claude-report-workspace\
├── .git/                 ← this root is a small git repo (docs/, .claude/, CLAUDE.md tracked)
├── .claude/              ← agents, skills, conventions (the subject of these docs)
├── docs/                 ← you are here
├── .work/                ← per-task directories (gitignored)
├── .benchmark/           ← local eval fixtures (gitignored)
├── CLAUDE.md
├── link-monolith-skills.ps1
└── repos/                ← SYMLINKS to the real repos (gitignored; each its own git repo)
    ├── CroesusServer     → C++ Frameworkserver monolith
    ├── ReportServer      → C++ report-generation engine
    ├── ReportFoundations → C# shared reporting libs
    ├── ReportManagerApi  → C# / .NET 8 report API
    └── pf-web            → TypeScript / Angular 21 + NX frontend
```

> **Two levels of git.** The workspace root is its own repo (tracking `.claude/`, `docs/`, `CLAUDE.md`,
> etc.). Each symlink under `repos/` points at a *separate* repo on its own branch and remote. Commits
> and PRs for product changes happen **inside the specific symlinked repo**, never at the root — see
> the [branch/commit/ship rules](gates-and-protocol.md#branch-commit--ship-rules).
