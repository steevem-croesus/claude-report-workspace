---
name: merge-request
description: Draft and open a meaningful merge request / pull request in the Croesus report workspace. Use when the user asks to "open a PR", "create a merge request", "create an MR", "raise a PR", "open a pull request", or "publish this branch". Detects the product repo + branch, picks the base (Gitflow develop), builds a title + structured body from the actual commits and diff, links the Jira issue, and opens it with gh (GitHub) — one MR per repo, never on the tooling root. Does NOT merge.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# merge-request

Turn a finished branch into a **meaningful merge request** — a title and body a reviewer can act on
without reverse-engineering the diff. This is the sibling of the `git-commit` skill: commit first
(that skill), then open the MR (this one). "MR" and "PR" mean the same thing here; the platform is
**GitHub via `gh`** (a GitLab fallback is noted at the end).

Authoritative rules to follow (cite and obey, don't restate):
- Org git guardrails + branch/ship rules → `.claude/conventions/protocol.md` (§ *Branch, commit & ship rules*).
- Repo topology (tooling root vs symlinked product repos) → root `CLAUDE.md`.
- Each product repo's own `CLAUDE.md` — pf-web enforces Conventional Commits (commitlint); the .NET/C++
  repos follow Gitflow + Conventional Commits (see the migration workspace's `CLAUDE.md`).

---

## 1. Locate the repo + branch — and refuse the wrong targets

An MR targets a **product repo with a remote**, never the workspace-root tooling repo (it has no
remote — a PR there is meaningless). This workspace spans several independent repos behind symlinks
(`repos/pf-web`, `repos/ReportManagerApi`, `repos/ReportFoundations`, `repos/CroesusServer`,
`repos/ReportServer`).

1. Determine which repo the branch/work lives in. If the user didn't say, check the repo the current
   task touched (`.work/<slug>/build-summary.md` lists changed files per repo) and
   `git -C <dir> status`.
2. **One MR per repo.** A cross-repo change (e.g. C#/API + Angular) becomes **separate MRs**, one per
   repo — say so and create each, then cross-link them in their bodies.
3. If the repo is ambiguous, ask once via `AskUserQuestion`.
4. Confirm a remote exists: `git -C <dir> remote -v`. No remote → stop and explain (nothing to open an
   MR against — e.g. the tooling root).

## 2. Preconditions (org guardrails — blocking)

Run inside the target repo (`git -C <dir> …`):

- **Branch is not a protected ref.** `git -C <dir> branch --show-current`; if it's `main`/`master`/
  `develop`/`release/*`/`support/*`, stop — you can't open an MR *from* a protected branch. Offer to
  move the commits to a feature branch first (`git switch -c feature/<jira>-<slug> --no-track <base>`).
- **Upstream isn't a protected ref.** `git -C <dir> rev-parse --abbrev-ref <branch>@{upstream}` — if it
  points at `origin/develop` (etc.), `git -C <dir> branch --unset-upstream <branch>` before pushing, so
  a bare push can't fast-forward a protected branch.
- **Commits exist ahead of the base** (see §3). `git -C <dir> log --oneline <base>..HEAD` must be
  non-empty. If there are uncommitted changes, tell the user to run the `git-commit` skill first.
- **Push the branch** with the destination explicit (never a bare first push):
  `git -C <dir> push -u origin <branch>`.

## 3. Pick the base branch

Gitflow default: **`develop`**. Use `main`/`master` only for `hotfix/*` or `release/*`. Detect the
repo's default (`git -C <dir> remote show origin | grep 'HEAD branch'`) and confirm the intended base
with the user if it's anything other than `develop`. State the base you'll target.

## 4. Understand the change (so the MR is meaningful)

- `git -C <dir> log <base>..HEAD --format='%s%n%b'` — the commits (subjects + bodies) are your best
  raw material; a good MR body synthesises them, it doesn't just relist them.
- `git -C <dir> diff --stat <base>...HEAD` and `git -C <dir> diff <base>...HEAD` — read the actual diff
  to describe *what changed and why*, and to spot anything needing reviewer attention.
- **Jira key**: infer from the branch name (`feature/FOG-9412-…`) or the `.work/<slug>/` slug; read
  `.work/<slug>/context.md` if present for the "why".

## 5. Write the MR

**Title** — Conventional Commits, imperative, ≤ ~72 chars, no trailing period:
`<type>(<scope>): <what the change does>`. For a squash-merged repo (pf-web) the title becomes the
squash commit subject, so make it a clean CC subject. Types: `feat`/`fix`/`refactor`/`perf`/`test`/
`docs`/`build`/`ci`/`chore`.

**Body** — fill only the sections that apply; keep it tight and specific:

```markdown
## Summary
<1-3 sentences: what this delivers and WHY. The reviewer reads this first.>

## Changes
- <area/file>: <what changed>
- <area/file>: <what changed>

## Testing
<what you ran and the result — e.g. `dotnet test …` green (N/N), `nx test …` green, manual steps.
Say "not run" honestly if you didn't.>

## Breaking changes
<API/DTO/contract/ReportFoundations ripple + migration notes — or "None".>

## Linked issues
Closes FOG-9412
<or `Refs FOG-9412` if it doesn't fully resolve it. Cross-repo: link the sibling MRs here.>

## Review notes
<the 1-3 spots to look at first; anything intentionally out of scope.>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

The final footer line is **required** on every MR body. Ground every claim in the real diff/commits —
never invent testing you didn't run or a "Closes" for an issue you can't confirm.

## 6. Confirm, then open

1. Show the user: **target repo + branch → base**, whether it'll be a **draft**, the **title**, and the
   full **body**. For multi-repo, show each MR's plan.
2. Open it (default to **draft** for work still in review; drop `-d` for ready-to-review). Pass the body
   via a file or `$'…'` so newlines survive:
   ```bash
   git -C <dir> push -u origin <branch>
   gh -C <dir> pr create --base <base> --head <branch> --title "<title>" --body-file <path> -d
   # (gh reads the repo from the cwd; use `gh` with `cd <dir> &&` if -C is unsupported by the gh version)
   ```
3. Print the returned **MR URL**. For multi-repo, list all URLs and confirm they cross-link.

## 7. Do not merge, do not approve

Opening the MR is where this skill stops. Never `gh pr merge`, never approve, never change the base of
an existing protected branch. Merging is a human decision.

## GitLab fallback

If the repo's remote is GitLab (not GitHub), use the same title/body with:
`glab mr create --source-branch <branch> --target-branch <base> --title "<title>" --description "<body>"`
(add `--draft` for a draft). Everything else in this skill is identical.

## Guardrails (always)
- Never run org-denied CLIs (`aws`, `terraform`/`tofu`, or wrappers like `assume`/`granted`).
- Never open an MR from/into the tooling-root repo (no remote), and never one MR spanning two repos.
- Never a bare first push; branch from a protected ref only with `--no-track`; never unset-then-track a
  protected ref as upstream.
- Never fabricate testing results or issue links; if nothing is committed ahead of base, say so.
