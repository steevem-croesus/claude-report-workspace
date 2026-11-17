# How to choose a workflow

There are seven. Pick by the *kind* of work, not by the repo. This is the decision table from
[`.claude/conventions/workflows.md`](../../.claude/conventions/workflows.md), which is authoritative.

| If the task is… | Use | Gated? | Changes code? |
|---|---|---|---|
| add/change user-facing or API behaviour | **`feature`** | ✅ | ✅ |
| something is broken / wrong output | **`bug`** | ✅ | ✅ |
| improve structure, keep behaviour identical | **`refactor`** | ✅ | ✅ |
| "should we…?" / unknown approach / evaluate options | **`spike`** | ✅ (decision) | ✗ (throwaway only) |
| "where is / how does X flow?" | **`explore`** | ✗ | ✗ |
| "why did / how did this happen?" | **`investigate`** | ✗ | ✗ |
| "help me understand this area" | **`learn`** | ✗ | ✗ |

## The tricky boundaries

- **`bug` vs `investigate`** — already know it's broken and want it *fixed* → `bug` (it runs
  `investigate`'s diagnosis as its phase 3). Only want to *understand* a behaviour → `investigate`.
- **`explore` vs `investigate`** — `explore` answers *where/what* (a code map). `investigate` answers
  *why/how* and rules out alternatives with git history and logs. `explore` is cheaper; reach for it
  first when you just need to locate things.
- **`feature` vs `refactor`** — new/changed behaviour → `feature`. Same behaviour, better shape →
  `refactor` (it enforces characterization tests *before* any edit).
- **`spike` first?** — if the *approach itself* is unknown (not just the details), run `spike` to
  reach a decision, then feed that decision into a `feature` or `refactor`.

## How to invoke

Type the slash command with your task inline:

```
/feature add a reportFormat query parameter to the download endpoint
/bug RPT-12345
/explore how does a queued report reach S3?
```

Or just describe the task in plain language — Claude matches it to a workflow from the skill
descriptions. Slash commands make the choice explicit; useful when the task sits near a boundary
above.

## What you get either way

Every workflow shares the [protocol](../reference/gates-and-protocol.md): a `.work/<slug>/` task
directory, named agents per phase, and (for the gated ones) interactive **approve / request changes /
cancel** stops you control. See [Reference: workflows](../reference/workflows.md) for the exact phase
list of each.
