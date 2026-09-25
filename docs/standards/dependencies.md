# Dependency Standard

## Purpose

This document defines how this workspace selects, locks, scans, and updates third-party
dependencies.

> **Relation to the development methodology.** This standard is this project's elaboration
> of methodology [C2 – Beroendehantering, paketkällor & signering](../methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md).
>
> - Dependencies are **locked** to specific, hash-verified versions (`requirements-lock.txt`,
>   `pip-compile`), not loose version ranges (C2 SKA 3).
> - An **SBOM** is not generated automatically yet — there is no release pipeline
>   (C2 SKA 1, `GAP-C2-SBOM`).
> - **`pip-audit`** on every PR plus **Dependabot alerts** on `main` are the SCA (C2 SKA 2);
>   **Dependabot version-update PRs** are the update routine (C2 SKA 5).
> - **Licence scanning** runs in CI against the allowlist below (C2 SKA 4).
>
> The mechanism decisions (pip-compile, pip-audit, pip-licenses, Dependabot, SBOM) are
> recorded in [`interpretations.md` §5](../methodology-compliance/interpretations.md#5-dependency-tooling-c2).

## Lockfile

- `requirements.in` is the source list of direct pip dependencies (version ranges).
  `requirements-lock.txt` is its `pip-compile --generate-hashes --no-annotate --no-header`
  output — the actual, hash-pinned versions installed.
- `environment.yml`'s `pip:` block is just `-r requirements-lock.txt`; do not add packages
  there directly — add them to `requirements.in` and recompile.
- Only Python itself comes from Conda (`environment.yml`). A genuinely Conda-native
  package, if one is ever needed, is pinned exactly there — everything else belongs in the
  pip lock.
- **To update a dependency:** edit its range in `requirements.in`, run
  `pip-compile --generate-hashes --no-annotate --no-header requirements.in`, and commit
  both files together. CI fails if `requirements-lock.txt` doesn't match what
  `requirements.in` compiles to (drift check), so the lock can never silently go stale.
- A **runtime** dependency of the package is also listed (as a range) in `[project]
  dependencies` in `pyproject.toml` — packaging metadata, kept in step with
  `requirements.in`, which remains the install source of truth.
- **Cross-platform gotcha:** compiling locally on Windows can silently include or exclude
  platform-conditional transitive packages that CI's Linux compile resolves differently
  (`colorama`, needed by pytest on Windows only, is pinned in `requirements.in` for this
  reason). If CI's drift check fails after a Windows-local edit, trust CI's diff over your
  own local output.

## SBOM

- Generate from your CI/CD platform's native dependency-graph export if it has one (GitHub
  does, SPDX format) rather than adding a separate SBOM tool — as part of every deploy,
  uploaded as a build artifact.
- Not generated on every PR/CI run — an SBOM describes what got *deployed*, not every
  candidate change.

## SCA (vulnerability scanning)

- **`pip-audit`** runs against `requirements-lock.txt` in CI's `Dependencies` job on every
  pull request, before merge.
- **Dependabot alerts** and automated security fixes are enabled at the repository level
  (*Settings → Security*, see `docs/development/repo-settings.md` §4); they watch `main`
  after merge.
- Reachability analysis is a criterion for a more capable scanner *if and when one is
  adopted* — not required to start.

## Licence scanning

Checked in CI (`ci.yml`'s `dependencies` job) with `pip-licenses` against the resolved
environment.

The scan runs in a separate virtual environment holding only the locked dependencies, so
the scanning tools themselves are not scanned.

**Allowed licences** — the enforcement copy is the `--allow-only` list in `ci.yml`; keep
the two identical. Checked 2026-09-25 against the 19 locked packages, which use MIT, BSD,
Apache-2.0, `Apache-2.0 OR BSD-2-Clause` and the PSF licence:

```text
Apache Software License
Apache-2.0
Apache Software License; BSD License
Apache Software License; MIT License
Apache-2.0 OR BSD-2-Clause
BSD License
BSD-2-Clause
BSD-3-Clause
BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0
MIT
MIT License
MPL-2.0 AND MIT
Mozilla Public License 2.0 (MPL 2.0)
PSF-2.0
Python Software Foundation License
```

Copyleft licences (GPL, LGPL, AGPL) are deliberately not allowed; MPL-2.0 is the only
weak-copyleft licence on the list.

**This repository's own package** (`accounting-agent`) and the environment's `pip` /
`setuptools` are excluded by name (`--ignore-packages`), not added to the allowlist.

**Exception process:** a dependency whose licence is not on the allowlist fails CI. To add
one:

1. The owner decides whether the licence is acceptable — there is no organisation
   legal function (interpretations §5).
2. Add the licence string to both the list above and `ci.yml` in the same PR that adds the
   dependency, recording in the PR who approved it and when.

## Related

- [`docs/standards/coding.md`](coding.md), [`testing.md`](testing.md), [`git.md`](git.md) —
  the other working conventions.
