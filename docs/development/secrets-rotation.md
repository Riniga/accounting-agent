# Secrets Rotation Runbook

## Purpose

What to do when a secret is exposed (C4 SKA 4–5). The project has no deployment and no
stored CI secrets today, so the template's OIDC/identity-federation migration runbook
(C4 SKA 2) was removed; if a deploy or a stored credential is ever introduced, write that
runbook for the actual platform then.
See [`docs/methodology-compliance/interpretations.md`](../methodology-compliance/interpretations.md)
for the tool decisions you make along the way.

## If a secret is exposed

An exposed secret (committed, leaked in a log, visible in a screen-share) is **compromised
immediately** — treat it as such regardless of repo visibility or how briefly it was
exposed (C4 SKA 4).

1. **Rotate first, always.** Generate a new value and revoke the old one at the source —
   your cloud provider's portal/CLI, the relevant provider's dashboard for anything else
   (an LLM API key, a GitHub PAT, …). Do this before anything else below.
2. **Update the CI secret** (e.g. GitHub → *Settings → Secrets and variables → Actions*) to
   the new value. Confirm the next workflow run picks it up.
3. **History cleanup is second, not first, and not sufficient alone** (C4 SKA 5) — a secret
   that was ever pushed is compromised the moment it left the local machine, whether or not
   it's later removed from history. Clean history anyway, so it doesn't keep showing up in
   clones/forks/CI logs, using `git filter-repo` or GitHub's own guidance:
   <https://docs.github.com/articles/removing-sensitive-data-from-a-repository>.
4. **Record what happened** — which secret, when, how it was exposed, the rotation
   timestamp — somewhere durable (a PR description, an incident note). Not because every
   repo runs a formal CVD process (that may be central to your organisation, see
   [C3](../methodology/c-sakerhet/sarbarhetshantering-patchning-och-cvd.md)), but because
   "what happened and when" is the first thing anyone investigating later will need.

## Related

- [`docs/methodology/c-sakerhet/hantering-av-hemligheter.md`](../methodology/c-sakerhet/hantering-av-hemligheter.md) —
  the methodology chapter this operationalises.
