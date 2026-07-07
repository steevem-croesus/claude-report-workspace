# The design philosophy

This page is about *why* the `.claude/` system exists in this shape. It won't tell you how to run a
workflow — for that, see the [How-to guides](../how-to/). It's here to give you the mental model that
makes everything else feel inevitable rather than arbitrary.

## The problem this solves

The Croesus Xpert report pipeline spans five codebases in three languages: two C++ monoliths
(`CroesusServer`, `ReportServer`), two C# stacks (`ReportFoundations`, `ReportManagerApi`), and an
Angular frontend (`pf-web`). A single piece of report work — say, adding a report field — can ripple
through all of them, in a fixed order, each with its own conventions, branch, and PR.

That combination is exactly where ad-hoc AI assistance goes wrong: it guesses the wrong repo, invents
requirements the ticket never stated, writes code before understanding the existing flow, or ships a
plausible-but-wrong port of subtle C++ date math. The `.claude/` system is a deliberate answer to
that failure mode. Its through-line is:

> **Make the work legible and reversible.** Every step produces a named artifact you can read; every
> risky step waits for your approval before it happens.

## Idea 1 — Match the *shape* of the process to the *kind* of work

There isn't one "do the task" procedure, because the safeguards that matter differ by kind of work:

- A **bug** fix is worthless — even dangerous — without a reproduction and a regression test, so the
  `bug` workflow makes those mandatory and puts *diagnosis* before any patch.
- A **refactor** must not change behaviour, so `refactor` forces characterization tests *before* the
  first edit and requires the build to stay green after *every* step.
- A **spike** exists precisely because the approach is unknown, so its output is a *decision*, its
  prototypes are throwaway, and it's timeboxed.
- **Explore / investigate / learn** don't change code at all, so they carry no gates and stay cheap.

Seven workflows, each encoding the discipline that its kind of work actually needs. This is why
"[choosing a workflow](../how-to/choose-a-workflow.md)" is the first real decision — the workflow
*is* the safeguard.

## Idea 2 — One artifact per phase, on disk

Each phase writes exactly one file into `.work/<slug>/` (`context.md`, `exploration.md`, `plan.md`,
`build-summary.md`, `review-code.md`, `retro.md`, …). This is not bookkeeping for its own sake:

- **It makes the reasoning inspectable.** You can read the plan before any code is written, and the
  review before you approve shipping.
- **It survives across sessions.** Because the directory lives at the workspace root (not inside a
  product repo), a task can be picked up later — the trail is still there.
- **It keeps the product repos clean.** Nothing about the *process* leaks into the code repos.

See [Reference: the task directory](../reference/task-directory.md) for the full artifact list.

## Idea 3 — Gates put a human at the irreversible moments

Reading code, mapping it, and planning are all reversible — you can throw the artifact away. Writing
code, and especially *shipping* it, are not. So the workflows stop for your approval at exactly two
universal points — after the **plan** and after the **build+review** — and nowhere gratuitously in
between. This is the subject of its own page: [gates & the build bar](gates-and-the-build-bar.md).

## Idea 4 — Narrow agents, each with one job

Rather than one agent that does everything, the work is split across
[nine specialists](../reference/agents.md): a locator, a root-cause analyst, a planner, a builder, a
reviewer, and so on — several of them strictly read-only. A terse adversarial reviewer that only
reviews produces better reviews than a generalist that also wrote the code. Why this matters is
discussed in [the orchestrator & agent model](orchestrator-and-agents.md).

## Idea 5 — Defer to local authority

Generic advice loses to the repo in front of you. The whole system is built to *defer*: skills defer
to `workflows.md` + `protocol.md`; agents defer to each repo's own `CLAUDE.md` /
`copilot-instructions.md`; the C++→C# port defers to `copilot-instructions.md`'s recipe. The
`.claude/` files deliberately say "cite and follow them — do not restate their rules," so there's one
source of truth for each thing. (These `docs/` follow the same principle: they explain and index the
`.claude/` files rather than duplicating them — see
[how to keep docs in sync](../how-to/keep-docs-in-sync.md).)

## What this buys you

- You can trust that a `bug` fix has a real regression test, and a `refactor` didn't change behaviour.
- You see the plan — with its risks, estimate, and honest grade — *before* code exists.
- Multi-repo work respects each repo's conventions and lands on separate branches/PRs, as the org's
  git rules require.
- The knowledge doesn't evaporate: every gated workflow ends with a retrospective proposing durable
  learnings.

## What it deliberately is *not*

- **Not autonomous.** It's gated on purpose; it asks rather than guessing past a real fork.
- **Not a replacement for the org's `code-fleet` plugin** — it interoperates with it (the build/review
  phases can be delegated to `/code-fleet:work`). It adds what the fleet lacks: the report topology
  awareness, the `cpp-to-csharp-porter`, and the read-only understanding roles.
