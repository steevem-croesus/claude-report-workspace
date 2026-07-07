# Plan — <TICKET-ID or task slug>

_Written by planner · Date: <YYYY-MM-DD>_

**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
<!-- Buildable only when Status = ready AND Grade ∈ {A, S}. Scale: F < D < C < B < A < S. -->

## Problem
<one paragraph. Name the target repo(s) and language(s).>

## Requirements coverage
| Requirement (from context / acceptance criteria) | Covered by | Notes |
|---|---|---|
| <req 1> | Step 2 | |
| <req 2> | Step 3 | |
| <req 3> | — | deferred / out-of-scope — <why> |

_Nothing requested may be silently dropped; every row maps to a Step or an explicit deferral._

## Affected areas
- **<repo>** — `path/to/area` — <what changes>
- **<repo>** — `path/to/area` — <what changes>

## Steps
<ordered and concrete. For multi-repo/multi-language work, group under `#### <repo-or-lang>`.>

#### <repo-or-lang A>
1. <step>
2. <step>

#### <repo-or-lang B>
1. <step>

## Tests
- <what to test> — tier: <SmallTests / MediumTests / Vitest / E2E> — traces to Step <n>

## Risks & breaking changes
- <shared-lib ripple, contract/DTO change, migration, C++→C# fidelity risk>

## Decision points
| # | Decision | Options considered | Chosen | Rationale | Status |
|---|---|---|---|---|---|
| 1 | <…> | A / B | A | <why> | resolved |
| 2 | <…> | X / Y | — | <why it needs the user> | needs-user |

_Any `needs-user` row must also appear in Open questions and keeps the plan in `draft`._

## Estimate
_T-shirt size → ideal engineer-time: XS ≤ 2h · S ≈ ½ day · M ≈ 1-2 days · L ≈ 3-5 days · XL > 1 week (split it)._

| Step | Size | Ideal time | Notes |
|---|---|---|---|
| Step 1 — <…> | S | ~½ day | |
| Step 2 — <…> | M | ~1-2 days | |
| Tests (item 5) | S | ~½ day | |

- **Per repo (multi-repo only):** <repo A: M · repo B: S>
- **Overall:** <size> — <range, e.g. 3-5 ideal days>
- **Confidence:** <high / medium / low>
- **What drives it:** <the 1-3 assumptions / unknowns / XL-or-open-question risks that move the number>

## Open questions (resolve at the plan gate)
- <…>
