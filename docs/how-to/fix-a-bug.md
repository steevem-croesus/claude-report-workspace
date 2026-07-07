# How to fix a bug

Goal: fix a defect through the `bug` workflow, which enforces one hard rule:

> **No fix ships without a reproduction and a regression test** that fails *before* the fix and passes
> *after*. Diagnosis is mandatory and separate from the fix — you don't patch symptoms.

**Prerequisites:** a bug report or Jira key describing wrong/broken behaviour.

## Steps

1. **Invoke it.** `/bug <symptom or Jira key>` — e.g. `/bug FOG-9412` or `/bug the year-to-date
   parameter returns last year's start date for January reports`.

2. **Context.** `context-gatherer` captures the report, repro steps, and any linked PRs → `context.md`.

3. **Reproduce — this comes before diagnosing.** Claude establishes a reproduction, preferring a
   **failing test** that captures the defect; otherwise documented repro steps. Status is recorded in
   `bug-diagnosis.md` as reliable / intermittent / not-yet-reproduced.
   - If it **can't** reproduce, it stops and asks you (via a prompt) for more detail or permission to
     proceed on best evidence — it won't blindly patch.

4. **Diagnose.** `investigator` works the evidence (code, `git log`/`git blame`, tickets, logs), forms
   hypotheses, refutes them adversarially, and appends the **root cause + confidence** to
   `bug-diagnosis.md`. It distinguishes the *trigger* from the underlying *cause*.

5. **Plan the fix.** `planner` writes a minimal, fix-scoped `plan.md` whose Tests section **includes
   the regression test**. Same [build bar](pass-the-plan-gate.md) applies at the plan gate — small
   fixes may grade quickly, but the bar still holds unless you explicitly override it.

6. **Build the fix.** `implementer` (or [`cpp-to-csharp-porter`](port-cpp-to-csharp.md) if the fix is
   in a port) writes the fix **and** the regression test, then builds and runs tests.

7. **Verify + review.** Claude re-runs the failing test/repro to confirm it's gone, then `reviewer`
   checks the diff — and specifically that the regression test covers the **root cause, not just the
   symptom**. Code gate: **approve / request changes / cancel** (changes loops back, cap 3).

8. **Ship (optional)** and **retrospective.** `retro.md` **must** record the *class* of root cause so
   similar bugs are caught earlier next time. Approve the proposed learnings you want kept.

## Common pitfalls

- **Skipping reproduction because "the cause is obvious."** The workflow won't let you — and "obvious"
  causes are often the trigger, not the root cause.
- **A regression test that passes even without the fix.** The reviewer flags this; the test must fail
  before the fix.
- **Confusing this with [`investigate`](../reference/workflows.md#6-investigate).** If you only want to
  *understand* why something happened without fixing it, use `investigate`.

## Reference

- Phase table: [Reference: workflows §2](../reference/workflows.md#2-bug)
- The full skill spec: [`.claude/skills/bug/SKILL.md`](../../.claude/skills/bug/SKILL.md)
