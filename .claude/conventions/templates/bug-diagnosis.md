# Bug diagnosis — <TICKET-ID or task slug>

_Written by orchestrator (repro) + investigator (root cause) · Date: <YYYY-MM-DD>_

## Symptom
<what's observed vs expected, with the exact error/output and where it appears>

## Reproduction
- **Steps / test:** <the minimal repro, or the failing test that now exists>
- **Repro status:** <reliably reproduced / intermittent / not yet reproduced>
- **Environment:** <repo, branch, data conditions>

## Evidence
- `repo/path:line` — <what it shows>
- `commit <sha>` — <what changed and when> (`git blame` / `git log -S`)
- `JIRA <key>` / `PR #n` — <relevant history>
- logs — <relevant lines>

## Hypotheses
| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| 1 | <…> | confirmed / refuted | <…> |
| 2 | <…> | refuted | <…> |

## Root cause
<the most-supported cause — distinguish the trigger from the underlying cause and contributing factors>

- **Confidence:** <high / medium / low>
- **Where a fix belongs:** `repo/path` — <but not the fix design; that's the plan>

## Open questions
- <what's still unknown, if any>
