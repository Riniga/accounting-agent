# Threat Modeling Standard

## Purpose

Lightweight threat modelling for changes with real security impact — a data-flow sketch and
STRIDE's six categories, done in the design phase before code is written (cheapest time to
act on a finding), not a heavyweight annual exercise.

> **Relation to the development methodology.** This standard is this project's elaboration
> of methodology [C1 – Secure coding-principer](../methodology/c-sakerhet/secure-coding-principer.md)
> SKA 4 and BÖR 1. Enforced as a plan-writing habit, not a CI gate —
> threat modelling is a design activity, not something a tool can verify happened correctly.

## When a plan needs one

Per the chapter: "för varje feature eller förändring med betydande säkerhetspåverkan"
(for every feature or change with significant security impact). That's a judgement call the
plan's author makes, not an automated trigger. As a rough guide, consider one when a change:

- Adds or changes **authentication or authorization** logic.
- Adds a **new external-facing surface** (a new endpoint, a new input a user or an external
  system can control).
- Introduces a **new data flow handling sensitive data** (secrets, credentials, personal
  data).
- Changes **trust boundaries** — what a component trusts to be true about its caller or its
  input.

Most day-to-day changes (a bug fix, a doc update, a refactor with the same external
behaviour) do not need one. When in doubt, a two-minute STRIDE pass costs little; skipping
it on something that turns out to matter costs a lot more later.

## How to do it

1. Sketch the data flow: what enters the system, from where, through which component, to
   where it ends up. A few boxes and arrows — a whiteboard photo or an ASCII sketch in the
   plan is enough. No diagramming tool required.
2. For each flow that crosses a trust boundary, ask STRIDE's six questions:

| Category | Question |
|---|---|
| **S**poofing | Can someone pretend to be a user, service, or component they aren't? |
| **T**ampering | Can data be modified in transit or at rest without detection? |
| **R**epudiation | Can an action be taken without leaving a trace of who did it? |
| **I**nformation Disclosure | Can data reach someone who shouldn't see it? |
| **D**enial of Service | Can the flow be used to make the system unavailable? |
| **E**levation of Privilege | Can this flow be used to gain access beyond what was granted? |

3. For anything with a real answer (not "no, because X"), note it as a risk in the plan's
   "Risks / open questions" section, with a decision: fix it now, accept it with a reason,
   or track it as a follow-up.

## Where it lives

Put the sketch and the STRIDE pass directly in the relevant `docs/plans/*.plan.md`'s
"Risks / open questions" section — plans already have a natural home for this, no separate
document or process to maintain. A short "Threat model (STRIDE)" subheading makes it easy to
find later.

## Example

```text
Data flow: Admin UI → PipelineRunner.run_async() → subprocess (local) OR
           GitHub Actions dispatch (remote) → Azure Storage (publish)

- Spoofing: the dispatch path authenticates with a GitHub PAT (ADMIN_DISPATCH_TOKEN);
  anyone with Admin UI access can trigger a real deploy. Accepted — Admin itself requires
  login (see its auth setup); not re-litigated here.
- Tampering: N/A — no user-supplied data reaches the dispatched workflow's inputs.
- Repudiation: the GitHub Actions run log records who/what dispatched it. Sufficient.
- Information Disclosure: the PAT is an Actions secret, never logged (see coding.md
  "Security" — no secret logging). Confirmed no log line echoes it.
- Denial of Service: N/A — not evaluated for this iteration.
- Elevation of Privilege: the dispatch token's scope is limited to this repo's workflows,
  not org-wide. Confirmed in the PAT's GitHub settings.
```

## Related

- [`docs/standards/coding.md`](coding.md) "Security" — the baseline secure-coding rules this
  complements.
- [`docs/methodology-compliance/interpretations.md`](../methodology-compliance/interpretations.md) —
  record the C1 SAST/DAST tool-position decision here alongside this standard.
