---
name: git-commit
description: Craft meaningful, convention-respecting git commits in the Croesus report workspace. Use when the user asks to "commit", "commit my changes", "write a commit message", "make a conventional commit", or "commit and split into logical chunks". Detects which repo the changes belong to (the tooling root vs a symlinked product repo under repos/), applies that repo's commit convention (Conventional Commits + commitlint for pf-web, team style for the .NET repos), groups unrelated changes into separate commits, and enforces the org branch/commit guardrails. Does NOT push or open PRs unless explicitly asked.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# git-commit

Turn a working tree full of changes into one or more **meaningful, convention-respecting commits**.
The hard problems here are *which repo* the changes belong to (this workspace spans several separate
git repos behind symlinks) and *which convention* that repo uses. Get those right, write a message
that explains **why**, and never violate the org git guardrails.

Authoritative rules to follow (do not restate — cite and obey):
- Org git guardrails + per-repo commit rules → `.claude/conventions/protocol.md`
  (§ *Branch, commit & ship rules*, § *Guardrails*).
- Repo topology (root repo vs symlinked product repos) → root `CLAUDE.md`.
- Each product repo's own `CLAUDE.md` / `copilot-instructions.md` wins on local convention.

---

## 1. Locate the repo(s) with changes — do this first

This workspace is several git repos, not one:

| Location | What it versions | Commit convention |
|---|---|---|
| workspace **root** (`C:\Repos\claude-report-workspace`) | tooling only: `.claude/`, `docs/`, `CLAUDE.md` (local repo, `main`, no remote) | Conventional Commits (default) |
| `repos/pf-web` | Angular frontend | **Conventional Commits, enforced by commitlint** |
| `repos/ReportManagerApi`, `repos/ReportFoundations` | C# / .NET 8 | team conventions (match recent `git log`) |
| `repos/CroesusServer`, `repos/ReportServer` | C++ | team conventions (usually read-only here) |

Steps:
1. Run `git -C <dir> status --short` in the location the user pointed at. If they didn't say, check
   the **root** and any `repos/<repo>` that the current task touched (a `.work/<slug>/build-summary.md`
   lists changed files per repo — read it if present).
2. **One commit never spans two repos** — they're independent repos. If changes exist in more than
   one, handle each repo as its own commit set and tell the user you're doing so.
3. If it's ambiguous which repo the user means, ask once via `AskUserQuestion`.

## 2. Check the branch — org guardrail (blocking)

Before committing to a **product** repo, run `git -C <dir> branch --show-current`.
- If it's a **protected ref** (`main`, `master`, `develop`, `release/*`, `support/*`), **stop and warn**.
  Product changes should not be committed straight onto a protected branch. Offer to branch first:
  `git -C <dir> switch -c <type>/<slug>-<short-desc> --no-track origin/<protected>` (note `--no-track`,
  per protocol.md), then commit onto that branch.
- The workspace **root** repo is local-only with no remote and no protected-branch policy — a direct
  commit to its `main` is fine.

## 3. Understand the change (so the message is meaningful, not mechanical)

- `git -C <dir> diff` (unstaged) and `git -C <dir> diff --staged` (staged) — **read the actual diff**,
  don't guess from filenames. Understand *what* changed and, more importantly, *why*.
- `git -C <dir> log --oneline -n 10` — match the repo's existing subject style, casing, and scope
  vocabulary. Consistency with the repo beats any generic rule.
- For pf-web, check for `commitlint.config.*` / `.commitlintrc*` and honour its `type-enum` / `scope`
  rules exactly (commitlint will reject a non-conforming message on commit).

## 4. Group into logical commits

One commit = one coherent, self-explaining change. If the working tree mixes unrelated work
(e.g. a bug fix + a docs tweak + a rename), **propose splitting** into separate commits rather than
one grab-bag commit:
- stage selectively by path: `git -C <dir> add <paths>` (or `git -C <dir> add -p` for partial-file
  hunks), commit, repeat;
- keep refactors separate from behavioural changes; keep formatting-only churn out of a logic commit.

Do **not** stage: build output (`bin/`, `obj/`, `dist/`, `.angular/`, `node_modules/`), secrets/`.env`,
or the workspace's `.work/` and `.benchmark/` dirs. If any are already staged or untracked-and-tempting,
flag it.

## 5. Write the message

**Format (Conventional Commits — required for pf-web & the root, recommended everywhere here):**

```
<type>(<scope>): <subject>

<body — why the change, what it affects, any non-obvious reasoning>

<footer — issue refs, BREAKING CHANGE, trailers>
```

- **type**: `feat` · `fix` · `docs` · `refactor` · `perf` · `test` · `build` · `ci` · `chore` ·
  `style` · `revert`. (For a repo that doesn't use Conventional Commits, drop the `type(scope):`
  prefix and match its `git log` style instead.)
- **scope** (optional but preferred): the area touched — e.g. `report`, `spooler`, `docs`, the NX
  project/domain for pf-web, the layer for ReportManagerApi.
- **subject**: imperative mood ("add", not "added"/"adds"), no trailing period, ≤ ~72 chars. Say what
  the change *does*, specifically — not "update files".
- **body** (wrap ~72 cols): explain the **why** and the impact. Skip it only for a truly trivial
  one-liner. This is what makes a commit *meaningful* — a reviewer reads the body to understand intent.
- **footer**:
  - Reference the ticket if there is one — infer the Jira key from the branch name
    (`feature/FOG-9412-…`) or the `.work/<slug>/` slug: `Refs: FOG-9412` (or `Closes:` when it fully
    resolves it).
  - `BREAKING CHANGE: <what and the migration>` for any incompatible change — mandatory for
    ReportFoundations changes that ripple to consumers, or API/DTO contract changes.
  - End with the harness co-author trailer:
    `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
    (It's a standard git trailer; if pf-web's commitlint rejects it, drop it and note that you did.)

**Subject examples (good):**
- `docs(diataxis): add tutorials/how-to/reference/explanation tree for .claude workflows`
- `fix(report): correct YTD start-date for January in GetStartYearFromSelectedYM`
- `refactor(spooler): extract BatchRequestBuilder to share the two generation flows`

**Avoid:** `update code`, `fixes`, `wip`, `misc changes`, a subject that just restates the filename.

## 6. Confirm, then commit

1. Show the user: the target **repo + branch**, the **files** to be staged for this commit, and the
   **full drafted message**. If you're splitting into several commits, show the plan.
2. Commit with a real multi-line message — use repeated `-m` or a heredoc so the body/footer are
   preserved:
   ```bash
   git -C <dir> commit -m "<type>(<scope>): <subject>" -m "<body>" -m "<footer trailers>"
   ```
3. After committing, run `git -C <dir> log -1 --stat` and show it so the user sees exactly what
   landed. If commitlint (a hook) rejected it, read the error, fix the message, retry.

## 7. Do not push (unless asked)

Committing is where this skill stops. **Do not `git push`, create a PR, or touch a remote** unless
the user explicitly asks. If they do want to publish, follow protocol.md: first push is
`git -C <dir> push -u origin <branch>` (never a bare `git push`), and per-repo PRs — or hand off to
the `commit-commands:commit-push-pr` skill / a workflow's gated *ship* step.

## Guardrails (always)
- Never run org-denied CLIs (`aws`, `terraform`/`tofu`, or wrappers like `assume`/`granted`).
- Never let a new branch silently track a protected ref — use `--no-track` when branching from one.
- Never commit across repos in a single commit; never commit secrets or build output.
- If nothing is staged and nothing is changed, say so — don't create an empty commit.
