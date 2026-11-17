# How to run the feature workflow

Goal: take a new capability (report field, endpoint, UI, API change) from a ticket to working, tested
code — and optionally to a PR — through the gated `feature` playbook.

**Prerequisites:** a task description or Jira key; Claude Code open in the workspace. Not for defects
(use [`bug`](fix-a-bug.md)) or pure restructuring (use `refactor`).

## Steps

1. **Invoke it.** `/feature <what you want built>` — include the Jira key if there is one; it becomes
   the task slug and pulls ticket context automatically.

2. **Let context + exploration run.** `context-gatherer` writes `context.md`; `explorer` writes
   `exploration.md`. If Claude asks a clarifying question here, answer it — it only asks when a wrong
   guess would derail the plan.

3. **At the plan gate, read the header first.** `plan.md` opens with `**Status:** … · **Grade:** …`.
   You can only approve-to-build a `ready` + **A/S** plan (the *build bar*). If it's below bar, see
   [How to get a plan past the gate](pass-the-plan-gate.md). Otherwise choose **approve / request
   changes / cancel**.

4. **Let the build run.** For a cross-repo feature, builders run in **pipeline order** —
   C++ analysis → C#/API → Angular UI — one per repo slice named under the plan's `#### <repo>`
   sub-sections. Each builds and runs its tests and writes/updates `build-summary.md`.

5. **At the code gate**, review `review-code.md`'s verdict. Must-fix findings → **request changes**
   (loops back to build, capped at 3 rounds). Clean → **approve**.

6. **Ship (optional).** If you say yes, Claude branches **per touched repo** (`--no-track` from a
   protected ref), commits, `git push -u`, and opens a PR — following the
   [org git rules](../reference/gates-and-protocol.md#branch-commit--ship-rules). Say no and nothing
   is committed.

7. **Retrospective.** `retro.md` proposes durable learnings and doc updates as a checklist. Approve
   the ones worth keeping — Claude won't write memory or edit docs unasked.

## Tips

- **Cross-stack work is at most two branches/PRs** — one in the `monolith` monorepo (C# + C++ together), one in
  `pf-web`. Never commit product code at the workspace root.
- **Delegating to `code-fleet`.** The build+review phases can instead be handed to `/code-fleet:work`
  if you prefer its language packs; the workspace agents add the multi-repo topology awareness and the
  `cpp-to-csharp-porter`. See [`workflows.md` → Relationship to code-fleet](../../.claude/conventions/workflows.md).
- **Value-provider ports** inside a feature are handled by
  [`cpp-to-csharp-porter`](port-cpp-to-csharp.md), not the generic implementer.

## Reference

- Phase table: [Reference: workflows §1](../reference/workflows.md#1-feature)
- Gate mechanics: [Reference: gates & protocol](../reference/gates-and-protocol.md)
- The full skill spec: [`.claude/skills/feature/SKILL.md`](../../.claude/skills/feature/SKILL.md)
