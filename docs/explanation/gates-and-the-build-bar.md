# Gates & the build bar

This page explains *why* the gated workflows stop for your approval, and why the plan gate has an
unusual entry condition — the **build bar**. For the mechanics (what buttons you get, how to clear a
sub-bar plan), see the reference and how-to:
[gates & protocol](../reference/gates-and-protocol.md),
[get a plan past the gate](../how-to/pass-the-plan-gate.md).

## Why gate at all?

The workflows draw a line between **reversible** and **irreversible** work:

- *Reversible:* gathering context, mapping code, drafting a plan, reviewing a diff. If it's wrong, you
  discard the artifact and nothing was harmed.
- *Irreversible (or costly to undo):* writing code, and above all committing/pushing/opening a PR.

A gate is placed at each transition from reversible to irreversible: the **plan gate** (before any
code is written) and the **code gate** (before anything can be shipped). Everywhere else the workflow
just proceeds — gating the cheap steps would be friction with no payoff. The principle: *spend the
human's attention where a mistake is expensive to reverse.*

Gates are also where the workflow **refuses to guess**. "approve / request changes / cancel" is a real
fork with real trade-offs — exactly the kind of decision the system hands back to you rather than
inventing an answer for.

## Why the build bar?

Here's the subtler design choice. The plan gate won't even *offer* "approve" unless `plan.md` is
`ready` and graded **A** or **S** (on the scale F < D < C < B < A < S).

The reasoning: **the plan is the contract the builder executes.** A vague plan doesn't fail at the
plan gate — it fails later, silently, when the implementer fills the gaps with guesses. Those guesses
surface as rework at the *code* gate, which is far more expensive (code has been written) and easier
to wave through (it looks done). By refusing to build from a sub-A plan, the system moves the failure
forward to the cheapest place to fix it: the plan, where fixing means editing prose, not code.

So a `draft` or B-grade plan isn't a nuisance — it's the system telling you, early and cheaply, that
something isn't decided yet: an open question, a `needs-user` decision point, or a step so
underspecified the builder would have to guess.

## Why an honest `draft` beats an inflated `ready`

The [`planner`](../reference/agents.md#planner) is explicitly instructed **never to inflate the grade
or flip to `ready` to get past the gate** — an over-graded plan is considered *worse* than an honest
`draft`. And the [`reviewer`](../reference/agents.md#reviewer), in plan mode, treats a wrongly-`ready`
or over-graded plan as a **must-fix**.

Why guard the grade so carefully? Because the entire mechanism depends on the grade being truthful. If
grades could be inflated to unlock the gate, the bar would protect nothing — it would just add a step
where the planner marks its own homework as an A. Making the grade adversarially checked (the reviewer
verifies it) and making dishonesty the *worst* option is what gives "ready + A" its meaning. The bar
is only as good as the honesty of the grade behind it.

## Why let you override it, then?

Because the bar is a *default*, not a cage. Some changes are genuinely trivial and you've already
judged them fine; forcing an A-grade plan for a one-line change would be bureaucracy. So you can
explicitly override and approve a sub-bar plan — but the override is **recorded** in
`_signals/revision-request.md`. The design goal isn't to prevent you from proceeding; it's to make
proceeding-below-bar a *conscious, auditable* act rather than an accident. Absent an explicit
override, the bar holds.

## The loop cap

The code gate's "request changes" can loop back to build, but only **3 times**. This exists so a
build↔review cycle that isn't converging surfaces to you rather than spinning indefinitely — after 3
rounds the workflow stops and reports what's still open. It's the same instinct as the HALT cap:
bounded automation that escalates to a human instead of thrashing.

## The through-line

Every one of these choices — where to gate, the build bar, the grade honesty rules, the override, the
loop cap — comes back to one idea from the [design philosophy](design-philosophy.md): *put the human's
judgement at the expensive, irreversible moments, and refuse to fake progress past them.*
