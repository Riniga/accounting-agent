# B — Skriva kod

First assessment: 2026-09-25 (MVP-001). The codebase is a skeleton (one package, two
modules); several points are "met" mainly because there is little code to get wrong.
Reassess after MVP-002.

---

### `B1` — `Kodkvalitet & clean code`

Methodology chapter: [`kodkvalitet-och-clean-code`](../methodology/b-skriva-kod/kodkvalitet-och-clean-code.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Meaningful, intention-revealing names | met | Reviewed in PR #5. |
| 2 | Single Responsibility per class/module | met | `profile.py` (profile model + loading), `cli.py` (command line). |

**BÖR points we adopt:** complexity thresholds (BÖR 2) — see interpretations §3.

**Project interpretation:** cyclomatic complexity gate — [`interpretations.md#3-formatter-linter-and-complexity-b1-b2`](interpretations.md#3-formatter-linter-and-complexity-b1-b2).

**External dependency:** none. **Follow-up plan:** none needed. **Gap-register rows:** none.

---

### `B2` — `Kodstandard & stil`

Methodology chapter: [`kodstandard-och-stil`](../methodology/b-skriva-kod/kodstandard-och-stil.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | `.editorconfig` in every repo | met | Repository root. |
| 2 | A designated, binding formatter per language | met | Ruff (Python). |
| 3 | Established tools with default configuration | met | Ruff defaults plus a small rule selection. |
| 4 | Enforced in pre-commit and in CI | met | Pre-commit hook plus the required `Ruff` check; shown to block in MVP-001 step 4.2. |
| 5 | Review never comments on pure formatting | met | Formatting is fully automated. |

**Project interpretation:** [`interpretations.md#3-formatter-linter-and-complexity-b1-b2`](interpretations.md#3-formatter-linter-and-complexity-b1-b2).

**External dependency:** none. **Follow-up plan:** none needed. **Gap-register rows:** none.

---

### `B3` — `Arkitektur- och designprinciper på kodnivå`

Methodology chapter: [`arkitektur-och-designprinciper`](../methodology/b-skriva-kod/arkitektur-och-designprinciper.md)

- **Methodology status:** `utkast` (pending: architect review)
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Dependencies point to the domain core, not infrastructure | met | Nothing to violate yet. The rule becomes real in MVP-002, when the book model must not depend on file I/O. |
| 2 | Explicit public surface vs. internals | partial | Private helpers are `_`-prefixed; there is no declared public API (`__all__`) yet. |
| 3 | Module boundaries enforced by tooling | not met | Not needed with two modules. Revisit when MVP-002 adds a domain package. |

**External dependency:** none.
**Follow-up plan:** MVP-002 — introduce the domain/IO split and decide on boundary tooling.
**Gap-register rows:** `GAP-B3-BOUNDARIES`

---

### `B4` — `Datamodellering & databasdesign`

Methodology chapter: [`datamodellering-och-databasdesign`](../methodology/b-skriva-kod/datamodellering-och-databasdesign.md)

- **Methodology status:** `utkast` (pending: architect review of BÖR 7)
- **Platform standing:** `not applicable yet`

No database ([ADR-004](../architecture/decisions/ADR-004-csv-and-markdown-storage.md)). The
spirit of SKA 2–4 (backward-compatible changes, integrity enforced by the store, not only
the app) applies to the CSV/Markdown formats from MVP-002 on. File-format changes need
migration code, and validation must not rely on the agent alone.

**Gap-register rows:** none (reassess in MVP-002).

---

### `B5` — `Dokumentation av kod`

Methodology chapter: [`dokumentation-av-kod`](../methodology/b-skriva-kod/dokumentation-av-kod.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | README: purpose, runnable install/run/test commands, ownership/status | partial | Purpose, owner, status and licence are in place. The commands are added in MVP-001 step 6.1. |
| 2 | Docs updated in the same PR as the change | met | Practised throughout MVP-001. |
| 3 | Significant decisions as ADRs, Nygard format | met | ADR-001–005. |
| 4 | Accepted ADRs never edited; superseded instead | met | |
| 5 | Runnable documentation examples validated automatically | partial | The documented `run` command is exercised end to end by `test_module_entry_point_runs_end_to_end`. The setup commands in `docs/development/` are not validated automatically. |

**External dependency:** none.
**Follow-up plan:** MVP-001 step 6.1 (README commands).
**Gap-register rows:** `GAP-B5-README`, `GAP-B5-DOCTEST`
