# Dependency Standard

## Purpose

This document defines how this workspace selects, locks, scans, and updates third-party
dependencies.

> **Relation to Skanskas utvecklingsmetodik.** This standard is this project's elaboration
> of methodology [C2 – Beroendehantering, paketkällor & signering](../methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md).
>
> - Dependencies are **locked** to specific, hash-verified versions (`requirements-lock.txt`,
>   `pip-compile`), not loose version ranges (C2 SKA 3).
> - An **SBOM** is exported on every deploy (C2 SKA 1).
> - **Dependabot alerts** are the SCA baseline (C2 SKA 2); **Dependabot version-update PRs**
>   are the update routine (C2 SKA 5).
> - **Licence scanning** runs in CI against the allowlist below (C2 SKA 4).
>
> Record the mechanism decisions you make (lockfile tool, SBOM source, SCA/licence-scan
> tool, and why) in
> [`interpretations.md`](../methodology-compliance/interpretations.md) — this project chose
> `pip-compile` (not `conda-lock`/`uv`), GitHub's native SBOM export, and `pip-licenses`
> (not `dependency-review-action`, which needs GitHub Advanced Security this project's
> private-repo tier didn't have confirmed) as a worked example.

## Lockfile

- `requirements.in` is the source list of direct pip dependencies (version ranges).
  `requirements-lock.txt` is its `pip-compile --generate-hashes --no-annotate --no-header`
  output — the actual, hash-pinned versions installed.
- `environment.yml`'s `pip:` block is just `-r requirements-lock.txt`; do not add packages
  there directly — add them to `requirements.in` and recompile.
- Genuinely Conda-native packages are pinned exactly in `environment.yml` itself (same
  pattern as `ruff==0.16.6`) — not part of the pip lock. Keep this list as short as
  possible; most things belong in the pip lock instead.
- **To update a dependency:** edit its range in `requirements.in`, run
  `pip-compile --generate-hashes --no-annotate --no-header requirements.in`, and commit
  both files together. CI fails if `requirements-lock.txt` doesn't match what
  `requirements.in` compiles to (drift check), so the lock can never silently go stale.
- Per-app `pyproject.toml` `dependencies` (version ranges) are unchanged by this — they are
  packaging metadata for each app, not this repo's own install source of truth.
- **Cross-platform gotcha:** compiling locally on Windows can silently include or exclude
  platform-conditional transitive packages that CI's Linux compile resolves differently
  (this project hit it twice — see the example comment in `requirements.in`). If CI's
  drift check fails after a Windows-local edit, trust CI's diff over your own local output.

## SBOM

- Generate from your CI/CD platform's native dependency-graph export if it has one (GitHub
  does, SPDX format) rather than adding a separate SBOM tool — as part of every deploy,
  uploaded as a build artifact.
- Not generated on every PR/CI run — an SBOM describes what got *deployed*, not every
  candidate change.

## SCA (vulnerability scanning)

- Dependabot alerts (GitHub-native) are a reasonable baseline — enabled at the repository
  level (*Settings → Security*), not something this repo's own workflows configure. Check
  whether it's actually available for your repo's plan/tier before assuming it — a private
  repo without GitHub Advanced Security may not have it (this project's didn't; confirmed
  via the API, not assumed).
- Reachability analysis is a criterion for a more capable scanner *if and when one is
  adopted* — not required to start.

## Licence scanning

Checked in CI (`ci.yml`'s `dependencies` job) with `pip-licenses` against the resolved
environment.

**Allowed licences** — start from a real, measured baseline (run `pip-licenses` against
your actual resolved environment and read what it reports), not a copied list:

```text
MIT
BSD-3-Clause
Apache-2.0
<...add what your own dependencies actually use...>
```

This is not a general-purpose OSS licence policy — it should reflect what your own
dependencies actually use, checked and dated. Decide deliberately whether to allow copyleft
licences (GPL, AGPL, etc.); this project's example deliberately excluded them beyond
MPL-2.0.

**This workspace's own packages** report `UNKNOWN` to `pip-licenses` (no licence
classifier — they're internal, not published) and should be excluded from the check by
name (`--ignore-packages`), not added to the allowlist.

**Exception process:** a dependency whose licence is not on the allowlist fails CI. To add
one:

1. Confirm with your organisation's legal/procurement function that the licence is
   acceptable for this project's use (an external process, not owned by this repo).
2. Add the licence string to the allowlist above in the same PR that adds the dependency,
   with a one-line comment recording who confirmed it and when.

## Related

- [`docs/standards/coding.md`](coding.md), [`testing.md`](testing.md), [`git.md`](git.md) —
  the other working conventions.
