# Secrets Rotation & OIDC Migration Runbook

## Purpose

Two runbooks in one document: what to do when a secret is exposed (C4 SKA 4–5), and how to
migrate deploy authentication from a stored credential to OIDC/workload identity (C4 SKA 2).
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

## OIDC migration for deploy authentication (worked example — adapt or remove)

**Status: documented, not executed, in the project this example is drawn from.** That
project's deploy workflow authenticated to Azure with a stored service-principal credential
(a full `az ad sp create-for-rbac --sdk-auth` JSON blob in one GitHub Actions secret). C4
SKA 2 asks for identity federation instead, eliminating the stored secret entirely. The
commands below are real and were verified to be correct, but deliberately not applied,
because **deploys on merge to `main` were automatic**: switching the workflow files to
OIDC before the federated credential actually existed would have broken the very next
deploy. If your own deploy trigger isn't automatic, you may be able to do this in one PR
instead of in the careful sequence below.

**Do these in order if your deploys are automatic. Do not skip the manual-dispatch
verification step.**

1. **Find the existing app registration's client (app) ID:**

   ```bash
   az ad app list --display-name "<your-deploy-app-registration-name>" --query "[].appId" -o tsv
   ```

2. **Create a federated credential** trusting GitHub's OIDC issuer for this repo, scoped to
   `main` (or whichever branch/environment your deploy workflow(s) actually run against):

   ```bash
   az ad app federated-credential create \
     --id <APP_ID_FROM_STEP_1> \
     --parameters '{
       "name": "github-actions-main",
       "issuer": "https://token.actions.githubusercontent.com",
       "subject": "repo:<owner>/<repo>:ref:refs/heads/main",
       "audiences": ["api://AzureADTokenExchange"]
     }'
   ```

3. **Add three new, small GitHub Actions secrets** (Settings → Secrets and variables →
   Actions) — replacing the one large JSON blob with individually-scoped, non-sensitive-by-
   themselves identifiers (none of these alone grants access without the federation trust
   above and a live GitHub Actions run from this specific repo/ref):
   - `AZURE_CLIENT_ID` — the app ID from step 1.
   - `AZURE_TENANT_ID` — `az account show --query tenantId -o tsv`.
   - `AZURE_SUBSCRIPTION_ID` — `az account show --query id -o tsv`.

4. **Edit every workflow that logs into Azure, together, in the same PR** — half-migrated
   is worse than not migrated:

   ```yaml
   permissions:
     id-token: write # required for OIDC token issuance
     contents: read

   # ...

   - name: Azure login
     uses: azure/login@v2
     with:
       client-id: ${{ secrets.AZURE_CLIENT_ID }}
       tenant-id: ${{ secrets.AZURE_TENANT_ID }}
       subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
   ```

   (Replaces a `creds: ${{ secrets.AZURE_CREDENTIALS }}` line entirely.)

5. **Verify before merging to `main`.** Push the workflow-file change to a feature branch
   and dispatch the affected workflow(s) manually against it (`workflow_dispatch`, pointed
   at that branch if your setup allows dispatching a non-default ref). Confirm the Azure
   login step succeeds with the new inputs before merging — this is the step that must not
   be skipped if deploys on merge are automatic.
6. **Once confirmed working, remove the old stored-credential secret** and consider
   deleting the old client-secret credential on the app registration
   (`az ad app credential list` / `az ad app credential delete`) — the whole point of this
   migration is to stop having a long-lived stored secret at all.

## Related

- [`docs/methodology/c-sakerhet/hantering-av-hemligheter.md`](../methodology/c-sakerhet/hantering-av-hemligheter.md) —
  the methodology chapter this operationalises.
