# Reference — Skills

Skills are the model-invocable entry points. Two families live here.

## Workflow skills (owned by this workspace)

Under [`.claude/skills/`](../../.claude/skills/), one per gated/read-only workflow. Each is
model-invocable (Claude picks it from the description) or runnable as a slash command. Each **defers
to** [`workflows.md`](../../.claude/conventions/workflows.md) and
[`protocol.md`](../../.claude/conventions/protocol.md) for the authoritative rules and orchestrates
the [agents](agents.md) via the Agent tool.

| Skill | Slash command | `workflows.md` §  | Details |
|---|---|---|---|
| feature | `/feature` | §1 | [reference](workflows.md#1-feature) · [how-to](../how-to/run-the-feature-workflow.md) |
| bug | `/bug` | §2 | [reference](workflows.md#2-bug) · [how-to](../how-to/fix-a-bug.md) |
| refactor | `/refactor` | §3 | [reference](workflows.md#3-refactor) |
| spike | `/spike` | §4 | [reference](workflows.md#4-spike) |
| explore | `/explore` | §5 | [reference](workflows.md#5-explore) |
| investigate | `/investigate` | §6 | [reference](workflows.md#6-investigate) |
| learn | `/learn` | §7 | [reference](workflows.md#7-learn) |

**Common shape of every workflow skill:**

- `allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash`.
- Dispatches each subagent with the Agent tool, passing its `subagent_type` (the agent name) and a
  prompt of the form:
  ```
  Task directory: .work/<slug>/
  Task: <the task text>
  ```
- **Setup** derives the slug (Jira key if present, else kebab-case of the first ~4 words; confirm if
  guessed) and `mkdir -p .work/<slug>/_signals/`.
- The gated ones (`feature`/`bug`/`refactor`) enforce the [build bar](gates-and-protocol.md#the-plan-gate--the-build-bar)
  at the plan gate and cap build↔review loops at **3**.
- Read-only ones (`explore`/`investigate`/`learn`) have no gates, no build, no ship, no retro.

## Monolith skills (symlinked in)

Seven CFF-monolith authoring/testing helpers are **symlinked** into `.claude/skills/` from
`/c/Repos/monolith/.claude/skills/`. They are machine-specific links — **gitignored, not tracked**
(see [`.gitignore`](../../.gitignore)) — and are (re)created by running `link-monolith-skills.ps1`
elevated, then restarting Claude Code. The real skills are owned by the monolith repo; **edit them
there, not here.**

| Skill | Purpose |
|---|---|
| `croesus-orm` | create/modify Croesus ORM classes (BOs, Repositories, Flex objects, FlexScenarios) |
| `create-small-tests` | xUnit + Moq unit tests for a controller/service/BusinessLogic class |
| `create-medium-tests` | integration tests via `WebApplicationFactory` |
| `create-large-tests` | Python E2E tests for a CFF product route |
| `create-internal-route` | scaffold a new internal API route (clean architecture) |
| `implement-full-story` | full Definition-of-Done: route + all test levels |
| `croesus-process-conventions` | C# conventions for the CroesusProcess codebase |

These are useful *inside* the build phase of a `feature`/`bug` when working in the monolith C# repos.

## Related plugin commands

Not part of this workspace's set, but interoperable — see
[workflows.md → Relationship to code-fleet](workflows.md#relationship-to-code-fleet):
`/code-fleet:work`, `/code-fleet:review`, and the `code-fleet` language-pack agents.
