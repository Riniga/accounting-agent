# Repository settings (owner-applied)

Some methodology requirements are **GitHub repository settings**, not files in the repo.
They cannot be committed — the repository owner applies them in the GitHub UI (or via
`gh api`). This document is the exact checklist.

Record the adoption decision as an ADR. Track each setting's status as a gap-register row
in [`../methodology-compliance/gap-register.md`](../methodology-compliance/gap-register.md)
until it's applied — this project used `GAP-D2-BRANCHPROTECT`, `GAP-F1-ENFORCE`, and
`GAP-E2-GREENMAIN` as a worked example.

> **Status: not yet applied — fill in when you apply this to a real repo.** When you set
> this up, record here (with the date and any ruleset/rule id) exactly what you applied and
> any deliberate deviation (e.g. required-approval count while the project has a single
> maintainer — document that as an exception, same pattern as
> [`exceptions.md`](../methodology-compliance/exceptions.md), and track it as its own gap
> row until a second reviewer exists to close it).

---

## 1. Branch protection on `main` — required

Applied as a **repository ruleset** (Settings → Rules → Rulesets), targeting
`~DEFAULT_BRANCH`. A classic branch-protection rule is an equivalent alternative.

| Setting | Value | Methodology basis |
|---------|-------|-------------------|
| Require a pull request before merging | **on** | [D2](../methodology/d-kvalitetssakring/kodgranskning.md) SKA 1, [F1](../methodology/f-ai-samarbete/riktlinjer-for-ai-assisterade-verktyg.md) SKA 1 |
| Required approvals | **1** (or **0**, documented as an exception, only while a single maintainer genuinely cannot get a non-author review — raise to 1 the moment a second reviewer exists) | D2 SKA 2 |
| Dismiss stale pull request approvals when new commits are pushed | **on** | D2 SKA 4 |
| Require conversation resolution before merging | **on** | D2 |
| Require review from Code Owners | **on once a `CODEOWNERS` file exists** | D2 SKA 3 |
| Require status checks to pass before merging | **on** — every named CI job you want to gate (e.g. `Run tests`, `Ruff`, `SAST`, `Secret scan`) | [E2](../methodology/e-leverans/ci-cd-och-automatisering.md) SKA 1 |
| Require branches to be up to date before merging (`strict`) | **on** | E2 SKA 4 (keeps `main` green) |
| Block force pushes (`non_fast_forward`) | **on** | [git.md](../standards/git.md) |
| Block branch deletion | **on** | git.md |

**Direct updates to `main` are prohibited by the ruleset.** Enforced by "Require a pull
request before merging"; the **bypass list must remain empty** — no roles, teams, apps, or
deploy keys, and org/repo admins included (`bypass_actors: []`,
`current_user_can_bypass: never`). A guardrail an admin or a bot token can skip is not a
technical guardrail (methodology F1 SKA 1, 6; A2 SKA 6).

Optional extra hardening (not required by the methodology, sensible with AI-assisted
commits): **Require approval of the most recent reviewable push** — the person who pushed
the last commit cannot be its sole approver.

### Status-check names

Each CI job's `name:` field **is** its status-check context — that's what you search for
and mark "required" in the ruleset. If a check doesn't appear in the search box, it hasn't
run on a PR yet: open one against `main`, let CI run once, then add the check.

Order jobs fail-fast: a fast lint/format job first (`needs:` chain), with more expensive
jobs (a full test run, SAST, a Conda-based environment) gated behind it rather than running
in parallel — see this repo's own `.github/workflows/ci.yml` for the pattern.

### Apply / inspect via `gh`

```bash
# inspect the current ruleset
gh api repos/<owner>/<repo>/rulesets
gh api repos/<owner>/<repo>/rulesets/<ruleset-id>

# a classic branch-protection alternative
gh api -X PUT repos/<owner>/<repo>/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f 'required_pull_request_reviews[required_approving_review_count]=1' \
  -F 'required_pull_request_reviews[dismiss_stale_reviews]=true' \
  -F 'required_status_checks[strict]=true' \
  -f 'required_status_checks[checks][][context]=Run tests' \
  -F 'enforce_admins=true' \
  -F 'restrictions=' \
  -F 'allow_force_pushes=false' \
  -F 'allow_deletions=false'
```

## 2. Access for AI-tool / bot accounts

If any AI tool (e.g. a Copilot coding-agent identity) is granted write access to the repo:

- It is subject to branch protection like any other actor (section 1, "do not allow
  bypassing").
- It works via branches and pull requests only — never a direct push or a self-merge to
  `main` (F1 SKA 1).
- Access is tied to the organisation's identity management, not a standalone per-tool
  account (A2 SKA 5).

## 3. When a second reviewer exists

- **Raise "Required approvals" back to 1** (if it was lowered) and add a `CODEOWNERS` file
  with **Require review from Code Owners** enabled. This closes the single-maintainer
  exception and its gap-register row.
- Enable **Require linked issues / work items** (or the equivalent branch policy on
  whichever platform hosts the repo) —
  [E1](../methodology/e-leverans/versionshantering-och-branchstrategi.md) SKA 6.

---

## 4. Dependency security (methodology C2)

> **Status: not yet applied — fill in when you apply this to a real repo.** Three
> repository-level security settings, applied via `gh api` (equivalent to
> *Settings → Security*):
>
> - **Dependency graph** — a prerequisite for the two settings below; some platforms
>   enable it automatically when you enable either of them.
> - **Dependabot alerts** (`PUT /repos/.../vulnerability-alerts`) — the C2 SKA 2 SCA
>   baseline.
> - **Dependabot automated security fixes**
>   (`PUT /repos/.../automated-security-fixes`) — opens a PR automatically when an alert has
>   a known fix.
>
> `.github/dependabot.yml` (version-update PRs, C2 SKA 5) is committed code, not a repo
> setting, so it isn't listed here — see `docs/standards/dependencies.md`.

---

## Owner checklist

- [ ] Branch protection on `main` applied per section 1 — record the ruleset id and date.
- [ ] Bypass list confirmed empty (`bypass_actors: []`, admins included).
- [ ] Required approvals set correctly (1, or 0 as a documented, tracked exception for a
      genuinely single-maintainer project).
- [ ] Each CI job you want to gate added to the required status checks.
- [ ] Any AI-tool write access reviewed per section 2 (or: no AI tool has write access).
- [ ] **When a second reviewer joins:** raise required approvals to 1, add `CODEOWNERS`
      (section 3).
- [ ] *(optional)* Enable "Require approval of the most recent reviewable push".
- [ ] Dependency graph, Dependabot alerts, and automated security fixes enabled per
      section 4.
