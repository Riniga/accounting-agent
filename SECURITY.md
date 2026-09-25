# Security

## Reporting a vulnerability

If you believe you have found a security vulnerability in this project, **do not open a
public issue or pull request.** Report it directly to the project owner, Rickard
Nisses-Gagnér, through GitHub's private vulnerability reporting for this repository
(*Security → Report a vulnerability*).

## Coordinated vulnerability disclosure

There is no central security function behind this project; the project owner handles
disclosure. Reports are acknowledged, fixed, and disclosed once a fix is available.
Response times: Unknown – to be decided (tracked in the methodology gap register, chapter C3).

## `security.txt`

Not applicable — the project publishes no website or service where a `security.txt` could
be served.

## Secrets and configuration

- Secrets are never committed. `.env` is git-ignored; `.env.example` (repo root) lists the
  required keys with no values.
- Deployment secrets are stored as CI/CD platform secrets (see `README.md`).
- If a secret is ever exposed, it is treated as compromised: rotate it immediately, then
  clean history. See
  [`docs/development/secrets-rotation.md`](docs/development/secrets-rotation.md) and
  [`docs/methodology/c-sakerhet/hantering-av-hemligheter.md`](docs/methodology/c-sakerhet/hantering-av-hemligheter.md).
